#!/usr/bin/env python3
"""
Deccan Agents — Unified Webhook Server & FastMCP Stdio Interface.
Autonomous Software Engineer & Agile Project Manager Coworker in Microsoft Teams.
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# FastAPI & Starlette
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except (ImportError, ModuleNotFoundError):
    from mcp.server import MCPServer as FastMCP

from pydantic import BaseModel, Field

# Core Agent Graph & Tools
from src.agent.graph import build_deccan_agent_graph
from src.tools.exa_client import search_technical_docs
from src.tools.jira_client import create_jira_issue, transition_jira_issue, create_epic, create_story
from src.tools.github_client import create_pull_request, get_pr_reviews
from src.tools.teams_client import send_task_acknowledged_card, send_epic_proposal_card

load_dotenv()

# Logging: stdout is strictly reserved for stdio JSON-RPC. All diagnostics route to stderr.
def log(msg: str) -> None:
    sys.stderr.write(f"[DECCAN SERVER] {msg}\n")
    sys.stderr.flush()

# Initialize FastAPI App
app = FastAPI(
    title="Deccan Agents Server",
    description="Autonomous Software Engineer & Agile Project Manager Coworker in Microsoft Teams",
    version="1.0.0"
)

# Initialize FastMCP Server
mcp = FastMCP("DeccanAgents")

# Global Compiled LangGraph
agent_graph = build_deccan_agent_graph()

# ---------------------------------------------------------------------------
# 1. FastAPI REST Endpoints & Webhooks
# ---------------------------------------------------------------------------

class WorkflowTriggerRequest(BaseModel):
    prompt: Optional[str] = Field(None, description="Custom prompt or feature request")
    mode: Optional[str] = Field("DEV_HOLIDAY", description="Workflow mode: DEV_HOLIDAY or PM_AGILE")

@app.get("/api/status")
def get_status() -> Dict[str, Any]:
    """Health check endpoint providing live integration status."""
    return {
        "service": "Deccan Agents",
        "status": "OPERATIONAL",
        "version": "1.0.0",
        "integrations": {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "exa": bool(os.getenv("EXA_API_KEY")),
            "github": bool(os.getenv("GITHUB_TOKEN")),
            "jira": bool(os.getenv("JIRA_API_TOKEN")),
            "teams": bool(os.getenv("TEAMS_WEBHOOK_URL") or os.getenv("MICROSOFT_APP_ID"))
        },
        "target_repo": os.getenv("GITHUB_REPO", "oxidebits/Deccan-Agents"),
        "target_jira": os.getenv("JIRA_SERVER", "https://deccanagents.atlassian.net")
    }

@app.post("/api/simulate-dev-workflow")
def simulate_dev_workflow(request: Optional[WorkflowTriggerRequest] = None) -> Dict[str, Any]:
    """1-Click Trigger for Scenario 1: Developer on Holiday / Cyclic Code Review Loop."""
    prompt = (request and request.prompt) or "Developer is on holiday. Implement JWT refresh token rotation with Redis blacklist for auth service."
    log(f"Triggering Scenario 1 (Dev Holiday) with prompt: '{prompt}'")
    
    state = {
        "workflow_mode": "DEV_HOLIDAY",
        "user_prompt": prompt,
        "task_id": "sim-dev-run-1"
    }
    
    result = agent_graph.invoke(state)
    return {
        "success": True,
        "scenario": "Scenario 1: Stand-in Developer",
        "jira_key": result.get("jira_key"),
        "jira_status": result.get("jira_status"),
        "github_pr": result.get("pr_url"),
        "review_iterations": result.get("iteration_count"),
        "test_results": result.get("test_results"),
        "audit_trail": result.get("audit_trail")
    }

@app.post("/api/simulate-pm-workflow")
def simulate_pm_workflow(request: Optional[WorkflowTriggerRequest] = None) -> Dict[str, Any]:
    """1-Click Trigger for Scenario 2: Agile Project Manager & Jira Epic Decomposition."""
    prompt = (request and request.prompt) or "Launch our Q4 Enterprise SSO and Multi-Tenant RBAC initiative."
    log(f"Triggering Scenario 2 (Agile PM) with prompt: '{prompt}'")
    
    state = {
        "workflow_mode": "PM_AGILE",
        "user_prompt": prompt,
        "task_id": "sim-pm-run-1"
    }
    
    result = agent_graph.invoke(state)
    return {
        "success": True,
        "scenario": "Scenario 2: Agile Project Manager",
        "epic_key": result.get("epic_key"),
        "stories_created": result.get("stories"),
        "total_story_points": result.get("total_story_points"),
        "audit_trail": result.get("audit_trail")
    }

@app.post("/api/messages")
async def handle_teams_messages(request: Request, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Microsoft Teams Bot Framework / Webhook message endpoint."""
    try:
        body = await request.json()
        log(f"Received inbound Teams message: {json.dumps(body)[:200]}")
        text = body.get("text", "") or body.get("value", {}).get("text", "")

        # Route mode based on keywords
        mode = "PM_AGILE" if any(k in text.lower() for k in ["epic", "sprint", "backlog", "initiative", "stories"]) else "DEV_HOLIDAY"

        def run_agent_job():
            agent_graph.invoke({
                "workflow_mode": mode,
                "user_prompt": text or "Inbound request from Teams",
                "task_id": "teams-msg-run"
            })

        background_tasks.add_task(run_agent_job)
        return {"status": "accepted", "mode": mode}
    except Exception as e:
        log(f"Error handling Teams message: {e}")
        return {"status": "error", "error": str(e)}

