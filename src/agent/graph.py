"""Unified LangGraph StateGraph connecting Dev & PM nodes with cyclic review loop."""

import os
import sys
from typing import Literal
from langgraph.graph import StateGraph, END

from src.agent.state import DeccanAgentState
from src.agent.nodes_dev import (
    plan_and_ground_feature,
    create_jira_tracking_task,
    synthesize_and_test_code,
    open_github_pr_and_request_review,
    evaluate_and_refactor_review,
    finalize_and_release
)
from src.agent.nodes_pm import (
    decompose_initiative_to_epic,
    dispatch_pm_proposal_card,
    synchronize_jira_agile_board
)

def route_workflow_mode(state: DeccanAgentState) -> str:
    """Routes initial execution based on whether the task is a Dev Feature or an Agile PM Initiative."""
    mode = state.get("workflow_mode")
    if mode == "PM_AGILE":
        return "decompose_initiative_to_epic"
    return "plan_and_ground_feature"

def route_review_feedback(state: DeccanAgentState) -> Literal["evaluate_and_refactor_review", "finalize_and_release"]:
    """Conditional router for the iterative code review loop."""
    review_status = state.get("review_status", "PENDING")
    iteration = state.get("iteration_count", 0)
    max_iter = state.get("max_iterations", 3)

    if review_status == "CHANGES_REQUESTED" and iteration < max_iter:
        return "evaluate_and_refactor_review"
    return "finalize_and_release"

def build_deccan_agent_graph():
    """Builds and compiles the unified Deccan Agents LangGraph StateGraph."""
    workflow = StateGraph(DeccanAgentState)

    # --- Scenario 1: Developer Nodes ---
    workflow.add_node("plan_and_ground_feature", plan_and_ground_feature)
    workflow.add_node("create_jira_tracking_task", create_jira_tracking_task)
    workflow.add_node("synthesize_and_test_code", synthesize_and_test_code)
    workflow.add_node("open_github_pr_and_request_review", open_github_pr_and_request_review)
    workflow.add_node("evaluate_and_refactor_review", evaluate_and_refactor_review)
    workflow.add_node("finalize_and_release", finalize_and_release)

    # --- Scenario 2: Agile PM Nodes ---
    workflow.add_node("decompose_initiative_to_epic", decompose_initiative_to_epic)
    workflow.add_node("dispatch_pm_proposal_card", dispatch_pm_proposal_card)
    workflow.add_node("synchronize_jira_agile_board", synchronize_jira_agile_board)

    # --- Entry Point & Mode Routing ---
    workflow.set_conditional_entry_point(
        route_workflow_mode,
        {
            "plan_and_ground_feature": "plan_and_ground_feature",
            "decompose_initiative_to_epic": "decompose_initiative_to_epic"
        }
    )

    # --- Scenario 1 Edges ---
    workflow.add_edge("plan_and_ground_feature", "create_jira_tracking_task")
    workflow.add_edge("create_jira_tracking_task", "synthesize_and_test_code")
    workflow.add_edge("synthesize_and_test_code", "open_github_pr_and_request_review")
    workflow.add_edge("open_github_pr_and_request_review", "evaluate_and_refactor_review")

    # Cyclic Review Refinement Edge
    workflow.add_conditional_edges(
        "evaluate_and_refactor_review",
        route_review_feedback,
        {
            "evaluate_and_refactor_review": "evaluate_and_refactor_review",
            "finalize_and_release": "finalize_and_release"
        }
    )
    workflow.add_edge("finalize_and_release", END)

    # --- Scenario 2 Edges ---
    workflow.add_edge("decompose_initiative_to_epic", "dispatch_pm_proposal_card")
    workflow.add_edge("dispatch_pm_proposal_card", "synchronize_jira_agile_board")
    workflow.add_edge("synchronize_jira_agile_board", END)

    return workflow.compile()
