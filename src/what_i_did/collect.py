from __future__ import annotations

import fnmatch
import subprocess
from pathlib import Path

import httpx
import pathspec

from what_i_did.models import RepoMeta, SelectedFile

GITHUB_API = "https://api.github.com"

# 소스로 인정할 확장자. 여기 없으면 "일반 소스 파일"로 포함되지 않고,
# PRIORITY_FILES / ENTRYPOINT_STEMS 에 걸리지 않는 한 선별 대상에서 빠진다.
SOURCE_EXTENSIONS = {
    ".py", ".pyi",
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".go",
    ".rs",
    ".java", ".kt", ".kts",
    ".rb",
    ".php",
    ".c", ".h", ".cc", ".cpp", ".hpp", ".hh", ".cxx",
    ".cs",
    ".swift",
    ".scala",
    ".sh", ".bash",
    ".lua",
    ".sql",
    ".vue", ".svelte",
    ".html", ".css", ".scss",
    ".toml", ".yaml", ".yml",
}

# 이 이름의 파일은 "이 프로젝트가 뭔지" 판단에 결정적이므로 최우선으로 집어넣는다.
# README + manifest 만으로도 용도/스택 추정이 상당히 된다.
PRIORITY_FILES = {
    "readme", "readme.md", "readme.rst", "readme.txt",
    "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
    "package.json", "tsconfig.json",
    "cargo.toml", "go.mod", "go.sum",
    "gemfile", "composer.json",
    "dockerfile", "makefile",
    "pom.xml", "build.gradle", "build.gradle.kts",
}

ENTRYPOINT_STEMS = {"main", "index", "app", "server", "cli", "__main__"}

EXCLUDE_DIRS = {
    ".git", ".github", ".hg", ".svn",
    "node_modules", "dist", "build", "out", "target",
    "__pycache__", ".venv", "venv", "env",
    "vendor", "third_party",
    ".next", ".nuxt", ".cache", ".tox", ".mypy_cache", ".pytest_cache",
    ".idea", ".vscode", ".gradle",
    "coverage", "htmlcov",
}

EXCLUDE_FILE_PATTERNS = [
    "*.lock", "*.min.js", "*.min.css", "*.map",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "uv.lock",
    "poetry.lock", "Cargo.lock", "Gemfile.lock", "composer.lock",
    "*.ipynb",
]

# 1MB 초과 단일 파일은 건너뛴다. 자동 생성물·대용량 데이터가 대부분이고
# 그 정도 크기면 한 파일이 char budget 을 통째로 먹는다.
MAX_FILE_BYTES = 1_000_000

# repo 하나당 LLM 에 보낼 총 문자 수 한도. Sonnet 4.6 컨텍스트(1M)는 충분하지만
# 비용·응답 지연을 감안해 보수적으로 잡음. 초과분은 잘리고 truncated=True 로 표시.
CHAR_BUDGET_DEFAULT = 150_000


def list_repos(username: str, include_forks: bool = False) -> list[RepoMeta]:
    # 비인증 호출 (시간당 60 req 제한). repo 목록 한 페이지 = 100개이므로
    # 대부분 계정은 1~2회 호출로 끝난다. 토큰·인증 관련 로직은 의도적으로 없다.
    repos: list[RepoMeta] = []
    page = 1
    with httpx.Client(
        timeout=30.0,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "what-i-did/0.1",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    ) as client:
        while True:
            r = client.get(
                f"{GITHUB_API}/users/{username}/repos",
                params={
                    "per_page": 100,
                    "page": page,
                    "type": "owner",
                    "sort": "pushed",
                    "direction": "desc",
                },
            )
            if r.status_code == 404:
                raise RuntimeError(f"GitHub user not found: {username}")
            if r.status_code == 403:
                raise RuntimeError(
                    "GitHub API rate limit hit (unauthenticated: 60 req/h). "
                    "Retry later."
                )
            r.raise_for_status()
            batch = r.json()
            if not batch:
                break
            for item in batch:
                if item.get("fork") and not include_forks:
                    continue
                repos.append(
                    RepoMeta(
                        name=item["name"],
                        full_name=item["full_name"],
                        default_branch=item.get("default_branch") or "main",
                        clone_url=item["clone_url"],
                        html_url=item["html_url"],
                        description=item.get("description"),
                        language=item.get("language"),
                        stargazers_count=item.get("stargazers_count", 0),
                        fork=item.get("fork", False),
                        archived=item.get("archived", False),
                        pushed_at=item.get("pushed_at"),
                    )
                )
            if len(batch) < 100:
                break
            page += 1
    return repos


def filter_excluded(
    repos: list[RepoMeta], exclude_globs: list[str]
) -> list[RepoMeta]:
    if not exclude_globs:
        return repos
    kept = []
    for repo in repos:
        if any(fnmatch.fnmatch(repo.name, pat) for pat in exclude_globs):
            continue
        kept.append(repo)
    return kept