@app.post("/webhooks/github")
async def handle_github_webhook(request: Request, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """GitHub Webhook Receiver for Pull Request Reviews and Issue Comments."""
    try:
        event = request.headers.get("X-GitHub-Event", "ping")
        body = await request.json()
        log(f"Received GitHub webhook event: {event}")

        if event == "ping":
            return {"status": "pong"}

        action = body.get("action", "")
        review = body.get("review", {})
        pr = body.get("pull_request", {})

        if event == "pull_request_review":
            review_state = review.get("state")
            log(f"PR #{pr.get('number')} Review submitted: {review_state}")

            def run_review_eval():
                agent_graph.invoke({
                    "workflow_mode": "DEV_HOLIDAY",
                    "pr_number": pr.get("number", 1),
                    "jira_key": os.getenv("JIRA_PROJECT_KEY", "SCRUM") + "-6",
                    "user_prompt": f"PR Review received: {review_state}"
                })

            background_tasks.add_task(run_review_eval)

        return {"status": "processed", "event": event, "action": action}
    except Exception as e:
        log(f"Error processing GitHub webhook: {e}")
        return {"status": "error", "error": str(e)}

# ---------------------------------------------------------------------------
# 2. FastMCP Tool Declarations (Stdio / JSON-RPC)
# ---------------------------------------------------------------------------

@mcp.tool()
def execute_dev_feature(prompt: str) -> str:
    """Executes Scenario 1: Decomposes prompt, grounds with Exa, creates Jira task, writes code, and opens PR."""
    log(f"FastMCP Tool: execute_dev_feature('{prompt[:50]}...')")
    state = {
        "workflow_mode": "DEV_HOLIDAY",
        "user_prompt": prompt,
        "task_id": "mcp-dev-tool"
    }
    res = agent_graph.invoke(state)
    return json.dumps({
        "status": "COMPLETED",
        "jira_key": res.get("jira_key"),
        "pr_url": res.get("pr_url"),
        "iterations": res.get("iteration_count"),
        "audit": res.get("audit_trail")
    }, indent=2)

@mcp.tool()
def execute_pm_agile_initiative(prompt: str) -> str:
    """Executes Scenario 2: Decomposes initiative into Epic, user stories, story points, and populates Jira."""
    log(f"FastMCP Tool: execute_pm_agile_initiative('{prompt[:50]}...')")
    state = {
        "workflow_mode": "PM_AGILE",
        "user_prompt": prompt,
        "task_id": "mcp-pm-tool"
    }
    res = agent_graph.invoke(state)
    return json.dumps({
        "status": "COMPLETED",
        "epic_key": res.get("epic_key"),
        "stories": res.get("stories"),
        "total_points": res.get("total_story_points"),
        "audit": res.get("audit_trail")
    }, indent=2)

@mcp.tool()
def search_technical_documentation(query: str) -> str:
    """Performs real-time neural search via Exa AI to retrieve verified technical citations."""
    results = search_technical_docs(query, num_results=2)
    return json.dumps(results, indent=2)

# ---------------------------------------------------------------------------
# 3. Main Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        log("Starting Deccan Agents in stdio FastMCP mode...")
        mcp.run()
    else:
        port = int(os.getenv("PORT", 8000))
        log(f"Starting Deccan Agents FastAPI server on port {port}...")
        uvicorn.run(app, host="0.0.0.0", port=port)
