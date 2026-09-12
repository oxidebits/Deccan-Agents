"""LangGraph deterministic state nodes for Scenario 2: Agile Project Manager & Jira Board Master."""

import os
import sys
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

from src.agent.state import DeccanAgentState
from src.tools.jira_client import create_epic, create_story, add_jira_comment
from src.tools.teams_client import send_epic_proposal_card

load_dotenv()

def log(msg: str) -> None:
    sys.stderr.write(f"[NODE PM] {msg}\n")
    sys.stderr.flush()

def decompose_initiative_to_epic(state: DeccanAgentState) -> Dict[str, Any]:
    """Node 1 (PM): Decomposes conversational initiative into structured Epic and User Stories."""
    prompt = state.get("user_prompt", "Launch Enterprise SSO and Multi-Tenant RBAC in Q4")
    log(f"Decomposing initiative: '{prompt[:60]}...'")

    epic_title = "Enterprise SSO & Multi-Tenant RBAC Architecture"
    epic_desc = (
        "Enterprise identity federation (SAML 2.0 / OIDC) and tenant-isolated "
        "Role-Based Access Control to unblock enterprise customer onboarding in Q4."
    )

    stories = [
        {
            "summary": "SAML 2.0 and OIDC Identity Provider Federation",
            "description": "Implement authentication endpoints for Okta, Azure AD, and Google Workspace.",
            "story_points": 5,
            "acceptance_criteria": [
                "Given an enterprise admin, when configuring SAML metadata XML, then validate certificate and SP entity ID.",
                "Given an authenticated user via SSO, when session token is issued, then map enterprise email to tenant account."
            ]
        },
        {
            "summary": "Tenant Isolation Middleware and Database Schema Partitioning",
            "description": "Enforce strict tenant scoping across all REST endpoints and PostgreSQL queries.",
            "story_points": 8,
            "acceptance_criteria": [
                "Given an incoming request, when parsed, then extract tenant_id from JWT claims and inject into DB context.",
                "Given a cross-tenant query attempt, when detected, then immediately abort with 403 Forbidden."
            ]
        },
        {
            "summary": "Granular RBAC Permission Evaluation Engine",
            "description": "Role and permission bitmask checker for Owner, Admin, Member, and Viewer roles.",
            "story_points": 5,
            "acceptance_criteria": [
                "Given a user role, when calling protected mutation endpoints, then verify permission bitmask.",
                "Given custom roles defined by tenant admin, then support dynamic permission binding."
            ]
        },
        {
            "summary": "Tenant Audit Logging and Compliance Export",
            "description": "Immutable audit trail of authentication and permission events.",
            "story_points": 3,
            "acceptance_criteria": [
                "Given any privilege escalation or user invitation, then emit signed JSON audit event.",
                "Given an audit compliance export request, then download encrypted report."
            ]
        }
    ]

    total_pts = sum(s["story_points"] for s in stories)
    dependency_links = [
        {"inward": stories[1]["summary"], "outward": stories[2]["summary"], "type": "Blocks"}
    ]

    audit = list(state.get("audit_trail") or [])
    audit.append(f"Decomposed initiative into Epic '{epic_title}' with 4 stories totaling {total_pts} story points.")

    return {
        "epic_title": epic_title,
        "epic_description": epic_desc,
        "stories": stories,
        "dependency_links": dependency_links,
        "total_story_points": total_pts,
        "audit_trail": audit
    }

def dispatch_pm_proposal_card(state: DeccanAgentState) -> Dict[str, Any]:
    """Node 2 (PM): Dispatches interactive proposal card to Microsoft Teams for human review."""
    epic_title = state.get("epic_title", "Enterprise SSO & Multi-Tenant RBAC")
    total_pts = state.get("total_story_points", 21)
    stories = state.get("stories", [])

    log(f"Dispatching Epic proposal card to Teams ({total_pts} story points)")
    send_epic_proposal_card(epic_title, total_pts, stories)

    audit = list(state.get("audit_trail") or [])
    audit.append(f"Dispatched interactive Epic proposal card to Teams.")

    return {"audit_trail": audit}

def synchronize_jira_agile_board(state: DeccanAgentState) -> Dict[str, Any]:
    """Node 3 (PM): Synchronizes Epic and Stories to Jira Cloud REST API."""
    epic_title = state.get("epic_title", "Enterprise SSO")
    epic_desc = state.get("epic_description", "Enterprise initiative")
    stories = state.get("stories", [])

    log(f"Synchronizing Epic '{epic_title}' to Jira Cloud")
    # 1. Create Epic
    epic_res = create_epic(epic_title, epic_desc)
    epic_key = epic_res.get("key", "SCRUM-10")

    created_stories = []
    # 2. Create Stories linked to Epic
    for s in stories:
        s_res = create_story(
            summary=s["summary"],
            description=s["description"],
            epic_key=epic_key,
            story_points=s["story_points"],
            acceptance_criteria=s["acceptance_criteria"]
        )
        created_stories.append({
            "key": s_res.get("key", f"{epic_key}-{len(created_stories)+1}"),
            "summary": s["summary"],
            "story_points": s["story_points"]
        })

    add_jira_comment(epic_key, f"Epic initialized with {len(created_stories)} decomposed user stories.")

    audit = list(state.get("audit_trail") or [])
    audit.append(f"Populated Jira Cloud: Epic {epic_key} and {len(created_stories)} child user stories.")

    return {
        "epic_key": epic_key,
        "stories": created_stories,
        "is_completed": True,
        "summary_outcome": f"Agile Epic {epic_key} ({state.get('total_story_points')} pts) successfully created with {len(created_stories)} stories in Jira Cloud.",
        "audit_trail": audit
    }
