"""Agent State Definition for Deccan Agents LangGraph StateMachine."""

from typing import TypedDict, List, Dict, Any, Optional, Literal

class DeccanAgentState(TypedDict, total=False):
    # Workflow Mode Selector
    workflow_mode: Literal["DEV_HOLIDAY", "PM_AGILE"]
    user_prompt: str
    task_id: str
    
    # Technical Grounding & Spec (Shared / Scenario 1)
    technical_spec: Dict[str, Any]
    exa_citations: List[Dict[str, str]]
    
    # Jira Tracking (Shared / Scenario 1)
    jira_key: str
    jira_summary: str
    jira_status: str
    jira_url: str
    
    # GitHub Code & PR Operations (Scenario 1)
    git_branch: str
    code_changes: List[Dict[str, str]]
    test_results: Dict[str, Any]
    pr_number: int
    pr_url: str
    pr_title: str
    
    # Code Review & Refactoring Feedback Loop (Scenario 1)
    review_status: Literal["PENDING", "CHANGES_REQUESTED", "APPROVED"]
    review_feedback_history: List[Dict[str, Any]]
    iteration_count: int
    max_iterations: int
    
    # Agile PM Initiatives & Epic Planning (Scenario 2)
    epic_key: str
    epic_title: str
    epic_description: str
    stories: List[Dict[str, Any]]
    dependency_links: List[Dict[str, str]]
    total_story_points: int
    
    # Completion & Audit
    is_completed: bool
    summary_outcome: str
    audit_trail: List[str]
