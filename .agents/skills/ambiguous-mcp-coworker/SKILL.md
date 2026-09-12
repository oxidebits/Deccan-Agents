---
name: ambiguous-mcp-coworker
description: >-
  Build, scaffold, and integrate autonomous AI coworkers with Ambiguous AI via the
  Model Context Protocol (MCP) or CLI. Use this skill whenever implementing tools,
  schemas, workflows, or handlers across Ambiguous apps (Docs, Mail, Chat, Sheets, CRM, Calendar).
---

# Ambiguous AI & MCP Coworker Skill

> [!IMPORTANT]
> **CRITICAL OPERATIONAL GUARDRAILS (From Real Dry Runs):**
> 1. **Clean Stdio Transport:** All logs, prints, and diagnostics MUST go to `stderr`. `stdout` is strictly reserved for JSON-RPC.
> 2. **MCP 1.x vs 2.x Dual Import:** MCP 2.x renamed `FastMCP` to `MCPServer`. Always use the dual import fallback below.
> 3. **Defensive Mock Data Access:** Seed data `sheets` and `rows` can be lists or dicts. Never call `.get()` directly on a list.
> 4. **Functional Coding & Zero Workarounds:** Write pure deterministic handlers with defensive fallbacks. No placeholder stubs.
> 5. **Traceability & Git Commits:** Log work in `EXECUTION_LOG.md` and commit after every user message with simple, descriptive messages.

---

## 1. Context Window Pre-Flight Protocol (Data & JSON Files)

> [!CAUTION]
> **DO NOT load entire raw JSON datasets (>150 lines) into the LLM context window.**
> - **Pre-flight Check:** Run `wc -l seed_data.json` or `ls -lh seed_data.json` via shell.
> - **Inspect Keys:** Run `jq 'keys' seed_data.json` to inspect top-level collections (`inbox`, `sheets`, `crm_leads`, `calendar_events`, `chat_channels`).
> - **Slice What You Need:** Extract only target items, e.g. `jq '.sheets[] | select(.title=="Competitor_Matrix_Q3_2026")' seed_data.json`.
> - **Token Estimate:** 1 token ≈ 4 characters. A 500-line JSON dump costs ~3,500 tokens of context.

---

## 2. Multi-App Coworker Architecture

```
 ┌─────────────────────────────────────────────────────────────┐
 │                    Ambiguous AI Workspace                   │
 │   [Docs]  [Sheets]  [Mail]  [Chat]  [CRM]  [Calendar]       │
 └──────────────────────────────┬──────────────────────────────┘
                                │ stdio JSON-RPC
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                FastMCP / Stdio Coworker Server              │
 │   - Invocation: @Massy mentions, /slash commands, webhooks  │
 │   - Tools: Mail reader, Doc writer, CRM/Sheet updater       │
 │   - Fallback: Offline seed_data.json for zero-fail demos    │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
                       [OpenAI / Exa APIs]
```

---

### 2.1 Foundational Invocation Patterns: `@mentions`, `/commands`, & Ambient Listeners

To fulfill the hackathon mandate (*"Agents leaving the chatbox"*), coworkers must respond to native workplace triggers rather than a detached chat input:

1. **`@mentions` in Workplace Chat & Documents (`@Massy`):**
   - In Ambiguous Chat, Slack, or doc comments, typing `@Massy` activates the agent.
   - The host platform passes the full conversation thread, sender persona, and document metadata into the prompt.
   - Example prompt: `@Massy triage this inbound email from Acme Retail and prepare our Deal Desk doc.`

2. **Slash Commands (`/massy`, `/triage`, `/brief`):**
   - Quick, predictable command execution inside workplace message inputs.
   - Maps directly to the composite orchestrator tool: `execute_coworker_workflow(target_entity, task)`.

