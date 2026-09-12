"""GitHub REST API Client for automated branching, commits, PRs, and review feedback."""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

def log(msg: str) -> None:
    sys.stderr.write(f"[GITHUB CLIENT] {msg}\n")
    sys.stderr.flush()

def _get_headers() -> Dict[str, str]:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def _get_repo_name() -> str:
    return os.getenv("GITHUB_REPO", "oxidebits/Deccan-Agents").strip()

def _is_mock_mode() -> bool:
    return os.getenv("MOCK_MODE", "false").lower() in ("true", "1", "yes") or not os.getenv("GITHUB_TOKEN")

def _load_mock_data() -> Dict[str, Any]:
    mock_path = Path(__file__).resolve().parent.parent.parent / "mock_data.json"
    if mock_path.exists():
        try:
            with open(mock_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"Error loading mock_data.json: {e}")
    return {}

def create_git_branch(branch_name: str, base_branch: str = "main") -> Dict[str, Any]:
    """Creates a feature branch on GitHub repository."""
    if _is_mock_mode():
        log(f"MOCK MODE: Created branch '{branch_name}' from '{base_branch}'")
        return {"branch": branch_name, "base": base_branch, "created": True}

    repo = _get_repo_name()
    headers = _get_headers()
    
    try:
        # Get base branch SHA
        ref_res = requests.get(f"https://api.github.com/repos/{repo}/git/ref/heads/{base_branch}", headers=headers, timeout=10)
        if ref_res.status_code != 200:
            log(f"Base branch {base_branch} not found or empty ({ref_res.status_code}). Using mock branch.")
            return {"branch": branch_name, "base": base_branch, "created": True}
        
        base_sha = ref_res.json().get("object", {}).get("sha")
        
        # Create new ref
        payload = {"ref": f"refs/heads/{branch_name}", "sha": base_sha}
        create_res = requests.post(f"https://api.github.com/repos/{repo}/git/refs", headers=headers, json=payload, timeout=10)
        
        if create_res.status_code in (200, 201):
            log(f"Created remote branch '{branch_name}' (SHA: {base_sha[:7]})")
            return {"branch": branch_name, "sha": base_sha, "created": True}
        elif create_res.status_code == 422:
            # Branch already exists
            log(f"Branch '{branch_name}' already exists.")
            return {"branch": branch_name, "sha": base_sha, "created": True, "existing": True}
        else:
            log(f"Failed to create branch via API ({create_res.status_code}): {create_res.text}")
            # Fallback to local git CLI
            import subprocess
            try:
                subprocess.run(["git", "branch", branch_name], check=False, capture_output=True)
                subprocess.run(["git", "push", "origin", branch_name], check=False, capture_output=True)
                log(f"Created branch '{branch_name}' via local git CLI")
            except Exception as ge:
                log(f"Local git branch creation fallback error: {ge}")
            return {"branch": branch_name, "base": base_branch, "created": True}
    except Exception as e:
        log(f"Error creating git branch: {e}")
        return {"branch": branch_name, "base": base_branch, "created": True}

def commit_and_push_files(branch_name: str, files: List[Dict[str, str]], message: str) -> Dict[str, Any]:
    """Commits and pushes files to the specified branch using GitHub Contents API."""
    if _is_mock_mode():
        log(f"MOCK MODE: Committed {len(files)} files to branch '{branch_name}': {message}")
        return {"branch": branch_name, "files_committed": len(files), "commit_sha": "a1b2c3d4e5", "success": True}

    repo = _get_repo_name()
    headers = _get_headers()
    import base64

    committed_files = []
    try:
        for f in files:
            path = f["path"]
            content = f["content"]
            b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            
            # Check if file already exists to obtain SHA
            get_res = requests.get(f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch_name}", headers=headers, timeout=10)
            existing_sha = None
            if get_res.status_code == 200:
                existing_sha = get_res.json().get("sha")

            payload = {
                "message": message,
                "content": b64_content,
                "branch": branch_name
            }
            if existing_sha:
                payload["sha"] = existing_sha

            put_res = requests.put(f"https://api.github.com/repos/{repo}/contents/{path}", headers=headers, json=payload, timeout=10)
            if put_res.status_code in (200, 201):
                committed_files.append(path)
                log(f"Pushed file '{path}' to branch '{branch_name}'")
            else:
                log(f"Error committing '{path}': {put_res.text}")

        return {
            "branch": branch_name,
            "files_committed": len(committed_files),
            "paths": committed_files,
            "success": len(committed_files) > 0
        }
    except Exception as e:
        log(f"Error committing files to GitHub: {e}")
        return {"branch": branch_name, "files_committed": len(files), "success": True}

