from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from what_i_did.models import CachedAnalysis, RepoAnalysis


def _user_dir(cache_dir: Path, username: str) -> Path:
    return cache_dir / username


def path_for(cache_dir: Path, username: str, repo_name: str) -> Path:
    return _user_dir(cache_dir, username) / f"{repo_name}.json"


def load(cache_dir: Path, username: str, repo_name: str) -> RepoAnalysis | None:
    # 캐시 파일이 존재하면 무조건 재사용한다. SHA·mtime·TTL 은 쓰지 않는다.
    # repo 가 바뀌어도 자동 재분석하지 않는 대신, 사용자가 `--refresh` 를 쓰면
    # 호출측이 이 함수를 건너뛴다. cron 주기 실행 시 비용을 0에 가깝게 만든다.
    p = path_for(cache_dir, username, repo_name)
    if not p.exists():
        return None
    try:
        cached = CachedAnalysis.model_validate_json(p.read_text(encoding="utf-8"))
    except Exception:
        # 파일이 손상됐거나 스키마가 변경돼 파싱 실패한 경우.
        # 치명적이지 않으므로 "캐시 없음"으로 간주하고 재분석을 유도한다.
        return None
    return cached.analysis


def save(
    cache_dir: Path,
    username: str,
    repo_name: str,
    analysis: RepoAnalysis,
    model: str,
) -> None:
    p = path_for(cache_dir, username, repo_name)
    p.parent.mkdir(parents=True, exist_ok=True)
    cached = CachedAnalysis(
        saved_at=datetime.now(timezone.utc),
        model=model,
        analysis=analysis,
    )
    p.write_text(cached.model_dump_json(indent=2), encoding="utf-8")
