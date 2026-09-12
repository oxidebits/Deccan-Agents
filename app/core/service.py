from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from app.core.router import OpenRouterManager
from app.core.runs import RunStore
from app.core.settings import Settings
from app.tools.codex_runner import CodexLocalRunner
from app.tools.github import GitHubPublisher


class ContextBridgeService:
    def __init__(self, settings: Settings, store: RunStore) -> None:
        self.settings = settings
        self.store = store
        self.models = OpenRouterManager(settings)
        self.runner = CodexLocalRunner(settings.mock_repo_path, settings.demo_premium_token)
        self.github = GitHubPublisher(settings)
        self._execution_lock = threading.Lock()

    def start(self, transcript: str) -> str:
        return self.store.create(transcript).id

    def execute(self, run_id: str) -> None:
        # A single disposable local repository is shared by demo runs.
        # Serialize it so simultaneous Teams mentions cannot race on git state.
        with self._execution_lock:
            self._execute_serially(run_id)

    def _execute_serially(self, run_id: str) -> None:
        self.store.update(run_id, status="running")
        try:
            transcript = self.store.get(run_id)["transcript"]  # type: ignore[index]
            specification = self.models.execute_triage(transcript)
            review = self.models.execute_review(specification.value)
            patch_path = self.runner.apply_fixed_premium_patch()
            validation = self.runner.execute_test_suite()
            result: dict[str, Any] = {
                "jira": self._simulated_jira(specification.value),
                "specification": specification.value,
                "triage_source": specification.source,
                "review": review.value,
                "review_source": review.source,
                "patch_path": str(patch_path),
                "tests": {"passed": validation.passed, "output": validation.output[-4000:]},
            }
            if not validation.passed:
                self.store.update(run_id, status="failed", result=result, error="Local validation failed.")
                return
            branch = self.runner.create_run_branch(run_id)
            pr = self.github.publish_draft(
                branch=branch,
                title=specification.value["title"],
                body=self._pull_request_body(specification.value, review.value),
                app_source=self.runner.patched_app_source(),
                test_source=self.runner.patched_test_source(),
            )
            result["github"] = {
                "mode": pr.mode,
                "branch": pr.branch,
                "url": pr.url,
                "detail": pr.detail,
            }
            fallback_used = "fallback" in specification.source or "fallback" in review.source
            self.store.update(run_id, status="degraded" if fallback_used or pr.mode == "failed" else "succeeded", result=result)
        except Exception as error:  # Keep a webhook-triggered background error observable.
            self.store.update(run_id, status="failed", error=f"{type(error).__name__}: {error}")

    @staticmethod
    def _simulated_jira(specification: dict[str, Any]) -> dict[str, Any]:
        return {
            "mode": "simulated",
            "key": "PROJ-901",
            "summary": specification["title"],
            "priority": specification.get("priority", "P0"),
            "description": specification["description"],
        }

    @staticmethod
    def _pull_request_body(specification: dict[str, Any], review: dict[str, Any]) -> str:
        criteria = "\n".join(f"- {item}" for item in specification["acceptance_criteria"])
        checks = "\n".join(f"- {item}" for item in review.get("checks", []))
        return f"""## ContextBridge generated demo patch

{specification["description"]}

### Acceptance criteria
{criteria}

### Peer review
{checks}

This is a draft PR created by the ContextBridge Enterprise prototype.
"""


def load_demo_transcript(project_root: Path) -> str:
    payload = json.loads((project_root / "data" / "demo_transcript.json").read_text(encoding="utf-8"))
    return payload["transcript"]
