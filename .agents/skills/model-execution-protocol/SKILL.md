---
name: model-execution-protocol
description: >-
  Strict operational protocol, engineering standards, and execution guidelines for models
  and AI agents working in this repository. Use this skill to govern thinking vs doing balance,
  functional programming standards, per-turn git commits, traceability logging, and context budgeting.
---

# Autonomous Model Execution & Engineering Protocol

> [!IMPORTANT]
> **MANDATORY OPERATIONAL GUARDRAILS FOR ALL AGENTS & MODELS:**
> Every AI agent or LLM operating in this repository must strictly adhere to the following 6 core operating principles. Failure to follow these rules degrades repository integrity.

---

## 1. Per-Turn Git Hygiene & Understandable Commits

- **Rule:** For **every user message** or completed unit of work, execute a git commit before returning your final response.
- **Commit Format:** Use simple, understandable, standard conventional commit messages:
  - `feat: <clear description of new capability>`
  - `fix: <clear description of bug or issue resolved>`
  - `docs: <clear description of documentation or skill updated>`
  - `test: <clear description of test added or verified>`
  - `refactor: <clear description of clean code improvement>`
- **No Vague Messages:** Avoid commits like `wip`, `update`, `changes`, or `fixed stuff`. State precisely what changed in plain language.

---

## 2. Balanced Thinking vs. Doing (Pragmatic Execution Ratio)

Agents must strike a disciplined balance between deliberation and execution:

| Anti-Pattern 1: Analysis Paralysis (Overthinking) | Anti-Pattern 2: The Hack / Corner-Cutter (Workarounds) | The Golden Standard: Pragmatic Execution |
| :--- | :--- | :--- |
| • Burns thousands of tokens researching obvious facts<br>• Writes multi-page theoretical essays<br>• Asks unnecessary questions instead of checking code<br>• Hesitates to take action | • Writes brittle workarounds or monkey-patches<br>• Leaves `TODO`, `# placeholder`, or fake mocks<br>• Ignores edge cases to produce quick fake passes<br>• Silently swallows errors with bare `except:` | • Quickly checks ground truth (`wc -l`, `jq`, `view_file`)<br>• Formulates direct, production-grade architecture<br>• Writes clean, robust code without detours<br>• Verifies against tests/compilers immediately |

**Token Budget Rule:** Spend $\le 20\%$ of effort analyzing ground truth, $\ge 60\%$ implementing robust logic, and $\ge 20\%$ validating with tests.

---

## 3. Functional Programming Practices & Craftsmanship

All code written by agents must adhere to clean functional principles:
1. **Pure Functions & Determinism:** Write functions with explicit inputs and outputs. Avoid mutating global variables or hidden state.
2. **State Immutability:** In state machines (e.g., LangGraph StateGraph, Svelte state handlers), return new state copies/dictionaries rather than modifying objects in place unpredictably.
3. **Explicit Typing & Defensive Defaults:**
   - Python: Use type hints (`def func(name: str, options: dict | None = None) -> list[str]:`).
   - TypeScript: Use strict interfaces/types; avoid `any`.
   - Always guard against `None` / `undefined` when reading external API or LLM outputs:
     ```python
     # Correct: Defensive functional fallback
     attendees = list(raw_input.get("attendees") or [])
     ```
4. **Zero Stub / Zero Workaround Policy:** Implement the full, functional logic. Do not leave stubbed placeholders or shortcuts. Get the job done correctly.

---

## 4. Live Traceability Logging (`EXECUTION_LOG.md`)

- **Rule:** As the model performs actions, it must maintain a structured audit trail in [EXECUTION_LOG.md](file:///Users/gaikwad/Desktop/skills/EXECUTION_LOG.md).
- **Log Entry Schema:**
  ```markdown
  ### [YYYY-MM-DD HH:MM] — <Task Title>
  - **Goal:** <One-sentence user objective>
  - **Files Touched:** <Clickable list of files modified/created>
  - **Key Decisions:** <Technical decisions made, avoiding workarounds>
  - **Verification:** <Command run and result: pass/fail>
  - **Commit:** `<git commit hash> - <commit message>`
  ```
- Keep the log concise, high-signal, and chronological. This enables human collaborators and subsequent models to instantly understand project trajectory.

---

## 5. Context Window Pre-Flight Protocol (Token Efficiency)

> [!CAUTION]
> **NEVER dump raw, unbudgeted files (>100 lines) into the context window.**
- **Check File Dimensions First:** Run `wc -l <file>` or `ls -lh <file>` via shell.
- **Inspect JSON Keys First:** Run `jq 'keys' <file>` to understand schemas before reading contents.
- **Slice Target Slices:** Use `jq` filters or line ranges (`view_file` with `StartLine`/`EndLine`) rather than loading full multi-megabyte payloads.
- **Rule of Thumb:** 1 token ≈ 4 characters. A 500-line JSON dump costs ~3,500 tokens of context.

---

## 6. Empirical Verification & Portability Guardrails

1. **Empirical Proof Before Claiming Success:** Never state "feature X is complete" without running verification tools:
   - Python / Backend: `uv run pytest tests/` or `uv run python -m harness.eval_runner`
   - Frontend / E2E: `pnpm test` or `npx tsc --noEmit`
2. **Zero Hardcoded Absolute Paths:** Always use relative paths (`./`) or runtime-resolved paths (`Path.cwd()`, `import.meta.url`). Code must run anywhere after being zipped, moved, or cloned.
3. **Clean Stdio Transport:** In MCP tools, agents, or CLI processes, `stdout` is strictly reserved for data (JSON-RPC). All logging, diagnostic prints, and debugging must route to `stderr`.
4. **No Speculative Code Sprawl:** When asked for documentation, planning, or skill updates, do not generate speculative code files (`.py`, `.ts`) unless explicitly instructed.