3. **Ambient & Event-Driven Listeners (No Manual Typing):**
   - **Inbound Mail:** Polling `get_unread_inbound_emails()` or webhook dispatch wakes the coworker when new partner/customer emails arrive.
   - **Spreadsheet Updates:** When rows are added to `Competitor_Matrix_Q3_2026`, coworker reads headers via `get_sheet_data()` and writes enrichment back via `update_ambiguous_sheet()`.
   - **Calendar Watchers:** Monitors upcoming events to schedule debrief holds via `schedule_calendar_hold()`.

4. **CopilotKit In-App Foundation (For Web Applications):**
   - If embedding the coworker into a custom web dashboard, use CopilotKit:
     - `useCopilotReadable({ description: "Current Sheet Rows", value: sheetData })` gives the agent instant awareness of what the user is looking at.
     - `useCopilotAction({ name: "updateSheetRow", ... })` binds agent decisions directly to frontend state.
     - `<CopilotTextarea />` provides inline `@Massy` completions directly inside text inputs where users type.

---

## 3. Production MCP Coworker Implementation

### Python (`FastMCP` with Dual MCP 1.x/2.x Import & Dual-Mode Fallback)

```python
import json
import os
import sys
from pathlib import Path

# Dual import handles both MCP 1.x (FastMCP) and MCP 2.x (MCPServer)
try:
    from mcp.server.fastmcp import FastMCP
except (ImportError, ModuleNotFoundError):
    from mcp.server import MCPServer as FastMCP

mcp = FastMCP("AmbiguousCoworker")

# Stdio rule: stderr only
def log(msg: str):
    sys.stderr.write(f"[AMBIGUOUS COWORKER] {msg}\n")
    sys.stderr.flush()

# Multi-path seed data loader
def load_mock_data() -> dict:
    candidates = [
        Path.cwd() / "seed_data.json",
        Path(__file__).parent / "seed_data.json",
        Path(__file__).resolve().parent.parent / "seed_data.json",
    ]
    for p in candidates:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}

MOCK_DATA = load_mock_data()

# ----------------- 6 App Tools -----------------

@mcp.tool()
def get_unread_inbound_emails() -> str:
    """Reads unread enterprise inquiries from Ambiguous Mail."""
    emails = MOCK_DATA.get("inbox", [])
    unread = [e for e in emails if e.get("status") == "unread"]
    return json.dumps(unread, indent=2)

@mcp.tool()
def create_ambiguous_doc(title: str, markdown_content: str, folder: str = "Research") -> str:
    """Creates a formatted intelligence dossier in Ambiguous Docs."""
    slug = title.lower().replace(" ", "-").replace("/", "-")
    log(f"Created doc '{title}' in folder '{folder}' ({len(markdown_content)} chars)")
    return f"[Success] Document '{title}' published to Ambiguous Docs ({folder}). Link: https://ambiguous.app/docs/{slug}"

@mcp.tool()
def update_crm_record(company: str, deal_stage: str, arr_estimate: int = 0, notes: str = "") -> str:
    """Updates deal pipeline state in Ambiguous CRM."""
    log(f"CRM Lead Updated: {company} | Stage: {deal_stage} | ARR: ${arr_estimate:,}")
    return f"[Success] CRM record updated for {company}: Status set to '{deal_stage}', ARR: ${arr_estimate:,}."

def _find_sheet(sheet_name: str) -> dict:
    sheets = MOCK_DATA.get("sheets", [])
    if isinstance(sheets, list):
        for s in sheets:
            if str(s.get("title", "")).lower() == sheet_name.lower() or str(s.get("id", "")).lower() == sheet_name.lower():
                s.setdefault("name", s.get("title"))
                return s
        new_sheet = {"id": f"sheet_{sheet_name.lower()}", "title": sheet_name, "name": sheet_name, "headers": ["Company", "Risk_Rating"], "rows": []}
        sheets.append(new_sheet)
        return new_sheet
    elif isinstance(sheets, dict):
        return sheets.setdefault(sheet_name, {"title": sheet_name, "name": sheet_name, "headers": ["Company", "Risk_Rating"], "rows": []})
    return {"title": sheet_name, "name": sheet_name, "headers": ["Company", "Risk_Rating"], "rows": []}

@mcp.tool()
def get_sheet_data(sheet_name: str) -> str:
    """Reads rows and columns from an Ambiguous Sheet."""
    sheet = _find_sheet(sheet_name)
    log(f"Read sheet '{sheet_name}': {len(sheet.get('rows', []))} rows")
    return json.dumps(sheet, indent=2)

@mcp.tool()
def update_ambiguous_sheet(sheet_name: str, row_identifier: str, column_name: str, new_value: str) -> str:
    """Updates a cell or row in an Ambiguous Sheet (e.g. Risk_Rating, Status)."""
    sheet = _find_sheet(sheet_name)
    headers = sheet.setdefault("headers", ["Company", "Risk_Rating"])
    if column_name not in headers:
        headers.append(column_name)
    col_idx = headers.index(column_name)

    rows = sheet.setdefault("rows", [])
    updated = False
    for r in rows:
        if isinstance(r, list):
            if len(r) > 0 and str(r[0]).lower() == row_identifier.lower():
                while len(r) <= col_idx:
                    r.append("")
                r[col_idx] = new_value
                updated = True
                break
        elif isinstance(r, dict):
            if str(r.get("company", "")).lower() == row_identifier.lower():
                r[column_name] = new_value
                updated = True
                break

    if not updated:
        new_row = [row_identifier] + [""] * (len(headers) - 1)
        new_row[col_idx] = new_value
        rows.append(new_row)

    log(f"Sheet '{sheet_name}' Updated: row='{row_identifier}', {column_name}='{new_value}'")
    return f"[Success] Updated sheet '{sheet_name}': Set {column_name}='{new_value}' for row '{row_identifier}'."

@mcp.tool()
def schedule_calendar_hold(title: str, proposed_slot: str, attendees: list[str] = None) -> str:
    """Reserves tentative meeting slots in Ambiguous Calendar."""
    attendee_list = attendees or []
    log(f"Calendar hold placed: {title} at {proposed_slot} with {attendee_list}")
    return f"[Success] Tentative hold '{title}' placed on Ambiguous Calendar for {proposed_slot}."

@mcp.tool()
def broadcast_team_notification(channel: str, message: str, action_url: str = None) -> str:
    """Posts high-priority notification cards to Ambiguous Chat with 1-click approvals."""
    action_str = f" [Action Link: {action_url}]" if action_url else ""
    log(f"Chat Notification #{channel}: {message}{action_str}")
    return f"[Success] Notification card posted to #{channel}: {message}{action_str}"

if __name__ == "__main__":
    log("Ambiguous Coworker FastMCP server running on stdio...")
    mcp.run()
```

