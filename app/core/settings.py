from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    """Load a minimal .env file without adding a runtime dependency."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _as_bool(value: str, default: bool = False) -> bool:
    if not value:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    project_root: Path
    run_mode: str
    teams_hmac_secret: str | None
    allow_unsigned_webhooks: bool
    public_base_url: str | None
    openrouter_api_key: str | None
    triage_model: str
    review_model: str
    demo_premium_token: str
    github_token: str | None
    github_repository: str | None
    github_base_branch: str
    slack_signing_secret: str | None

    @property
    def mock_repo_path(self) -> Path:
        return self.project_root / "mock_repo"

    @classmethod
    def from_environment(cls) -> "Settings":
        project_root = Path(__file__).resolve().parents[2]
        _load_dotenv(project_root / ".env")
        return cls(
            project_root=project_root,
            run_mode=os.getenv("RUN_MODE", "MOCK").upper(),
            teams_hmac_secret=os.getenv("TEAMS_HMAC_SECRET") or None,
            allow_unsigned_webhooks=_as_bool(os.getenv("ALLOW_UNSIGNED_WEBHOOKS", "")),
            public_base_url=os.getenv("PUBLIC_BASE_URL", "").rstrip("/") or None,
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY") or None,
            triage_model=os.getenv(
                "OPENROUTER_TRIAGE_MODEL", "meta-llama/llama-3.3-70b-instruct"
            ),
            review_model=os.getenv("OPENROUTER_REVIEW_MODEL", "deepseek/deepseek-r1"),
            demo_premium_token=os.getenv("DEMO_PREMIUM_TOKEN", "demo-premium-token"),
            github_token=os.getenv("GITHUB_TOKEN") or None,
            github_repository=os.getenv("GITHUB_REPOSITORY") or None,
            github_base_branch=os.getenv("GITHUB_BASE_BRANCH", "main"),
            slack_signing_secret=os.getenv("SLACK_SIGNING_SECRET") or None,
        )
