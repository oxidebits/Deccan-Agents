---
name: playwright-automation
description: >-
  Automate browser workflows, UI testing, screenshot capturing, and web interactions using Playwright TypeScript.
  Use this skill whenever controlling browsers, validating web pages, testing UI flows,
  or running Playwright via Node.js / TypeScript.
---

# Playwright Browser Automation Skill (Pure TypeScript)

> [!IMPORTANT]
> **CRITICAL OPERATIONAL GUARDRAILS (From Dry Runs):**
> 1. **Strict Mode Avoidance:** Never use ambiguous `getByText("String")` when that string appears in both buttons and headings. Use scoped locators:
>    - Headings: `page.getByRole("heading", { name: "Title" })`
>    - Buttons: `page.getByRole("button", { name: /Submit/i })`
>    - Table cells: `page.getByRole("cell", { name: "Value" })`
> 2. **Browser Binary Prerequisite:** Always ensure `npx playwright install chromium` is run before executing tests.
> 3. **Automatic Web Server:** Configure `webServer` in `playwright.config.ts` so `npm run dev` or `pnpm run dev` starts automatically.
> 4. **Empirical Verification:** Always execute tests (`pnpm test`) before declaring UI flows complete.
> 5. **Traceability & Commits:** Log verification passes to `EXECUTION_LOG.md` and commit after every turn with clear messages.

---

## 1. Context Window Pre-Flight Protocol (Test Logs & Traces)

> [!CAUTION]
> **NEVER dump binary trace files, video recordings, or raw base64 screenshots into the LLM context window.**
> - **Inspect Summaries:** Check the terminal output of `pnpm test`.
> - **Inspect Error Context:** If a test fails, Playwright generates a concise markdown snippet in `test-results/<test-name>/error-context.md`. Inspect ONLY that markdown file (`wc -l`, `cat`).

---

## 2. Production Playwright Configuration (`playwright.config.ts`)

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  testMatch: "**/*.spec.ts",
  fullyParallel: true,
  retries: 0,
  workers: 1,
  reporter: "list",
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { 
        ...devices["Desktop Chrome"],
        viewport: { width: 1280, height: 720 },
      },
    },
  ],
  webServer: {
    command: "pnpm run dev",
    url: "http://localhost:5173",
    reuseExistingServer: true,
    timeout: 30000,
  },
});
```

---

## 3. Production Test Suite Template (`tests/workplace-scenarios.spec.ts`)

```typescript
import { test, expect } from "@playwright/test";

test.describe("Massy Enterprise Workplace Scenarios", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText("Massy");
    await expect(page.getByText("MCP Connected")).toBeVisible();
  });

  test("Scenario 1: Inbound Lead Triage (Docs Generation)", async ({ page }) => {
    const wf1 = page.getByRole("button", { name: /1\. Inbound Enterprise Lead Triage/i });
    await wf1.click();
    await page.waitForTimeout(2200);

    // Scoped assertions avoid strict mode violations
    await expect(page.getByRole("heading", { name: /Stripe.*Dossier/i })).toBeVisible();
    await expect(page.getByText("Folder: Executive Briefings")).toBeVisible();
    await expect(page.getByText("Published to workspace teammates")).toBeVisible();
  });

  test("Scenario 2: M&A Sheet Audit (Competitor_Matrix_Q3_2026)", async ({ page }) => {
    const wf3 = page.getByRole("button", { name: /3\. M&A \/ Due Diligence Sheet Update/i });
    await wf3.click();
    await page.waitForTimeout(2200);

    await expect(page.getByRole("heading", { name: "Competitor_Matrix_Q3_2026" })).toBeVisible();
    await expect(page.getByRole("cell", { name: "Datavane" })).toBeVisible();
    await expect(page.getByText("Flagged - SEC Inquiry")).toBeVisible();
  });

  test("Scenario 3: Human-In-The-Loop Approval", async ({ page }) => {
    await page.getByRole("button", { name: /Team Chat/i }).click();
    await expect(page.getByText("Human-in-the-loop decision requested")).toBeVisible();

    await page.getByRole("button", { name: /1-Click Approve/i }).click();
    await expect(page.getByText("Confirm Human-In-The-Loop Action")).toBeVisible();

    await page.getByRole("button", { name: /Approve & Execute/i }).click();
    await expect(page.getByText("[Approved by Human Operator]")).toBeVisible();
  });
});
```

---

## 4. Dual-Layer Evaluation Architecture

To ensure high technical execution scoring from hackathon judges, verification operates across two complementary layers:

```
 ┌─────────────────────────────────────────────────────────────────────────┐
 │               Dual-Layer Autonomous Coworker Test Matrix               │
 ├────────────────────────────────────┬────────────────────────────────────┤
 │ Layer 1: Headless Harness & Trace  │ Layer 2: Playwright E2E UI         │
 │ (LangSmith + pytest + Python)      │ (Playwright + TypeScript)          │
 ├────────────────────────────────────┼────────────────────────────────────┤
 │ • Tool dispatch precision audit    │ • Visual DOM state changes         │
 │ • Exa citation & grounding check   │ • Svelte 5 Runes reactivity        │
 │ • Graph node latency profiling     │ • Human-In-The-Loop approval modal │
 │ • JSON-RPC stdio protocol purity   │ • Browser video demo capture       │
 └────────────────────────────────────┴────────────────────────────────────┘
```

---

## 5. Execution & Verification Commands

```bash
# 1. Run Layer 1: Python StateGraph & 4-Pillar Evaluation Harness
uv run python -m harness.eval_runner

# 2. Run Layer 2: Playwright E2E Browser Test Suite (Headless)
pnpm test

# 3. Run Layer 2 with visible browser (for live demo dry runs)
pnpm run test:headed
```
