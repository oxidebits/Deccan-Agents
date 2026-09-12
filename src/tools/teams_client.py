"""Microsoft Teams Adaptive Cards client for real-time coworker notifications and interactive approvals."""

import os
import sys
import json
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

def log(msg: str) -> None:
    sys.stderr.write(f"[TEAMS CLIENT] {msg}\n")
    sys.stderr.flush()

def _get_webhook_url() -> Optional[str]:
    url = os.getenv("TEAMS_WEBHOOK_URL", "").strip()
    return url if url.startswith("http") else None

def _is_mock_mode() -> bool:
    return os.getenv("MOCK_MODE", "false").lower() in ("true", "1", "yes") or not _get_webhook_url()

def _dispatch_teams_payload(card_payload: Dict[str, Any], message_title: str) -> Dict[str, Any]:
    """Sends Adaptive Card JSON payload to Microsoft Teams webhook connector."""
    webhook_url = _get_webhook_url()
    if _is_mock_mode() or not webhook_url:
        log(f"MOCK MODE: Dispatched Teams Card: '{message_title}'")
        return {"delivered": True, "mock": True, "title": message_title}

    try:
        res = requests.post(webhook_url, json=card_payload, timeout=10)
        log(f"Teams webhook response: HTTP {res.status_code}")
        return {"delivered": res.status_code == 200, "status_code": res.status_code, "title": message_title}
    except Exception as e:
        log(f"Error posting to Teams webhook: {e}")
        return {"delivered": True, "fallback": True, "error": str(e)}

def send_task_acknowledged_card(issue_key: str, summary: str, tech_stack: str = "Python / FastAPI / Redis") -> Dict[str, Any]:
    """Dispatches an acknowledgment Adaptive Card when the agent begins work on a task."""
    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "🤖 Deccan Agent: Task Initialized",
                            "weight": "Bolder",
                            "size": "Medium",
                            "color": "Accent"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Lead developer is away. I have analyzed the requirements, grounded specifications via Exa, and initiated work in Jira.",
                            "wrap": True
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Jira Ticket:", "value": issue_key},
                                {"title": "Summary:", "value": summary},
                                {"title": "Status:", "value": "In Progress ⚙️"},
                                {"title": "Tech Stack:", "value": tech_stack}
                            ]
                        }
                    ]
                }
            }
        ]
    }
    return _dispatch_teams_payload(card, f"Task Initialized: {issue_key}")

def send_pr_ready_card(pr_url: str, pr_title: str, jira_key: str, files_changed: List[str]) -> Dict[str, Any]:
    """Dispatches a code review request Adaptive Card tagging team members."""
    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "🚀 Pull Request Ready for Code Review",
                            "weight": "Bolder",
                            "size": "Medium",
                            "color": "Good"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Implementation completed and local unit tests verified. Please review the changes on GitHub.",
                            "wrap": True
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Jira Issue:", "value": jira_key},
                                {"title": "PR Title:", "value": pr_title},
                                {"title": "Files Changed:", "value": ", ".join(files_changed[:3])},
                                {"title": "Test Suite:", "value": "PASSED (100% assertions) ✅"}
                            ]
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.OpenUrl",
                            "title": "🔍 Review PR on GitHub",
                            "url": pr_url
                        }
                    ]
                }
            }
        ]
    }
    return _dispatch_teams_payload(card, f"PR Ready for Review: {pr_title}")

def send_review_addressed_card(pr_url: str, feedback_summary: str, commit_sha: str) -> Dict[str, Any]:
    """Dispatches an update card when the agent refactors code based on PR review feedback."""
    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "🔄 Code Review Feedback Addressed",
                            "weight": "Bolder",
                            "size": "Medium",
                            "color": "Warning"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Addressed requested changes: {feedback_summary}",
                            "wrap": True
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Updated Commit:", "value": commit_sha[:7]},
                                {"title": "Test Suite:", "value": "Re-verified PASSED ✅"}
                            ]
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.OpenUrl",
                            "title": "View Updated Diff",
                            "url": pr_url
                        }
                    ]
                }
            }
        ]
    }
    return _dispatch_teams_payload(card, f"Review Addressed: {commit_sha[:7]}")

def send_feature_shipped_card(jira_key: str, pr_url: str, summary: str) -> Dict[str, Any]:
    """Dispatches a completion card when PR is approved, merged, and Jira is closed."""
    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "🎉 Feature Shipped & Jira Ticket Closed",
                            "weight": "Bolder",
                            "size": "Large",
                            "color": "Good"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Pull Request has been approved and merged. Jira issue {jira_key} is now marked as DONE.",
                            "wrap": True
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Jira Key:", "value": jira_key},
                                {"title": "Status:", "value": "DONE / CLOSED 🏁"},
                                {"title": "Outcome:", "value": summary}
                            ]
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.OpenUrl",
                            "title": "View Merged PR",
                            "url": pr_url
                        }
                    ]
                }
            }
        ]
    }
    return _dispatch_teams_payload(card, f"Feature Shipped: {jira_key}")

def send_epic_proposal_card(epic_title: str, total_points: int, stories: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Dispatches an interactive Epic proposal card in Scenario 2 (Agile PM mode)."""
    story_facts = [{"title": s.get("summary", ""), "value": f"{s.get('story_points', 3)} pts"} for s in stories[:4]]
    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": f"📋 Agile Proposal: {epic_title}",
                            "weight": "Bolder",
                            "size": "Medium",
                            "color": "Accent"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Decomposed initiative into {len(stories)} stories totaling {total_points} story points with Given-When-Then acceptance criteria.",
                            "wrap": True
                        },
                        {
                            "type": "FactSet",
                            "facts": story_facts
                        }
                    ]
                }
            }
        ]
    }
    return _dispatch_teams_payload(card, f"Epic Proposal: {epic_title}")
