from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

import requests

from app.core.settings import Settings


@dataclass(frozen=True)
class PullRequestResult:
    mode: str
    branch: str
    url: str | None
    detail: str


class GitHubPublisher:
    """Creates a draft PR through the GitHub Git Database API when configured."""

    api_base = "https://api.github.com"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def publish_draft(
        self, branch: str, title: str, body: str, app_source: str, test_source: str
    ) -> PullRequestResult:
        if not self.settings.github_token or not self.settings.github_repository:
            return PullRequestResult(
                mode="simulated",
                branch=branch,
                url=None,
                detail="GitHub credentials are not configured; no remote repository was changed.",
            )
        try:
            return self._publish(branch, title, body, app_source, test_source)
        except (requests.RequestException, KeyError, TypeError, ValueError) as error:
            return PullRequestResult(
                mode="failed",
                branch=branch,
                url=None,
                detail=f"GitHub publishing failed: {error}",
            )

    def _publish(
        self, branch: str, title: str, body: str, app_source: str, test_source: str
    ) -> PullRequestResult:
        repository = self.settings.github_repository
        base = self.settings.github_base_branch
        base_ref = self._base_branch_ref(repository, base)
        base_sha = base_ref["object"]["sha"]
        base_commit = self._request("GET", f"/repos/{repository}/git/commits/{base_sha}")
        app_blob = self._request(
            "POST",
            f"/repos/{repository}/git/blobs",
            {"content": base64.b64encode(app_source.encode()).decode(), "encoding": "base64"},
        )
        test_blob = self._request(
            "POST",
            f"/repos/{repository}/git/blobs",
            {"content": base64.b64encode(test_source.encode()).decode(), "encoding": "base64"},
        )
        tree = self._request(
            "POST",
            f"/repos/{repository}/git/trees",
            {
                "base_tree": base_commit["tree"]["sha"],
                "tree": [
                    {"path": "app.py", "mode": "100644", "type": "blob", "sha": app_blob["sha"]},
                    {
                        "path": "tests/test_app.py",
                        "mode": "100644",
                        "type": "blob",
                        "sha": test_blob["sha"],
                    },
                ],
            },
        )
        commit = self._request(
            "POST",
            f"/repos/{repository}/git/commits",
            {
                "message": "Add premium subscription validation endpoint",
                "tree": tree["sha"],
                "parents": [base_sha],
            },
        )
        self._request(
            "POST",
            f"/repos/{repository}/git/refs",
            {"ref": f"refs/heads/{branch}", "sha": commit["sha"]},
        )
        pull_request = self._request(
            "POST",
            f"/repos/{repository}/pulls",
            {"title": title, "head": branch, "base": base, "body": body, "draft": True},
        )
        return PullRequestResult(
            mode="live", branch=branch, url=pull_request["html_url"], detail="Draft PR created."
        )

    def _base_branch_ref(self, repository: str, base: str) -> dict[str, Any]:
        try:
            return self._request("GET", f"/repos/{repository}/git/ref/heads/{base}")
        except requests.HTTPError as error:
            if error.response is None or error.response.status_code != 409:
                raise
            # A newly created GitHub repository has no commit or branch ref yet.
            # Create a harmless README to establish the configured base branch.
            self._request(
                "PUT",
                f"/repos/{repository}/contents/README.md",
                {
                    "message": "Initialize Relay demo repository",
                    "content": base64.b64encode(
                        b"# Relay demo repository\n\nDisposable target for ContextBridge Enterprise draft PRs.\n"
                    ).decode(),
                    "branch": base,
                },
            )
            return self._request("GET", f"/repos/{repository}/git/ref/heads/{base}")

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        response = requests.request(
            method,
            self.api_base + path,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.settings.github_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json=payload,
            timeout=(3, 20),
        )
        response.raise_for_status()
        return response.json()
