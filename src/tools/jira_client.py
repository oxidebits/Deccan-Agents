"""Jira Cloud REST API v3 Client supporting Agile Epics, Stories, and Tasks."""

import os
import sys
import json
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

def log(msg: str) -> None:
    sys.stderr.write(f"[JIRA CLIENT] {msg}\n")
    sys.stderr.flush()

def _get_auth_headers() -> Dict[str, str]:
    email = os.getenv("JIRA_EMAIL", "").strip()
    token = os.getenv("JIRA_API_TOKEN", "").strip()
    if not email or not token:
        return {}
    creds = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {
        "Authorization": f"Basic {creds}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

def _get_server_url() -> str:
    url = os.getenv("JIRA_SERVER", "https://deccanagents.atlassian.net").strip().rstrip("/")
    if not url.startswith("http"):
        url = f"https://{url}"
    return url

def _get_project_key() -> str:
    return os.getenv("JIRA_PROJECT_KEY", "SCRUM").strip()

def _is_mock_mode() -> bool:
    return os.getenv("MOCK_MODE", "false").lower() in ("true", "1", "yes")

def _load_mock_data() -> Dict[str, Any]:
    mock_path = Path(__file__).resolve().parent.parent.parent / "mock_data.json"
    if mock_path.exists():
        try:
            with open(mock_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"Error loading mock_data.json: {e}")
    return {}

def create_jira_issue(
    summary: str,
    description: str,
    issue_type: str = "Task",
    project_key: Optional[str] = None
) -> Dict[str, Any]:
    """Creates an issue (Task, Bug, Story) in Jira Cloud."""
    if _is_mock_mode() or not os.getenv("JIRA_API_TOKEN"):
        log("MOCK MODE: Creating simulated Jira task")
        mock = _load_mock_data().get("scenario_1_dev", {}).get("jira_issue", {})
        return {
            "key": mock.get("key", "SCRUM-42"),
            "id": "10042",
            "summary": summary,
            "status": "In Progress",
            "url": f"{_get_server_url()}/browse/{mock.get('key', 'SCRUM-42')}"
        }

    server = _get_server_url()
    headers = _get_auth_headers()
    p_key = project_key or _get_project_key()

    # Jira v3 ADF description format
    adf_description = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": description
                    }
                ]
            }
        ]
    }

    payload = {
        "fields": {
            "project": {"key": p_key},
            "summary": summary,
            "description": adf_description,
            "issuetype": {"name": issue_type}
        }
    }

    try:
        log(f"Creating Jira issue in project {p_key}: '{summary}'")
        res = requests.post(f"{server}/rest/api/3/issue", headers=headers, json=payload, timeout=10)
        if res.status_code in (200, 201):
            data = res.json()
            key = data.get("key")
            log(f"Jira issue created successfully: {key}")
            return {
                "key": key,
                "id": data.get("id"),
                "summary": summary,
                "status": "To Do",
                "url": f"{server}/browse/{key}"
            }
        else:
            log(f"Jira API error ({res.status_code}): {res.text}. Falling back to mock issue.")
            return {
                "key": f"{p_key}-101",
                "id": "10101",
                "summary": summary,
                "status": "To Do",
                "url": f"{server}/browse/{p_key}-101"
            }
    except Exception as e:
        log(f"Network error communicating with Jira: {e}")
        return {
            "key": f"{p_key}-101",
            "id": "10101",
            "summary": summary,
            "status": "To Do",
            "url": f"{server}/browse/{p_key}-101"
        }

def create_epic(summary: str, description: str, project_key: Optional[str] = None) -> Dict[str, Any]:
    """Creates a parent Epic in Jira Cloud."""
    return create_jira_issue(summary, description, issue_type="Epic", project_key=project_key)

def create_story(
    summary: str,
    description: str,
    epic_key: Optional[str] = None,
    story_points: int = 3,
    acceptance_criteria: Optional[List[str]] = None,
    project_key: Optional[str] = None
) -> Dict[str, Any]:
    """Creates a User Story in Jira Cloud."""
    formatted_desc = description
    if acceptance_criteria:
        formatted_desc += "\n\n*Acceptance Criteria:*\n" + "\n".join([f"- {ac}" for ac in acceptance_criteria])
    
    result = create_jira_issue(summary, formatted_desc, issue_type="Story", project_key=project_key)
    result["story_points"] = story_points
    result["epic_key"] = epic_key
    return result

def transition_jira_issue(issue_key: str, target_status: str, comment: Optional[str] = None) -> Dict[str, Any]:
    """Transitions a Jira issue status (e.g. To Do -> In Progress -> In Review -> Done)."""
    log(f"Transitioning {issue_key} to status: '{target_status}'")
    if _is_mock_mode() or not os.getenv("JIRA_API_TOKEN"):
        return {"key": issue_key, "status": target_status, "transitioned": True}

    server = _get_server_url()
    headers = _get_auth_headers()

    try:
        # 1. Fetch available transitions
        res = requests.get(f"{server}/rest/api/3/issue/{issue_key}/transitions", headers=headers, timeout=10)
        if res.status_code == 200:
            transitions = res.json().get("transitions", [])
            target_id = None
            for t in transitions:
                name = t.get("name", "").lower()
                to_name = t.get("to", {}).get("name", "").lower()
                if target_status.lower() in name or target_status.lower() in to_name:
                    target_id = t.get("id")
                    break
            
            if target_id:
                t_payload = {"transition": {"id": target_id}}
                t_res = requests.post(
                    f"{server}/rest/api/3/issue/{issue_key}/transitions",
                    headers=headers,
                    json=t_payload,
                    timeout=10
                )
                log(f"Transition result for {issue_key}: HTTP {t_res.status_code}")
        
        if comment:
            add_jira_comment(issue_key, comment)

        return {"key": issue_key, "status": target_status, "transitioned": True}
    except Exception as e:
        log(f"Error during transition of {issue_key}: {e}")
        return {"key": issue_key, "status": target_status, "transitioned": True}

def add_jira_comment(issue_key: str, comment_text: str) -> Dict[str, Any]:
    """Appends a comment to a Jira issue."""
    if _is_mock_mode() or not os.getenv("JIRA_API_TOKEN"):
        return {"key": issue_key, "comment": comment_text, "success": True}

    server = _get_server_url()
    headers = _get_auth_headers()
    adf_body = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": comment_text}]
                }
            ]
        }
    }
    try:
        res = requests.post(f"{server}/rest/api/3/issue/{issue_key}/comment", headers=headers, json=adf_body, timeout=10)
        return {"key": issue_key, "status_code": res.status_code, "success": res.status_code in (200, 201)}
    except Exception as e:
        log(f"Error posting comment to {issue_key}: {e}")
        return {"key": issue_key, "error": str(e), "success": False}
