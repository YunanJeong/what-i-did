from __future__ import annotations

from what_i_did import prompts
from what_i_did.models import PortfolioSummary, RepoAnalysis


def _render_repo_card(a: RepoAnalysis, p) -> str:
    lines = [f"### [{a.name}]({a.html_url})"]
    meta_bits = []
    if a.primary_language:
        meta_bits.append(a.primary_language)
    if a.stars:
        meta_bits.append(f"{p.LABEL_STARS}: {a.stars}")
    if meta_bits:
        lines.append(f"_{' · '.join(meta_bits)}_")
    if a.description:
        lines.append(f"> {a.description}")
    lines.append("")

    if a.purpose:
        lines.append(f"**{p.LABEL_PURPOSE}:** {a.purpose}")
        lines.append("")

    if a.key_features:
        lines.append(f"**{p.LABEL_FEATURES}:**")
        lines.extend(f"- {f}" for f in a.key_features)
        lines.append("")

    if a.tech_stack:
        lines.append(f"**{p.LABEL_TECH}:** {', '.join(a.tech_stack)}")
        lines.append("")

    if a.highlights:
        lines.append(f"**{p.LABEL_HIGHLIGHTS}:**")
        lines.extend(f"- {h}" for h in a.highlights)
        lines.append("")

    if a.user_contribution_notes:
        lines.append(f"**{p.LABEL_CONTRIB}:** {a.user_contribution_notes}")
        lines.append("")

    return "\n".join(lines)


def render(portfolio: PortfolioSummary) -> str:
    p = prompts.get(portfolio.lang)
    out: list[str] = []
    out.append(f"# {p.DOC_TITLE.format(username=portfolio.username)}")
    out.append("")

    if portfolio.overall_summary:
        out.append(f"## {p.SEC_SUMMARY}")
        out.append("")
        out.append(portfolio.overall_summary)
        out.append("")

    if portfolio.main_projects:
        out.append(f"## {p.SEC_MAIN}")
        out.append("")
        for a in portfolio.main_projects:
            out.append(_render_repo_card(a, p))

    if portfolio.side_projects:
        out.append(f"## {p.SEC_SIDE}")
        out.append("")
        for a in portfolio.side_projects:
            out.append(_render_repo_card(a, p))

    if portfolio.tech_counts:
        out.append(f"## {p.SEC_STACK}")
        out.append("")
        for tech, count in portfolio.tech_counts:
            out.append(f"- {tech} ({count})")
        out.append("")

    out.append("---")
    out.append(
        f"_{p.LABEL_GENERATED}: {portfolio.generated_at.strftime('%Y-%m-%d %H:%M UTC')} · "
        f"{p.LABEL_MODEL}: {portfolio.model}_"
    )
    return "\n".join(out) + "\n"
