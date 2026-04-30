from __future__ import annotations

import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import anthropic
import typer
from rich.console import Console

from what_i_did import aggregate, analyze, cache, collect
from what_i_did.models import RepoAnalysis
from what_i_did.render import docx as docx_render
from what_i_did.render import markdown as md_render

console = Console()


def _make_client(provider: str):
    # Provider 별로 다른 클라이언트 클래스가 필요하다. 둘 다 Anthropic SDK 의
    # 동일한 messages.create 인터페이스를 제공하지만 인증 경로가 다르다:
    # - anthropic: ANTHROPIC_API_KEY (SDK 가 env 에서 읽음)
    # - bedrock:  AWS 자격 증명 (AWS_BEARER_TOKEN_BEDROCK 또는 표준 boto3 체인),
    #             AWS_REGION. 모두 SDK/boto3 가 env 에서 읽음.
    # 코드에서 env 값을 직접 다루지 않는다 — 설계상 제약.
    if provider == "anthropic":
        return anthropic.Anthropic()
    if provider == "bedrock":
        return anthropic.AnthropicBedrock()
    raise typer.BadParameter(f"unknown provider: {provider}")


def _default_model(provider: str) -> str:
    # Bedrock 의 모델 id 는 `anthropic.claude-...-v1:0` 형태이며 리전/프로비저닝에
    # 따라 정확한 문자열이 달라진다. 기본값을 못 박으면 다수 사용자가 즉시 깨지므로
    # Bedrock 은 --model 명시를 강제한다.
    if provider == "anthropic":
        return "claude-sonnet-4-6"
    return ""  # bedrock: 사용자가 --model 을 반드시 주어야 함


def _default_output(username: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d")
    return Path(f"what-i-did-{username}-{stamp}")


def _default_cache_dir() -> Path:
    return Path.home() / ".cache" / "what-i-did"


def generate(
    username: str = typer.Argument(..., help="GitHub username to analyze."),
    exclude: list[str] = typer.Option(
        [], "--exclude", "-e",
        help="Glob pattern matched against repo name. Repeatable.",
    ),
    provider: str = typer.Option(
        "anthropic", "--provider", "-p",
        help="LLM provider: 'anthropic' (uses ANTHROPIC_API_KEY) "
             "or 'bedrock' (uses AWS credentials / AWS_REGION).",
        case_sensitive=False,
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m",
        help="Model id. Defaults to claude-sonnet-4-6 for anthropic provider; "
             "required for bedrock (e.g. 'anthropic.claude-sonnet-4-5-20250929-v1:0').",
    ),
    lang: str = typer.Option(
        "ko", "--lang", "-l",
        help="Output language: ko or en.",
        case_sensitive=False,
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="Output path without extension. Defaults to ./what-i-did-<user>-<date>.",
    ),
    refresh: bool = typer.Option(
        False, "--refresh",
        help="Ignore existing cache and re-analyze every repo.",
    ),
    max_repos: Optional[int] = typer.Option(
        None, "--max-repos",
        help="Debug cap on number of repos to analyze.",
    ),
    cache_dir: Optional[Path] = typer.Option(
        None, "--cache-dir",
        help="Cache directory. Defaults to ~/.cache/what-i-did.",
    ),
    include_forks: bool = typer.Option(
        False, "--include-forks",
        help="Include forked repositories.",
    ),
):
    """Analyze a GitHub account and write portfolio documents (Markdown + Word)."""
    lang_l = lang.lower()
    if lang_l not in ("ko", "en"):
        raise typer.BadParameter("--lang must be 'ko' or 'en'")
    provider_l = provider.lower()
    if provider_l not in ("anthropic", "bedrock"):
        raise typer.BadParameter("--provider must be 'anthropic' or 'bedrock'")
    if not model:
        model = _default_model(provider_l)
    if not model:
        raise typer.BadParameter(
            "--model is required when --provider=bedrock "
            "(e.g. 'anthropic.claude-sonnet-4-5-20250929-v1:0')"
        )
    cache_dir = cache_dir or _default_cache_dir()
    output = output or _default_output(username)

    console.print(
        f"[bold]what-i-did[/bold] · user=[cyan]{username}[/cyan] · "
        f"provider=[cyan]{provider_l}[/cyan] · "
        f"model=[cyan]{model}[/cyan] · lang=[cyan]{lang_l}[/cyan]"
    )

    console.print("Fetching repository list…")
    repos = collect.list_repos(username, include_forks=include_forks)
    repos = collect.filter_excluded(repos, exclude)
    if max_repos is not None:
        repos = repos[:max_repos]
    if not repos:
        console.print("[yellow]No repositories to analyze.[/yellow]")
        raise typer.Exit(code=1)
    console.print(f"  → {len(repos)} repo(s) selected")

    # 인증 값(ANTHROPIC_API_KEY / AWS 크리덴셜)은 SDK·boto3 가 env 에서 직접
    # 읽는다. 여기서 env 를 조회하거나 값을 다루지 않는다 — 설계상 제약.
    client = _make_client(provider_l)

    analyses: list[RepoAnalysis] = []
    # 클론 대상은 분석이 끝나면 의미 없으므로 임시 디렉토리에 두고 전체 삭제한다.
    tmp_root = Path(tempfile.mkdtemp(prefix="what-i-did-"))
    try:
        for i, meta in enumerate(repos, 1):
            label = f"[{i}/{len(repos)}] {meta.name}"

            if not refresh:
                cached = cache.load(cache_dir, username, meta.name)
                if cached is not None:
                    console.print(f"{label} [dim](cached)[/dim]")
                    analyses.append(cached)
                    continue

            console.print(f"{label} cloning…")
            repo_path = collect.clone_repo(meta, tmp_root)
            if repo_path is None:
                console.print("  [yellow]clone failed, skipping[/yellow]")
                continue

            selected, truncated = collect.select_files(repo_path)
            if not selected:
                console.print("  [yellow]no analyzable files, skipping[/yellow]")
                continue

            console.print(f"  analyzing {len(selected)} file(s)…")
            try:
                analysis = analyze.analyze_repo(
                    client, meta, selected, truncated, model, lang_l
                )
            except Exception as exc:
                console.print(f"  [red]analysis failed: {exc}[/red]")
                continue

            cache.save(cache_dir, username, meta.name, analysis, model)
            analyses.append(analysis)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    if not analyses:
        console.print("[red]No successful analyses; aborting.[/red]")
        raise typer.Exit(code=2)

    console.print("Writing overall summary…")
    try:
        overall = analyze.summarize_portfolio(
            client, username, analyses, model, lang_l
        )
    except Exception as exc:
        console.print(f"  [yellow]summary failed: {exc}[/yellow]")
        overall = ""

    portfolio = aggregate.summarize(username, analyses, overall, model, lang_l)

    md_path = output.with_suffix(".md")
    docx_path = output.with_suffix(".docx")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md_render.render(portfolio), encoding="utf-8")
    docx_render.render(portfolio, docx_path)
    console.print(f"[green]✓[/green] {md_path}")
    console.print(f"[green]✓[/green] {docx_path}")


def app() -> None:
    typer.run(generate)


if __name__ == "__main__":
    app()
