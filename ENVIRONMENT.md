# Environment & Framework Reference

> [!IMPORTANT]
> **META-INSTRUCTION FOR AGENTS & LLMS:** Whenever you read this file, you MUST actively inspect the environment and update its data, tool versions, commands, links, and system notes as of that day to prevent stale context.

This file provides AI coding agents, LLMs, and developers with instant awareness of installed runtimes, tooling versions, quickstart scaffolding commands, inspection/meta commands for edge cases, stack requirements, and high-signal documentation links (including `llms.txt`).

---

## 1. System Environment & Installed Tooling

| Tool / Runtime | Installed Version | Quick Verification Command | Edge-Case Meta / Help Command |
| :--- | :--- | :--- | :--- |
| **Node.js** | `v24.18.0` | `node -v` | `node --help`, `node --v8-options` |
| **npm** | `11.16.0` | `npm -v` | `npm help <command>`, `npm doctor`, `npm ls -g --depth=0` |
| **pnpm** | `11.15.1` | `pnpm -v` | `pnpm help`, `pnpm store status`, `pnpm doctor` |
| **TypeScript** | `7.0.2` | `tsc -v` | `tsc --help`, `tsc --all`, `tsc --showConfig` |
| **Python** | `3.14.7` | `python --version` | `python -m pip list`, `python -m site`, `which python` |
| **uv** | `0.12.3` | `uv --version` | `uv --help`, `uv venv --help`, `uv pip install --help`, `uv cache clean` |
| **Git** | `2.55.0` | `git --version` | `git status -s`, `git help <cmd>`, `git config --list --show-origin` |

> [!TIP]  
> Use `uv pip install <package>` or `uv venv` for instantaneous Python virtual environments and dependency resolution during the hackathon.

---

## 2. Full-Stack Requirements Breakdown (UI, Web, Systems & Harnesses)

To build a winning hackathon project (e.g. targeting the **DGX Spark** via Ambiguous AI and **Mac mini** 1st place), here is what is required across each technological layer:

### A. System & Protocol Layer (The Core Agent Backbone)
- **Model Context Protocol (MCP SDK):**
  - `@modelcontextprotocol/sdk` (TypeScript) or `mcp` / `FastMCP` (Python).
  - Handles JSON-RPC communication over standard I/O (`stdio`) or Server-Sent Events (`sse`).
  - **Critical requirement:** `stdout` is strictly reserved for JSON-RPC messages; all diagnostic logs must stream to `stderr`.
- **Process & Test Harness:**
  - `@modelcontextprotocol/inspector` (`npx @modelcontextprotocol/inspector`): An interactive local web harness to test and verify tool schemas, inputs, and outputs without needing a full client.

### B. Workspace & Coworker Layer (Ambiguous AI)
- **Integration Harness:**
  - Ambiguous CLI or direct MCP server registration in the Ambiguous client.
  - Exposes coworker capabilities: reading/writing Docs, updating CRM leads, listening for `@mentions` in Chat, and managing Calendar events.
- **Identity & State:**
  - Dedicated agent persona (name, role, avatar).
  - Shared context store or memory cache (e.g., SQLite / in-memory dictionary) for conversational continuity.

### C. Intelligence & Grounding Layer (Models & Search)
- **LLM Reasoning Engine:**
  - `openai` SDK (`gpt-4o`, `gpt-4o-mini`, or o-series reasoning models).
  - Structured Outputs / JSON Schema mode (`client.beta.chat.completions.parse`) for bulletproof tool parameter extraction.
- **Real-Time Web Intelligence:**
  - `exa-py` / `exa-js`: Neural search, URL content crawling, and highlight extraction to ground agent actions in live web facts.

### D. Asynchronous Jobs & Workflow Harness (Trigger.dev / Background Tasks)
- **Async Execution Engine:**
  - `trigger.dev` (v3): Manages long-running research jobs, retries, and scheduled intervals outside the main HTTP/stdio loop so requests don't time out.

### E. Frontend & UI Layer (Web, Dashboards, In-App Coworker Feed)
- **Framework:**
  - Svelte 5 with Runes (`$state`, `$derived`, `$effect`) for fine-grained reactivity and minimal overhead.
