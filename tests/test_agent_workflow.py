"""Comprehensive test suite verifying Deccan Agents workflows and tools."""

import pytest
import os
from dotenv import load_dotenv

from src.tools.exa_client import search_technical_docs
from src.tools.jira_client import create_jira_issue, transition_jira_issue
from src.tools.teams_client import send_task_acknowledged_card, send_epic_proposal_card
from src.agent.graph import build_deccan_agent_graph

load_dotenv()

@pytest.fixture(scope="module")
def agent_graph():
    return build_deccan_agent_graph()

def test_exa_search_citations():
    """Verify Exa search returns formatted citations with titles and URLs."""
    results = search_technical_docs("JWT token blacklist redis python", num_results=2)
    assert isinstance(results, list)
    assert len(results) >= 1
    first = results[0]
    assert "title" in first
    assert "url" in first
    assert "summary" in first
    assert len(first["summary"]) > 10

def test_teams_adaptive_cards():
    """Verify Teams card generators produce valid delivered payloads."""
    c1 = send_task_acknowledged_card("SCRUM-5", "Test Task")
    assert c1["delivered"] is True

    c2 = send_epic_proposal_card("Enterprise SSO", 21, [{"summary": "SAML", "story_points": 5}])
    assert c2["delivered"] is True

def test_scenario_1_dev_workflow(agent_graph):
    """Verify Scenario 1 (Developer on Holiday) executes full cycle."""
    state = {
        "workflow_mode": "DEV_HOLIDAY",
        "user_prompt": "Lead dev is on holiday. Need urgent JWT refresh token rotation with Redis blacklist.",
        "task_id": "pytest-dev-run"
    }
    result = agent_graph.invoke(state)
    assert result["is_completed"] is True
    assert "SCRUM" in result.get("jira_key", "")
    assert result.get("jira_status") == "Done"
    assert "github.com" in result.get("pr_url", "")
    assert result.get("iteration_count") >= 1
    assert len(result.get("audit_trail", [])) >= 5

def test_scenario_2_pm_workflow(agent_graph):
    """Verify Scenario 2 (Agile PM) executes Epic and story breakdown."""
    state = {
        "workflow_mode": "PM_AGILE",
        "user_prompt": "Decompose Q4 Enterprise Multi-Tenant RBAC into Jira Epics and Stories.",
        "task_id": "pytest-pm-run"
    }
    result = agent_graph.invoke(state)
    assert result["is_completed"] is True
    assert "SCRUM" in result.get("epic_key", "")
    assert len(result.get("stories", [])) == 4
    assert result.get("total_story_points") == 21
    assert len(result.get("audit_trail", [])) >= 3