---

### TypeScript (`@modelcontextprotocol/sdk`)

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import * as fs from "fs";
import * as path from "path";

const seedPath = path.resolve(process.cwd(), "seed_data.json");
const mockData = fs.existsSync(seedPath) ? JSON.parse(fs.readFileSync(seedPath, "utf-8")) : {};

const server = new Server({ name: "ambiguous-coworker", version: "1.0.0" }, { capabilities: { tools: {} } });

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    { name: "get_unread_inbound_emails", description: "Reads unread emails from Ambiguous Mail", inputSchema: { type: "object", properties: {} } },
    { name: "create_ambiguous_doc", description: "Publishes markdown dossier to Ambiguous Docs", inputSchema: { type: "object", properties: { title: { type: "string" }, markdown_content: { type: "string" }, folder: { type: "string", default: "Research" } }, required: ["title", "markdown_content"] } },
    { name: "update_crm_record", description: "Updates pipeline deal stage in Ambiguous CRM", inputSchema: { type: "object", properties: { company: { type: "string" }, deal_stage: { type: "string" }, arr_estimate: { type: "number" }, notes: { type: "string" } }, required: ["company", "deal_stage"] } },
    { name: "get_sheet_data", description: "Reads Ambiguous Sheet rows", inputSchema: { type: "object", properties: { sheet_name: { type: "string" } }, required: ["sheet_name"] } },
    { name: "update_ambiguous_sheet", description: "Updates cells/ratings in Ambiguous Sheet", inputSchema: { type: "object", properties: { sheet_name: { type: "string" }, row_identifier: { type: "string" }, column_name: { type: "string" }, new_value: { type: "string" } }, required: ["sheet_name", "row_identifier", "column_name", "new_value"] } },
    { name: "schedule_calendar_hold", description: "Reserves meeting holds in Ambiguous Calendar", inputSchema: { type: "object", properties: { title: { type: "string" }, proposed_slot: { type: "string" }, attendees: { type: "array", items: { type: "string" } } }, required: ["title", "proposed_slot"] } },
    { name: "broadcast_team_notification", description: "Posts notification cards to Ambiguous Chat", inputSchema: { type: "object", properties: { channel: { type: "string" }, message: { type: "string" }, action_url: { type: "string" } }, required: ["channel", "message"] } },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params as { name: string; arguments: any };
  switch (name) {
    case "get_unread_inbound_emails":
      return { content: [{ type: "text", text: JSON.stringify(mockData.inbox || [], null, 2) }] };
    case "create_ambiguous_doc":
      return { content: [{ type: "text", text: `[Success] Doc '${args.title}' created.` }] };
    case "update_crm_record":
      return { content: [{ type: "text", text: `[Success] CRM record updated for ${args.company}: Stage='${args.deal_stage}'.` }] };
    case "get_sheet_data":
      return { content: [{ type: "text", text: JSON.stringify(mockData.sheets || [], null, 2) }] };
    case "update_ambiguous_sheet":
      return { content: [{ type: "text", text: `[Success] Sheet '${args.sheet_name}' row '${args.row_identifier}' set ${args.column_name}='${args.new_value}'.` }] };
    case "schedule_calendar_hold":
      return { content: [{ type: "text", text: `[Success] Hold '${args.title}' scheduled for ${args.proposed_slot}.` }] };
    case "broadcast_team_notification":
      return { content: [{ type: "text", text: `[Success] Notification posted to #${args.channel}: ${args.message}` }] };
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

async function run() {
  await server.connect(new StdioServerTransport());
  console.error("Ambiguous MCP Coworker running on stdio");
}
run().catch(console.error);
```

---

## 4. Tool Contract & Schema Evaluation under Harness

When an autonomous coworker is invoked via Model Context Protocol, the evaluation harness validates tool execution against three strict criteria:

### A. Defensive Parameter & State Resilience
Tools must accept loose or partial parameters without throwing unhandled exceptions. If the LLM generates an optional field as `None` or an empty string, defaults must take over gracefully:
```python
# Harness Contract Rule: Type defensive fallbacks
@mcp.tool()
def schedule_calendar_hold(title: str, proposed_slot: str, attendees: list[str] = None) -> str:
    attendee_list = attendees or []  # Defend against None attendee lists from LLM
    ...
```

### B. Stdio Transport Purity Under High-Speed Evals
The harness tests stdio isolation by running automated tool calls in tight loops. 
- **Rule:** `stdout` is strictly reserved for JSON-RPC messages. 
- Any stray `print()` statement will corrupt the stdio pipe and cause the MCP client to drop the connection (`JSONRPCParseException`). 
- Always route internal traces and diagnostics to `sys.stderr`.

### C. LangSmith Tool-Execution Trace Propagation
When tools run within an active LangGraph trace, LangSmith automatically records:
1. Tool name and input argument dictionary
2. Execution latency (e.g., `< 50ms` for seed data access)
3. Return payload structure and token size

---

## 5. Verification Checklist

- [ ] Inspect `seed_data.json` size (`wc -l seed_data.json`) before loading into prompts.
- [ ] Verify Stdio transport handshake:
  ```bash
  npx --yes @modelcontextprotocol/inspector uv run python server.py
  ```
- [ ] Run backend unit tests:
  ```bash
  uv run pytest tests/test_server.py -v
  ```
- [ ] Run the 4-Pillar Evaluation Harness:
  ```bash
  uv run python -m harness.eval_runner
  ```
