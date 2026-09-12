# Project Rules & Runtime Context

## Local System Information
- Node.js: v24.18.0
- npm: 11.16.0
- pnpm: 11.15.1
- TypeScript Compiler: 7.0.2
- Python: 3.14.7 (use `uv` for lightning-fast venvs and pip installs: `uv 0.12.3`)
- Git: 2.55.0

## Critical Hackathon Resources
- High-signal documentation endpoints & llms.txt are listed in [ENVIRONMENT.md](./ENVIRONMENT.md).
- Event brief & submission rules: [README.md](./README.md).
- Target strategy: [PREP_STRATEGY.md](./PREP_STRATEGY.md).
- Winning project specification: [WINNING_PROJECT_SPEC.md](./WINNING_PROJECT_SPEC.md).

## Modern Development Practices (Crucial Guardrails)
- **Mandatory Git Commit Per User Turn:** For every user message or completed milestone, execute a `git commit` with a simple, clear, and understandable message. Never leave uncommitted changes at turn end.
- **Balanced Thinking vs. Doing:** Avoid analysis paralysis (token-wasting theoretical essays) and avoid lazy shortcuts (cheap workarounds, fake mocks, or `TODO` stubs). Spend $\le 20\%$ effort inspecting ground truth, $\ge 60\%$ implementing clean logic, and $\ge 20\%$ validating.
- **Functional Coding Standards:** Every piece of code must adhere to clean functional practices: pure deterministic functions, explicit type signatures, state immutability, defensive error handling, and robust production-grade quality. Get the job done correctly.
- **Live Traceability Logging:** Maintain a clear audit trail in [EXECUTION_LOG.md](./EXECUTION_LOG.md) documenting goals, files modified, architectural decisions, test verification results, and commit hashes for every step.
- **Context Window Pre-Flight Protocol:** NEVER dump raw datasets (>100 lines) into context. Check dimensions first with `wc -l` or inspect keys with `jq 'keys'`.
- **Empirical Verification Before Completion:** Always verify changes with unit tests, compilers, or eval runners (`uv run pytest`, `pnpm test`, `uv run python -m harness.eval_runner`) before declaring success.
- **Zero Raw Pip on macOS (PEP 668):** NEVER run bare `pip install`. Modern macOS uses externally managed Python. Always use `uv venv` and `uv pip install`, or run tools via `uv run <tool>`.
- **Zero Hardcoded Absolute Paths:** Always use relative paths (`./`) or workspace-resolved paths so the project can be zipped, moved, or cloned anywhere without breaking.
- **Clean MCP stdio Transport:** When writing MCP servers or CLI agents, all diagnostic logs must go to `stderr` so that `stdout` is strictly reserved for clean JSON-RPC.
- **Model Execution Protocol Skill:** For detailed patterns and schemas, reference [.agents/skills/model-execution-protocol/SKILL.md](./.agents/skills/model-execution-protocol/SKILL.md).
