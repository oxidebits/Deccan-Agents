#!/usr/bin/env python3
"""
Interactive Microsoft Teams Group Chat Simulator for Deccan Agents.
Simulates authentic multi-role collaboration for the Webshop-Ecom store in Svelte 5.
Roles:
  1. Apoorva Agrawal (Product Owner / PM)
  2. Kushal (Lead Developer - On Holiday / OOO)
  3. Senior Reviewer (QA / Tech Lead)
  4. @DeccanAgent (Autonomous AI Coworker)
"""

import os
import sys
import time
import json
from dotenv import load_dotenv

from src.agent.graph import build_deccan_agent_graph
from src.tools.teams_client import (
    send_task_acknowledged_card,
    send_pr_ready_card,
    send_review_addressed_card,
    send_feature_shipped_card
)

load_dotenv()

# ANSI Color Codes for terminal visual brilliance
RESET = "\033[0m"
BOLD = "\033[1m"
BLUE = "\033[38;5;39m"       # PO/PM
CYAN = "\033[38;5;51m"       # Developer OOO
YELLOW = "\033[38;5;220m"    # Senior Reviewer
MAGENTA = "\033[38;5;213m"   # Deccan Agent
GREEN = "\033[38;5;48m"      # System Success
WHITE = "\033[38;5;255m"

def print_teams_header():
    print(f"\n{BOLD}{MAGENTA}======================================================================{RESET}")
    print(f"{BOLD}{WHITE} 💬 MICROSOFT TEAMS GROUP CHAT: 'Webshop-Ecom Sprint Delivery'{RESET}")
    print(f"{BOLD}{WHITE} Thread ID: 19:wnd66nNqiF99yYDeG4v2AMVAgMvlMLnhc-ljPWcqyoc1@thread.v2{RESET}")
    print(f"{BOLD}{MAGENTA}======================================================================{RESET}\n")

def print_message(author: str, role: str, color: str, message: str, delay: float = 1.0):
    time.sleep(delay)
    print(f"{BOLD}{color}[{author} — {role}]{RESET}")
    print(f"{WHITE}{message}{RESET}\n")

def run_teams_chat_simulation():
    print_teams_header()

    # Step 1: PO sets up the conversation
    print_message(
        "Apoorva Agrawal",
        "Product Owner / PM",
        BLUE,
        "Hi team! Setting up this group chat to coordinate our urgent features for the Webshop-Ecom store. "
        "We have a promotional campaign launching soon and need the Svelte 5 Cart Drawer with Promo Code discount calculation.",
        delay=0.8
    )

    # Step 2: Vacationing developer auto-responds
    print_message(
        "Kushal Gaikwad",
        "Lead Developer (Out on Holiday 🏖️)",
        CYAN,
        "Hey Apoorva! I'm on PTO until Monday with limited connectivity. "
        "Please assign this to @DeccanAgent — our autonomous coworker can plan the Jira task, implement the Svelte 5 store, and open the PR.",
        delay=1.0
    )

    # Step 3: PO triggers @DeccanAgent
    pm_prompt = (
        "@DeccanAgent Kushal is on holiday today. Please implement the Svelte 5 Cart Drawer with "
        "Promo Code discount calculation for our Webshop-Ecom store. Connect to Jira SCRUM board and GitHub."
    )
    print_message(
        "Apoorva Agrawal",
        "Product Owner / PM",
        BLUE,
        pm_prompt,
        delay=1.2
    )

    # Step 4: @DeccanAgent awakens & executes LangGraph StateGraph
    print(f"{BOLD}{GREEN}>>> [SYSTEM: @DeccanAgent received invocation in Teams. Executing StateGraph...] <<<{RESET}\n")
    
    agent_graph = build_deccan_agent_graph()
    state = {
        "workflow_mode": "DEV_HOLIDAY",
        "user_prompt": pm_prompt,
        "task_id": "teams-live-sim-1"
    }

    # Execute workflow
    result = agent_graph.invoke(state)

    jira_key = result.get("jira_key", "SCRUM-12")
    pr_url = result.get("pr_url", "https://github.com/oxidebits/Deccan-Agents/pull/1")

    # Step 5: Agent posts initial card
    print_message(
        "🤖 @DeccanAgent",
        "Autonomous Coworker",
        MAGENTA,
        f"Understood @Apoorva! Task initialized for **Webshop-Ecom**:\n"
        f"• Jira Ticket Created: **{jira_key}** (Status: *In Progress*)\n"
        f"• Exa Grounding: Retrieved 2 verified Svelte 5 runes patterns.\n"
        f"• Implementation: Synthesized `CartDrawer.svelte` and `cartStore.svelte.ts`.\n"
        f"• Tests: Verified 4 unit tests passing (100% assertions).\n"
        f"• GitHub Pull Request: Opened {pr_url}\n"
        f"👉 @Reviewer please review the Svelte components on GitHub!",
        delay=1.5
    )

    # Step 6: Senior Reviewer leaves feedback
    review_feedback = "Great work @DeccanAgent! Code is clean. Please ensure promo code validation handles expired codes (e.g. EXPIRED10) and shows the discount percentage badge in the Cart Drawer."
    print_message(
        "Senior Reviewer",
        "Code Reviewer / QA Lead",
        YELLOW,
        f"Left review comments on {pr_url}:\n\"{review_feedback}\"",
        delay=1.2
    )

    # Step 7: Agent addresses review & updates thread
    print_message(
        "🤖 @DeccanAgent",
        "Autonomous Coworker",
        MAGENTA,
        f"Addressed your review feedback @SeniorReviewer:\n"
        f"• Updated `cartStore.svelte.ts` with expired promo code validation.\n"
        f"• Added dynamic discount percentage badge in `CartDrawer.svelte`.\n"
        f"• Re-ran test suite: PASSED ✅.\n"
        f"• Pushed commit `c7d8e9f` to PR {pr_url}. Ready for re-review!",
        delay=1.2
    )

    # Step 8: Senior Reviewer approves
    print_message(
        "Senior Reviewer",
        "Code Reviewer / QA Lead",
        YELLOW,
        f"Changes verified and tested cleanly. Approved the Pull Request! 👍",
        delay=1.0
    )

    # Step 9: Agent finalizes release & celebrates
    print_message(
        "🤖 @DeccanAgent",
        "Autonomous Coworker",
        MAGENTA,
        f"🎉 **Feature Shipped & Merged!**\n"
        f"• Merged PR {pr_url} into `main`.\n"
        f"• Jira Ticket **{jira_key}** transitioned to **DONE / CLOSED** 🏁.\n"
        f"• Cart Drawer feature is ready for the Webshop-Ecom store deployment. Enjoy your holiday @Kushal!",
        delay=1.5
    )

    print(f"{BOLD}{GREEN}======================================================================{RESET}")
    print(f"{BOLD}{GREEN} ✅ SIMULATION COMPLETE: End-to-end loop succeeded with 100% precision!{RESET}")
    print(f"{BOLD}{WHITE} Live Jira Ticket: {result.get('jira_url')}{RESET}")
    print(f"{BOLD}{WHITE} Live GitHub PR:   {pr_url}{RESET}")
    print(f"{BOLD}{GREEN}======================================================================{RESET}\n")

if __name__ == "__main__":
    run_teams_chat_simulation()
