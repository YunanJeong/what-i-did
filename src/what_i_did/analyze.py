from __future__ import annotations

import json

import anthropic

from what_i_did import prompts
from what_i_did.collect import build_file_tree, build_files_block
from what_i_did.models import RepoAnalysis, RepoMeta, SelectedFile


# Anthropic API 의 output_config.format 에 그대로 주입하는 JSON Schema.
# additionalProperties=false + required 전 필드로 지정해 LLM 응답 형식을 강제.
# 필드 이름이 바뀌면 models.RepoAnalysis / prompts.*.SYSTEM 도 함께 바꿔야 한다.
REPO_ANALYSIS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "purpose": {"type": "string"},
        "key_features": {"type": "array", "items": {"type": "string"}},
        "tech_stack": {"type": "array", "items": {"type": "string"}},
        "highlights": {"type": "array", "items": {"type": "string"}},
        "user_contribution_notes": {"type": "string"},
        "is_toy": {"type": "boolean"},
        "truncated": {"type": "boolean"},
    },
    "required": [
        "purpose",
        "key_features",
        "tech_stack",
        "highlights",
        "user_contribution_notes",
        "is_toy",
        "truncated",
    ],
}


def _extract_text(response) -> str:
    for block in response.content:
        if block.type == "text":
            return block.text
    return ""


def analyze_repo(
    client: anthropic.Anthropic,
    meta: RepoMeta,
    selected: list[SelectedFile],
    truncated: bool,
    model: str,
    lang: str,
) -> RepoAnalysis:
    p = prompts.get(lang)
    user_text = p.USER_TEMPLATE.format(
        full_name=meta.full_name,
        name=meta.name,
        description=meta.description or "(none)",
        language=meta.language or "(unknown)",
        stars=meta.stargazers_count,
        default_branch=meta.default_branch,
        file_tree=build_file_tree(selected) or "(no files selected)",
        files_block=build_files_block(selected) or "(empty)",
        truncated=str(truncated).lower(),
    )

    # prompt caching: 시스템 프롬프트는 repo 간 불변이므로 cache_control 을 걸어
    # 두 번째 repo 부터는 시스템 블록이 캐시 히트된다.
    # user 메시지는 repo 마다 다르므로 캐시 대상에서 자연스럽게 제외된다.
    #
    # output_config.format: JSON Schema 로 응답 형식 강제. prefill 이 4.6 에서
    # 400 을 내므로 이 방식이 정식 대안이다.
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": p.SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_text}],
        output_config={
            "format": {"type": "json_schema", "schema": REPO_ANALYSIS_SCHEMA}
        },
    )

    text = _extract_text(response)
    data = json.loads(text)

    # LLM 은 input 이 잘렸다는 사실을 항상 눈치채지는 못하므로,
    # 호출측에서 truncated 를 감지했으면 모델 판정과 OR 로 합친다.
    return RepoAnalysis(
        name=meta.name,
        html_url=meta.html_url,
        description=meta.description,
        primary_language=meta.language,
        stars=meta.stargazers_count,
        purpose=data.get("purpose", ""),
        key_features=data.get("key_features", []),
        tech_stack=data.get("tech_stack", []),
        highlights=data.get("highlights", []),
        user_contribution_notes=data.get("user_contribution_notes", ""),
        is_toy=bool(data.get("is_toy", False)),
        truncated=bool(data.get("truncated", truncated)) or truncated,
    )


def summarize_portfolio(
    client: anthropic.Anthropic,
    username: str,
    analyses: list[RepoAnalysis],
    model: str,
    lang: str,
) -> str:
    if not analyses:
        return ""
    p = prompts.get(lang)
    compact = [
        {
            "name": a.name,
            "description": a.description,
            "purpose": a.purpose,
            "tech_stack": a.tech_stack,
            "key_features": a.key_features,
            "is_toy": a.is_toy,
        }
        for a in analyses
    ]
    response = client.messages.create(
        model=model,
        max_tokens=800,
        system=p.SUMMARY_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": p.SUMMARY_USER_TEMPLATE.format(
                    username=username,
                    analyses_json=json.dumps(compact, ensure_ascii=False, indent=2),
                ),
            }
        ],
    )
    return _extract_text(response).strip()