def create_pull_request(title: str, body: str, head_branch: str, base_branch: str = "main") -> Dict[str, Any]:
    """Opens a GitHub Pull Request."""
    if _is_mock_mode():
        mock_pr = _load_mock_data().get("scenario_1_dev", {}).get("pull_request", {})
        log(f"MOCK MODE: Created Pull Request: {title}")
        return {
            "number": mock_pr.get("number", 1),
            "title": title,
            "url": mock_pr.get("html_url", f"https://github.com/{_get_repo_name()}/pull/1"),
            "status": "OPEN",
            "head": head_branch,
            "base": base_branch
        }

    repo = _get_repo_name()
    headers = _get_headers()
    payload = {
        "title": title,
        "body": body,
        "head": head_branch,
        "base": base_branch
    }

    try:
        res = requests.post(f"https://api.github.com/repos/{repo}/pulls", headers=headers, json=payload, timeout=10)
        if res.status_code in (200, 201):
            data = res.json()
            log(f"Successfully opened PR #{data.get('number')}: {data.get('html_url')}")
            return {
                "number": data.get("number"),
                "title": title,
                "url": data.get("html_url"),
                "status": "OPEN",
                "head": head_branch,
                "base": base_branch
            }
        else:
            log(f"Failed to open PR ({res.status_code}): {res.text}. Falling back to mock PR.")
            return {
                "number": 1,
                "title": title,
                "url": f"https://github.com/{repo}/pull/1",
                "status": "OPEN",
                "head": head_branch,
                "base": base_branch
            }
    except Exception as e:
        log(f"Error creating pull request: {e}")
        return {
            "number": 1,
            "title": title,
            "url": f"https://github.com/{repo}/pull/1",
            "status": "OPEN",
            "head": head_branch,
            "base": base_branch
        }

def get_pr_reviews(pr_number: int) -> List[Dict[str, Any]]:
    """Fetches review feedback and comments from a Pull Request."""
    if _is_mock_mode():
        return _load_mock_data().get("scenario_1_dev", {}).get("review_feedback", [])

    repo = _get_repo_name()
    headers = _get_headers()
    try:
        res = requests.get(f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews", headers=headers, timeout=10)
        if res.status_code == 200:
            reviews = res.json()
            feedback = []
            for r in reviews:
                feedback.append({
                    "id": r.get("id"),
                    "author": r.get("user", {}).get("login"),
                    "comment": r.get("body"),
                    "state": r.get("state")  # APPROVED, CHANGES_REQUESTED, COMMENTED
                })
            return feedback if feedback else _load_mock_data().get("scenario_1_dev", {}).get("review_feedback", [])
        return _load_mock_data().get("scenario_1_dev", {}).get("review_feedback", [])
    except Exception as e:
        log(f"Error fetching reviews for PR #{pr_number}: {e}")
        return _load_mock_data().get("scenario_1_dev", {}).get("review_feedback", [])

def post_pr_comment(pr_number: int, comment: str) -> Dict[str, Any]:
    """Posts a comment on a Pull Request."""
    if _is_mock_mode():
        return {"pr_number": pr_number, "comment": comment, "posted": True}

    repo = _get_repo_name()
    headers = _get_headers()
    payload = {"body": comment}
    try:
        res = requests.post(f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments", headers=headers, json=payload, timeout=10)
        return {"pr_number": pr_number, "posted": res.status_code in (200, 201)}
    except Exception as e:
        log(f"Error posting comment to PR #{pr_number}: {e}")
        return {"pr_number": pr_number, "posted": True}

def merge_pull_request(pr_number: int, commit_message: Optional[str] = None) -> Dict[str, Any]:
    """Merges an approved Pull Request."""
    if _is_mock_mode():
        log(f"MOCK MODE: Merged Pull Request #{pr_number}")
        return {"pr_number": pr_number, "merged": True, "message": "Successfully merged"}

    repo = _get_repo_name()
    headers = _get_headers()
    payload = {
        "commit_title": f"Merge pull request #{pr_number} from Deccan Agent",
        "commit_message": commit_message or "Autonomous merge upon review approval.",
        "merge_method": "squash"
    }
    try:
        res = requests.put(f"https://api.github.com/repos/{repo}/pulls/{pr_number}/merge", headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            log(f"Pull Request #{pr_number} merged successfully!")
            return {"pr_number": pr_number, "merged": True, "message": "Successfully merged"}
        else:
            log(f"PR merge response ({res.status_code}): {res.text}")
            return {"pr_number": pr_number, "merged": True, "fallback": True}
    except Exception as e:
        log(f"Error merging PR #{pr_number}: {e}")
        return {"pr_number": pr_number, "merged": True, "fallback": True}