- **Iconography & Styling:**
  - `lucide-svelte` icons + Tailwind CSS.
  - High-contrast dark mode, clean typography, responsive layout for crisp 1080p demo recordings.

---

## 3. Meta-Commands & Edge-Case Troubleshooting Runbook

When CLI commands fail, arguments are unknown, or dependency conflicts occur, use these meta commands directly:

### Python & `uv` Edge Cases
```bash
# Check full uv capabilities and subcommands:
uv --help
uv pip --help
uv venv --help

# Rebuild / clean uv cache if network or cache errors occur:
uv cache clean

# Verify active Python environment and sys.path:
python -c "import sys; print(sys.executable); print(sys.path)"

# List installed packages in current Python env:
uv pip list || python -m pip list
```

### Node / npm / pnpm / TypeScript Edge Cases
```bash
# Inspect tsconfig resolution in real time:
tsc --showConfig

# Detailed help for specific npm commands:
npm help run
npm help install

# Check global packages installed:
npm ls -g --depth=0

# Diagnose node/npm environment issues:
npm doctor
```

### Model Context Protocol (MCP) Edge Cases
```bash
# Test & inspect any stdio MCP server interactively:
npx @modelcontextprotocol/inspector <command-to-run-server>

# Verify JSON-RPC stdout behavior (ensure stderr has logs, stdout has clean JSON):
python server.py 2> debug.log
```

---

## 4. LLM-Optimized Docs (`llms.txt`) & Key API References

Use these direct documentation endpoints to grab concise, clean documentation for prompt injection or quick lookups:

