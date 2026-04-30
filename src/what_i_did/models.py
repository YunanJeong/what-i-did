from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field


class RepoMeta(BaseModel):
    name: str
    full_name: str
    default_branch: str
    clone_url: str
    html_url: str
    description: str | None = None
    language: str | None = None
    stargazers_count: int = 0
    fork: bool = False
    archived: bool = False
    pushed_at: str | None = None


class SelectedFile(BaseModel):
    path: str
    size_bytes: int
    content: str


class RepoAnalysis(BaseModel):
    name: str
    html_url: str
    description: str | None = None
    primary_language: str | None = None
    stars: int = 0
    purpose: str = ""
    key_features: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list)
    user_contribution_notes: str = ""
    is_toy: bool = False
    truncated: bool = False


class CachedAnalysis(BaseModel):
    saved_at: datetime
    model: str
    analysis: RepoAnalysis


class PortfolioSummary(BaseModel):
    username: str
    generated_at: datetime
    model: str
    lang: str
    overall_summary: str = ""
    main_projects: list[RepoAnalysis] = Field(default_factory=list)
    side_projects: list[RepoAnalysis] = Field(default_factory=list)
    tech_counts: list[tuple[str, int]] = Field(default_factory=list)


class WorkPaths(BaseModel):
    clone_root: Path
    cache_dir: Path
