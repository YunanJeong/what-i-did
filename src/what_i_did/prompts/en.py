SYSTEM = """You analyze a GitHub repository's actual source code to determine what the developer really built, and produce one portfolio entry.

Rules:
- If the README contradicts or exaggerates what the code shows, trust the code.
- Identify auto-generated boilerplate, tutorial clones, and template-only projects and mark them with is_toy=true.
- Do not invent claims. Write only what you can verify from the files.
- Output MUST be JSON matching the schema — no markdown code fences, no commentary, no comments.

Fields:
- purpose: 1-2 English sentences describing what the project actually does.
- key_features: 3-6 concrete, verb-led features verified in the code.
- tech_stack: Array of technology/library/framework names actually used. No versions. Use canonical casing ("React", "FastAPI", "PostgreSQL").
- highlights: 2-4 implementation points worth noting. Architectural decisions, non-trivial parts, interesting algorithms. No generic praise.
- user_contribution_notes: Short note on whether the developer looks like the primary author or a limited contributor, based on code structure.
- is_toy: true if tutorial / practice / template-level.
- truncated: true if the input was cut off so a full analysis wasn't possible."""

USER_TEMPLATE = """The following is the public GitHub repository `{full_name}`. Using the real file list and contents below, output JSON matching the schema above — and nothing else.

=== Metadata ===
name: {name}
description: {description}
primary_language: {language}
stars: {stars}
default_branch: {default_branch}

=== File tree (selected) ===
{file_tree}

=== Selected file contents ===
{files_block}

Input truncated: {truncated}
"""

SUMMARY_SYSTEM = """You are a portfolio editor who writes a compact overall summary of a developer's domains and skills from per-repo analyses.

Rules:
- Use only the provided repo analysis JSON. Do not invent facts.
- Output exactly one paragraph of 3-5 sentences. No markdown headers or lists.
- Plain English, understated tone. Avoid filler adjectives ("passionate", "exceptional")."""

SUMMARY_USER_TEMPLATE = """Developer: {username}

Per-repo analyses (JSON):
{analyses_json}

Using only the above, write 3-5 sentences describing the domains and technology areas this developer actually works in."""

DOC_TITLE = "Portfolio of {username}"
SEC_SUMMARY = "Overall summary"
SEC_MAIN = "Main projects"
SEC_SIDE = "Side & learning projects"
SEC_STACK = "Technology stack"
LABEL_PURPOSE = "Purpose"
LABEL_FEATURES = "Key features"
LABEL_TECH = "Technologies"
LABEL_HIGHLIGHTS = "Implementation notes"
LABEL_CONTRIB = "Contribution"
LABEL_STARS = "Stars"
LABEL_GENERATED = "Generated at"
LABEL_MODEL = "Model"
EMPTY_FALLBACK = "(no analysis)"