def filter_included(
    repos: list[RepoMeta], include_globs: list[str]
) -> list[RepoMeta]:
    # include_globs 가 비면 전부 통과 (기본 동작 유지). 비어 있지 않으면
    # 그 중 하나라도 매칭되는 repo 만 남긴다. exclude 와 짝을 이루며,
    # 호출 순서는 include → exclude.
    if not include_globs:
        return repos
    return [
        r for r in repos
        if any(fnmatch.fnmatch(r.name, pat) for pat in include_globs)
    ]


def clone_repo(meta: RepoMeta, workdir: Path) -> Path | None:
    target = workdir / meta.name
    if target.exists():
        return target
    # depth=50 / single-branch / no-tags: 최신 코드와 약간의 history 만 필요.
    # 전체 클론은 용량·시간 낭비이며 분석 품질에 차이가 없다.
    cmd = [
        "git", "clone",
        "--depth=50",
        "--single-branch",
        "--no-tags",
        "--quiet",
        meta.clone_url,
        str(target),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    return target


def _load_gitignore(repo_path: Path) -> pathspec.PathSpec | None:
    gi = repo_path / ".gitignore"
    if not gi.exists():
        return None
    try:
        patterns = gi.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)


def _looks_binary(sample: bytes) -> bool:
    # NULL 바이트가 있으면 확정 바이너리. 없더라도 비출력 바이트 비율이 높으면
    # (bin/이미지/폰트 등) 분석 대상에서 뺀다. 첫 8KB 샘플만 본다.
    if b"\x00" in sample:
        return True
    if not sample:
        return False
    nontext = sum(1 for b in sample if b < 9 or (13 < b < 32))
    return nontext / len(sample) > 0.30


def _file_priority(rel: str, name_lower: str, stem_lower: str) -> int:
    # 낮을수록 먼저 선정. README/manifest → entrypoint → 얕은 소스 → 깊은 소스 순.
    # 예산이 부족할 때 중요한 파일이 먼저 들어가도록 하기 위함.
    if name_lower in PRIORITY_FILES or name_lower.startswith("readme"):
        return 0
    if stem_lower in ENTRYPOINT_STEMS:
        return 1
    depth = rel.count("/")
    return 2 + depth


def _iter_candidate_files(repo_path: Path):
    ignore = _load_gitignore(repo_path)
    for p in repo_path.rglob("*"):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(repo_path).as_posix()
        except ValueError:
            continue
        parts = rel.split("/")
        if any(part in EXCLUDE_DIRS for part in parts):
            continue
        name_lower = p.name.lower()
        if any(fnmatch.fnmatch(name_lower, pat.lower()) for pat in EXCLUDE_FILE_PATTERNS):
            continue
        if ignore and ignore.match_file(rel):
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        if size > MAX_FILE_BYTES:
            continue
        stem_lower = p.stem.lower()
        ext = p.suffix.lower()
        is_priority = (
            name_lower in PRIORITY_FILES
            or name_lower.startswith("readme")
            or stem_lower in ENTRYPOINT_STEMS
            or ext in SOURCE_EXTENSIONS
        )
        if not is_priority:
            continue
        yield p, rel, size, name_lower, stem_lower


def select_files(
    repo_path: Path, char_budget: int = CHAR_BUDGET_DEFAULT
) -> tuple[list[SelectedFile], bool]:
    candidates = []
    for p, rel, size, name_lower, stem_lower in _iter_candidate_files(repo_path):
        prio = _file_priority(rel, name_lower, stem_lower)
        candidates.append((prio, size, rel, p))

    candidates.sort(key=lambda x: (x[0], x[1], x[2]))

    selected: list[SelectedFile] = []
    used = 0
    truncated = False
    for _prio, _size, rel, p in candidates:
        try:
            with p.open("rb") as f:
                sample = f.read(8192)
            if _looks_binary(sample):
                continue
            data = p.read_bytes()
            text = data.decode("utf-8", errors="replace")
        except OSError:
            continue
        remaining = char_budget - used
        if remaining <= 0:
            truncated = True
            break
        if len(text) > remaining:
            text = text[:remaining] + "\n...[truncated]"
            truncated = True
        selected.append(SelectedFile(path=rel, size_bytes=p.stat().st_size, content=text))
        used += len(text)
        if used >= char_budget:
            truncated = True
            break
    return selected, truncated


def build_file_tree(selected: list[SelectedFile]) -> str:
    return "\n".join(f"- {s.path} ({s.size_bytes}B)" for s in selected)


def build_files_block(selected: list[SelectedFile]) -> str:
    parts = []
    for s in selected:
        parts.append(f"----- FILE: {s.path} -----\n{s.content}")
    return "\n\n".join(parts)
