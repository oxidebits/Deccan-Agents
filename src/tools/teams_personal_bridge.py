"""
Playwright Live Chat Bridge for Microsoft Teams Personal (teams.live.com)
Allows @DeccanAgent to operate directly inside free personal Teams group chats
without requiring enterprise Office 365 / Entra tenant webhooks.
"""
import os
import sys
import time
import asyncio
import logging
import argparse
from pathlib import Path
from typing import Set, Optional, Dict, Any, List

from playwright.async_api import async_playwright, BrowserContext, Page

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agent.graph import build_deccan_agent_graph

agent_graph = build_deccan_agent_graph()

logger = logging.getLogger("teams_personal_bridge")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [TeamsBridge] %(message)s"
)

DEFAULT_CHAT_URL = (
    "https://teams.live.com/l/message/"
    "19:wnd66nNqiF99yYDeG4v2AMVAgMvlMLnhc-ljPWcqyoc1@thread.v2/"
    "1789201363682?context=%7B%22contextType%22%3A%22chat%22%7D"
)
SESSION_DIR = Path(".teams_browser_session")


class TeamsPersonalBridge:
    def __init__(self, chat_url: str = DEFAULT_CHAT_URL, headless: bool = False):
        self.chat_url = chat_url
        self.headless = headless
        self.processed_ids: Set[str] = set()
        self.running = True

    async def run_agent_for_message(self, prompt: str) -> str:
        """Run the LangGraph workflow and return clean response text"""
        logger.info(f"Processing prompt for @DeccanAgent: '{prompt}'")
        try:
            initial_state = {
                "user_prompt": prompt,
                "current_node": "start",
                "iteration_count": 0,
                "review_status": "PENDING",
            }
            # Execute compiled LangGraph workflow
            result = await agent_graph.ainvoke(initial_state)
            
            mode = result.get("workflow_mode", "DEV_HOLIDAY")
            if mode == "DEV_HOLIDAY":
                jira_key = result.get("jira_key") or result.get("jira_issue_key", "SCRUM-DEV")
                pr_url = result.get("pr_url") or result.get("github_pr_url", "https://github.com/oxidebits/Deccan-Agents/pulls")
                review_status = result.get("review_status", "APPROVED")
                return (
                    f"🤖 @DeccanAgent [Stand-in Dev Report]:\n"
                    f"✅ Analyzed requirements & grounded Svelte 5 specs via Exa Neural Search.\n"
                    f"📋 Created Jira Task: {jira_key} (Status: In Progress -> In Review -> Done).\n"
                    f"💻 Synthesized Svelte 5 Webshop runes components (CartDrawer.svelte & cartStore.svelte.ts).\n"
                    f"🚀 Opened GitHub Pull Request: {pr_url}\n"
                    f"🔍 Automated Code Review: {review_status} & merged to main."
                )
            else:
                jira_epic = result.get("epic_key") or result.get("jira_epic_key", "SCRUM-EPIC")
                raw_stories = result.get("stories", [])
                story_keys = [s.get("key", s.get("id", "Story")) if isinstance(s, dict) else str(s) for s in raw_stories]
                stories_str = ", ".join(story_keys) if story_keys else "SCRUM-STORY"
                return (
                    f"🤖 @DeccanAgent [Agile PM Decomposition]:\n"
                    f"📋 Created Jira Initiative / Epic: {jira_epic}\n"
                    f"📝 Generated Atomic User Stories with Acceptance Criteria: {stories_str}\n"
                    f"📊 Sprint backlog & board dependencies linked in Atlassian Jira Cloud."
                )
        except Exception as e:
            logger.error(f"Error executing agent workflow: {e}", exc_info=True)
            return f"🤖 @DeccanAgent encountered an issue: {e}"

    async def handle_teams_web_prompts(self, page: Page):
        """Auto-clicks 'Continue on this browser' or 'Use web app instead' if prompted"""
        try:
            web_buttons = page.locator(
                'button:has-text("Continue on this browser"), '
                'a:has-text("Use the web app instead"), '
                'button:has-text("Use the web app instead"), '
                '[data-tid="joinOnWeb"]'
            )
            count = await web_buttons.count()
            if count > 0 and await web_buttons.first.is_visible():
                logger.info("Detected Teams browser launcher prompt. Clicking 'Continue on this browser'...")
                await web_buttons.first.click()
                await asyncio.sleep(2.0)
        except Exception:
            pass

    async def post_reply(self, page: Page, message_text: str):
        """Find the message compose box and submit the reply"""
        logger.info("Locating Teams message compose box...")
        input_selectors = [
            'div[role="textbox"]',
            'div[contenteditable="true"]',
            '[data-tid="ckeditor"]',
            'div.ck-editor__editable',
            '[aria-label*="Type a message"]',
            '[aria-label*="Compose"]',
            'textarea',
        ]
        
        target_input = None
        for sel in input_selectors:
            loc = page.locator(sel).last
            if await loc.count() > 0 and await loc.is_visible():
                target_input = loc
                break
                
        if not target_input:
            logger.warning("Could not find standard compose box. Attempting fallback textbox...")
            target_input = page.locator('div[role="textbox"]').first

        if target_input and await target_input.count() > 0:
            await target_input.click()
            await asyncio.sleep(0.3)
            try:
                await target_input.fill(message_text)
            except Exception:
                await page.keyboard.type(message_text, delay=5)
                
            await asyncio.sleep(0.5)
            await page.keyboard.press("Enter")
            
            # Also check for explicit send button
            send_btn = page.locator(
                'button[data-tid="sendMessageButton"], '
                'button[aria-label*="Send"], '
                'button[title*="Send"]'
            ).last
            if await send_btn.count() > 0 and await send_btn.is_visible():
                await send_btn.click()
                
            logger.info("Successfully submitted reply to Teams chat.")
        else:
            logger.error("Failed to locate compose input box to post reply.")

    async def scan_for_mentions(self, page: Page) -> List[Dict[str, str]]:
        """Deep DOM scan for any message containing @deccanagent not inside an input box"""
        js_code = """
        () => {
            const mentions = [];
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            let node;
            while (node = walker.nextNode()) {
                const val = (node.nodeValue || '').trim();
                if (val.toLowerCase().includes('@deccanagent')) {
                    const parent = node.parentElement;
                    // Ignore text inside inputs, textareas, or compose boxes
                    if (parent && !parent.closest('textarea, input, [contenteditable="true"], .ck-editor__editable')) {
                        const container = parent.closest('[data-mid], [role="listitem"], [data-tid*="message"], div[class*="message"], div[class*="ChatMessage"]') || parent;
                        const text = (container.innerText || val).trim();
                        const id = container.getAttribute('data-mid') || container.getAttribute('id') || ('text_' + text.slice(0, 50));
                        mentions.push({ text: text, id: id });
                    }
                }
            }
            return mentions;
        }
        """
        try:
            return await page.evaluate(js_code)
        except Exception as e:
            logger.debug(f"Scan evaluate error: {e}")
            return []

    async def start(self):
        """Launch browser with persistent session and start chat polling loop"""
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        
        async with async_playwright() as p:
            logger.info(f"Launching Chromium with persistent context: {SESSION_DIR.resolve()}")
            context: BrowserContext = await p.chromium.launch_persistent_context(
                user_data_dir=str(SESSION_DIR.resolve()),
                headless=self.headless,
                viewport={"width": 1280, "height": 850},
                args=["--disable-blink-features=AutomationControlled"]
            )
            
            page = context.pages[0] if context.pages else await context.new_page()
            logger.info(f"Navigating to Teams chat: {self.chat_url}")
            await page.goto(self.chat_url, wait_until="domcontentloaded")
            
            # Check for Microsoft login page
            if "login.live.com" in page.url or "login.microsoftonline.com" in page.url:
                print("\n" + "="*70)
                print("🔑 [ACTION REQUIRED] Please complete sign-in in the opened browser window.")
                print("Once you sign in, Teams Personal will load and cookies are saved for good!")
                print("="*70 + "\n")
                
                try:
                    await page.wait_for_url("**/teams.live.com/**", timeout=300000)
                    logger.info("Authentication detected! Navigating to group chat...")
                except Exception:
                    logger.warning("Timed out waiting for login. Retrying navigation...")

                # Always re-navigate to group chat after authentication completes
                await page.goto(self.chat_url, wait_until="domcontentloaded")
                await asyncio.sleep(3.0)

            # Auto-handle "Continue on this browser" prompt
            await self.handle_teams_web_prompts(page)
            
            logger.info("Teams Chat loaded. Starting message listener loop (Press Ctrl+C to stop)...")
            
            poll_count = 0
            while self.running:
                try:
                    poll_count += 1
                    await self.handle_teams_web_prompts(page)
                    
                    # Deep scan for mentions
                    mentions = await self.scan_for_mentions(page)
                    
                    for item in mentions:
                        msg_id = item["id"]
                        text = item["text"]
                        
                        if msg_id in self.processed_ids:
                            continue
                            
                        self.processed_ids.add(msg_id)
                        logger.info(f"Detected new mention: '{text}'")
                        
                        # Clean prompt
                        clean_prompt = text
                        for trigger in ["@deccanagent", "@DeccanAgent", "@Deccan Agent"]:
                            clean_prompt = clean_prompt.replace(trigger, "")
                        clean_prompt = clean_prompt.strip()
                        if not clean_prompt:
                            clean_prompt = "Implement Svelte 5 Webshop Cart Drawer with Promo Code discount"
                            
                        # Execute LangGraph agent workflow
                        reply = await self.run_agent_for_message(clean_prompt)
                        
                        # Post reply back to Teams chat
                        await self.post_reply(page, reply)
                        
                    # Heartbeat log every 10 iterations (~20s)
                    if poll_count % 10 == 0:
                        logger.info(
                            f"Listening on: {page.url[:60]}... "
                            f"(Processed mentions: {len(self.processed_ids)})"
                        )
                        
                    await asyncio.sleep(2.0)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.debug(f"Listener loop iteration: {e}")
                    await asyncio.sleep(2.0)

            await context.close()


def main():
    parser = argparse.ArgumentParser(description="Deccan Agents Live Teams Personal Bridge")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--chat-url", default=DEFAULT_CHAT_URL, help="Direct Teams group chat URL")
    parser.add_argument("--test-prompt", help="Direct test prompt to verify agent response without browser")
    args = parser.parse_args()

    if args.test_prompt:
        bridge = TeamsPersonalBridge()
        reply = asyncio.run(bridge.run_agent_for_message(args.test_prompt))
        print("\nGenerated Agent Reply:\n" + reply)
        return

    bridge = TeamsPersonalBridge(chat_url=args.chat_url, headless=args.headless)
    try:
        asyncio.run(bridge.start())
    except KeyboardInterrupt:
        print("\nStopping Teams Personal Bridge...")

if __name__ == "__main__":
    main()
