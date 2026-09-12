"""
Seed Webshop-Ecom Scrum Board with Epics, Stories, and Tasks in Active Sprint.
Populates: https://deccanagents.atlassian.net/jira/software/projects/SCRUM/boards/1
"""
import os
import sys
import base64
import requests
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.jira_client import (
    create_epic,
    create_story,
    create_jira_issue,
    transition_jira_issue,
    add_jira_comment,
    _get_server_url,
    _get_auth_headers
)

load_dotenv()

server = _get_server_url()
headers = _get_auth_headers()

def get_active_sprint_id(board_id: int = 1) -> int:
    res = requests.get(f"{server}/rest/agile/1.0/board/{board_id}/sprint", headers=headers)
    if res.status_code == 200:
        for sp in res.json().get("values", []):
            if sp.get("state") == "active":
                return sp.get("id")
    return 2  # Fallback to Sprint 2

def add_issues_to_sprint(sprint_id: int, issue_keys: list):
    res = requests.post(
        f"{server}/rest/agile/1.0/sprint/{sprint_id}/issue",
        headers=headers,
        json={"issues": issue_keys}
    )
    print(f"Added {issue_keys} to Sprint {sprint_id}: HTTP {res.status_code}")

def seed_webshop():
    print("Seeding Webshop-Ecom Scrum Board on Jira Cloud...")
    active_sprint_id = get_active_sprint_id(board_id=1)
    print(f"Active Sprint ID: {active_sprint_id} (SCRUM Sprint 0)")

    # 1. Create Core Epics
    print("\n--- 1. Creating Epics ---")
    epic1 = create_epic(
        summary="Webshop-Ecom: Core Cart & Dynamic Pricing Engine",
        description="Parent epic covering the Svelte 5 cart drawer, runes reactivity, and dynamic coupon discount engine."
    )
    print(f"Created Epic 1: {epic1['key']} - {epic1['summary']}")

    epic2 = create_epic(
        summary="Customer Checkout & Multi-Currency Payment Gateway",
        description="Parent epic covering checkout flow, Stripe/Razorpay integration, and order fulfillment."
    )
    print(f"Created Epic 2: {epic2['key']} - {epic2['summary']}")

    # 2. Create User Stories across Sprint Columns
    print("\n--- 2. Creating User Stories & Tasks ---")
    
    # Story A: To Do (Catalog filtering)
    story_a = create_story(
        summary="[Catalog] Svelte 5 Instant Product Filtering by Price and Category",
        description="As a shopper, I want to filter products by category and price range with instant reactivity without full-page reloads.",
        epic_key=epic1["key"],
        story_points=3,
        acceptance_criteria=[
            "Given a catalog with 50+ items, when price slider changes, then product grid updates within 50ms using Svelte 5 $derived.",
            "Category filters support multi-select pills with count badges."
        ]
    )
    print(f"Created Story A: {story_a['key']} (To Do)")

    # Story B: To Do (WebSocket Inventory)
    story_b = create_story(
        summary="[Inventory] Real-time Stock Depletion Check via WebSockets",
        description="As a shopper, I want real-time notifications when an item in my cart is low in stock so that I can checkout before it sells out.",
        epic_key=epic1["key"],
        story_points=5,
        acceptance_criteria=[
            "Given an item in cart with <= 3 remaining units, display 'Only 3 left!' alert badge.",
            "If stock reaches 0 during checkout session, disable proceed button and offer waitlist notify."
        ]
    )
    print(f"Created Story B: {story_b['key']} (To Do)")

    # Story C: In Progress (Checkout Payment Gateway)
    story_c = create_story(
        summary="[Checkout] Stripe & Razorpay Multi-Currency Payment Gateway",
        description="As an international customer, I want to checkout using my preferred local currency (USD, EUR, INR) via Stripe or Razorpay.",
        epic_key=epic2["key"],
        story_points=5,
        acceptance_criteria=[
            "Supports 3DS2 secure authorization flows.",
            "Handles webhook asynchronous payment confirmations with idempotency keys."
        ]
    )
    transition_jira_issue(story_c["key"], "In Progress")
    add_jira_comment(story_c["key"], "Agent started work on payment gateway webhook handlers.")
    print(f"Created Story C: {story_c['key']} (In Progress)")

    # Story D: In Review (Dynamic Promo Code Validation)
    story_d = create_story(
        summary="[Discount] Dynamic Promo Code Validation with 15% OFF Coupon",
        description="As a buyer, I want to enter coupon code 'DECCAN15' at cart checkout to receive an instant 15% discount on eligible subtotal items.",
        epic_key=epic1["key"],
        story_points=3,
        acceptance_criteria=[
            "Valid coupon codes apply discount instantly to subtotal.",
            "Invalid or expired codes display clear red inline error banner.",
            "Discounts cannot reduce shipping fees below minimum."
        ]
    )
    transition_jira_issue(story_d["key"], "In Progress")
    transition_jira_issue(story_d["key"], "In Review")
    add_jira_comment(story_d["key"], "PR #3 open for review: Implemented promo code validation regex and subtotal reduction.")
    print(f"Created Story D: {story_d['key']} (In Review)")

    # Story E: Done (Svelte 5 Runes State Store)
    story_e = create_story(
        summary="[Cart] Svelte 5 Runes Reactive State Store for Webshop Items",
        description="As a frontend developer, I want a unified cartStore using Svelte 5 $state and $derived runes to manage cart items and subtotal reactivity.",
        epic_key=epic1["key"],
        story_points=2,
        acceptance_criteria=[
            "cartStore export uses Svelte 5 $state rune.",
            "Total calculation uses $derived rune.",
            "Unit tests verify item addition, quantity increment, and item removal."
        ]
    )
    transition_jira_issue(story_e["key"], "In Progress")
    transition_jira_issue(story_e["key"], "In Review")
    transition_jira_issue(story_e["key"], "Done")
    add_jira_comment(story_e["key"], "Code merged and released via PR #1. Feature tested and verified.")
    print(f"Created Story E: {story_e['key']} (Done)")

    # 3. Add all new stories + SCRUM-18 + SCRUM-19 to Active Sprint
    new_keys = [story_a["key"], story_b["key"], story_c["key"], story_d["key"], story_e["key"], "SCRUM-18", "SCRUM-19"]
    add_issues_to_sprint(active_sprint_id, new_keys)

    print("\nSeeding Complete!")
    print(f"Check your board: https://deccanagents.atlassian.net/jira/software/projects/SCRUM/boards/1")

if __name__ == "__main__":
    seed_webshop()
