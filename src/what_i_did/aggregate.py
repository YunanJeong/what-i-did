from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from what_i_did.models import PortfolioSummary, RepoAnalysis


def summarize(
    username: str,
    analyses: list[RepoAnalysis],
    overall_summary: str,
    model: str,
    lang: str,
) -> PortfolioSummary:
    # is_toy 판정은 LLM 이 한다. 튜토리얼·템플릿·실습 수준은 side 로 분리해
    # 포트폴리오 본문을 흐리지 않게 한다.
    main = [a for a in analyses if not a.is_toy]
    side = [a for a in analyses if a.is_toy]
    # 주 프로젝트는 스타 수 내림차순, 동점이면 이름 오름차순.
    main.sort(key=lambda a: (-a.stars, a.name.lower()))
    side.sort(key=lambda a: a.name.lower())

    counter: Counter[str] = Counter()
    for a in analyses:
        for tech in a.tech_stack:
            t = tech.strip()
            if t:
                counter[t] += 1
    tech_counts = sorted(
        counter.items(), key=lambda kv: (-kv[1], kv[0].lower())
    )

    return PortfolioSummary(
        username=username,
        generated_at=datetime.now(timezone.utc),
        model=model,
        lang=lang,
        overall_summary=overall_summary,
        main_projects=main,
        side_projects=side,
        tech_counts=tech_counts,
    )