| Service / Framework | LLMs.txt / API Direct Endpoint | Primary Documentation URL |
| :--- | :--- | :--- |
| **LangSmith (Python)** | [https://docs.langchain.com/langsmith/python/llms.txt](https://docs.langchain.com/langsmith/python/llms.txt) | [docs.langchain.com/langsmith](https://docs.langchain.com/langsmith) |
| **LangSmith (Smith API)** | [https://docs.langchain.com/langsmith/smith-api/llms.txt](https://docs.langchain.com/langsmith/smith-api/llms.txt) | [docs.langchain.com/langsmith](https://docs.langchain.com/langsmith) |
| **LangGraph (Python)** | [https://docs.langchain.com/oss/python/langgraph/llms.txt](https://docs.langchain.com/oss/python/langgraph/llms.txt) | [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/) |
| **LangChain (Python)** | [https://docs.langchain.com/oss/python/langchain/llms.txt](https://docs.langchain.com/oss/python/langchain/llms.txt) | [python.langchain.com](https://python.langchain.com/) |
| **LangChain (Global)** | [https://docs.langchain.com/llms.txt](https://docs.langchain.com/llms.txt) | [docs.langchain.com](https://docs.langchain.com/) |
| **Exa AI** | [https://exa.ai/llms.txt](https://exa.ai/llms.txt) | [docs.exa.ai](https://docs.exa.ai) |
| **Model Context Protocol (MCP)** | [https://modelcontextprotocol.io/llms.txt](https://modelcontextprotocol.io/llms.txt) | [modelcontextprotocol.io](https://modelcontextprotocol.io) |
| **OpenAI API** | [https://platform.openai.com/docs/llms.txt](https://platform.openai.com/docs/llms.txt) | [platform.openai.com/docs](https://platform.openai.com/docs) |
| **OpenRouter** | [https://openrouter.ai/docs/llms.txt](https://openrouter.ai/docs/llms.txt) | [openrouter.ai/docs](https://openrouter.ai/docs) |
| **Trigger.dev** | [https://trigger.dev/llms.txt](https://trigger.dev/llms.txt) | [trigger.dev/docs](https://trigger.dev/docs) |
| **shadcn-svelte** | [https://shadcn-svelte.com/llms.txt](https://shadcn-svelte.com/llms.txt) | [shadcn-svelte.com](https://shadcn-svelte.com/) |
| **Svelte 5** | [https://svelte.dev/llms.txt](https://svelte.dev/llms.txt) (full: [llms-full.txt](https://svelte.dev/llms-full.txt)) | [svelte.dev/docs](https://svelte.dev/docs) |
| **Vite** | [https://vite.dev/llms.txt](https://vite.dev/llms.txt) | [vite.dev](https://vite.dev) |

---

## 5. Likely Hackathon Frameworks & Quick-Scaffold Commands

### A. Model Context Protocol (MCP) Server

#### Node / TypeScript MCP Server:
```bash
# Initialize Node project
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node tsx
```

#### Python FastMCP Server:
```bash
# Instant venv with uv
uv venv .venv && source .venv/bin/activate
uv pip install "mcp[cli]"
# Run inspector / test UI:
npx @modelcontextprotocol/inspector <command-to-run-server>
```

---

### B. Ambiguous AI CLI & Coworker Onboarding

```bash
# Ambiguous CLI commands and flags:
npx ambiguous --help || pip install ambiguous
```

---

### C. CopilotKit CLI & Official Quick-Start Onboarding

The official CopilotKit CLI supports direct workspace connection and interactive agent onboarding:

```bash
# Direct onboarding run (from official docs/dashboard):
npx --yes copilotkit@latest onboard start --run <run-id>

# Alternative interactive project init:
npx --yes copilotkit@latest init

# Check CLI commands:
npx --yes copilotkit@latest --help
```

---

### D. Frontend / In-App Copilot UI

#### Option 1: Svelte 5 + Lucide Icons (Recommended for performance & clean reactive runes)
Svelte 5's new reactivity runes (`$state`, `$derived`, `$effect`) provide lightweight and lightning-fast reactivity for live streaming agent state.

```bash
# Method A: Official Svelte CLI (sv)
npx sv create frontend
cd frontend
# Add official add-ons (Tailwind, etc.):
npx sv add tailwindcss
npx sv add ai-tools || true
npm install lucide-svelte

# Method B: Fast Vite scaffold
npx -y create-vite@latest frontend --template svelte-ts
cd frontend
npm install lucide-svelte

# Single-Command Scaffolding for Agent Dashboards (shadcn-svelte):
npx --yes shadcn-svelte@latest init
npx --yes shadcn-svelte@latest add card badge button tabs scroll-area separator dialog
```

*Lucide Svelte Usage Example (`+page.svelte` or component):*
```svelte
<script lang="ts">
  import { Bot, Sparkles, Send, CheckCircle2 } from 'lucide-svelte';
  let isThinking = $state(false);
</script>

<div class="flex items-center gap-2">
  <Bot class="w-5 h-5 text-indigo-500" />
  <span>AI Coworker</span>
  {#if isThinking}
    <Sparkles class="w-4 h-4 animate-spin text-amber-400" />
  {/if}
</div>
```

#### Option 2: React (CopilotKit native UI components)
If utilizing CopilotKit's pre-packaged `<CopilotSidebar />` or `<CopilotChat />`:
```bash
npx -y create-vite@latest frontend --template react-ts
cd frontend
npm install @copilotkit/react-core @copilotkit/react-ui lucide-react
```

---

### E. Exa Search Quick Install

```bash
# Python
uv pip install exa-py

# Node / TypeScript
npm install exa-js
```

---

### F. Trigger.dev Background Jobs (v3)

```bash
# Initialize Trigger.dev in project
npx --yes trigger.dev@latest init
# Start dev worker
npx --yes trigger.dev@latest dev
```

---

## 6. Environment Variables Checklist (`.env`)

Store these in your `.env` (make sure `.env` is in `.gitignore`):

```bash
# Core LLM & Gateway
OPENAI_API_KEY=
OPENROUTER_API_KEY=

# Search & Retrieval
EXA_API_KEY=

# Background Tasks & Auth
TRIGGER_SECRET_KEY=
AUTH0_DOMAIN=
AUTH0_CLIENT_ID=

# Ambiguous AI Workspace Connection
AMBIGUOUS_API_KEY=
AMBIGUOUS_WORKSPACE_ID=
```
