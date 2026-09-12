---
name: svelte5-agent-ui
description: >-
  Build real-time AI agent frontends and dashboards with Svelte 5, Runes, and Lucide icons.
  Use this skill whenever creating web UIs, streaming chat feeds, tool execution logs,
  or coworker dashboards using Svelte 5 ($state, $derived, $effect) and lucide-svelte.
---

# Svelte 5 Agent UI & Runes Skill

> [!IMPORTANT]
> **CRITICAL OPERATIONAL GUARDRAILS (From Dry Runs):**
> 1. **Package Versioning:** Use `lucide-svelte: "^1.0.1"` (or `@lucide/svelte`). Do not use non-existent versions.
> 2. **Svelte 5 Mount API:** Never use legacy Svelte 4 `new App(...)`. Use `mount(App, { target: document.getElementById('app')! })` from `'svelte'`.
> 3. **Runes State:** Use `$state()`, `$derived()`, and `$effect()`. Do not use legacy Svelte 4 `let` reactivity or `export let`.
> 4. **Functional Reactive Flow:** Derive values purely with `$derived()` without circular side-effects.
> 5. **Traceability & Commits:** Log UI changes in `EXECUTION_LOG.md` and commit on every user turn with clear messages.

---

## 1. Context Window Pre-Flight Protocol (Frontend Data & Assets)

> [!CAUTION]
> **DO NOT hardcode megabytes of mock data directly inside Svelte components.**
> - Store structured enterprise data in `seed_data.json`.
> - Check data size before importing: `wc -l seed_data.json`.
> - Import and bind reactively via runes: `let mockData = $state(seedData);`.

---

## 2. Quick Setup

```bash
# Fast Vite scaffold with Svelte 5 & TypeScript
pnpm create vite frontend --template svelte-ts
cd frontend
pnpm install lucide-svelte clsx tailwind-merge
```

---

## 3. Real-Time Coworker Dashboard Template (`src/App.svelte`)

```svelte
<script lang="ts">
  import { Bot, Sparkles, CheckCircle2, RefreshCw, MessageSquare } from 'lucide-svelte';

  // 1. Reactive State using Svelte 5 Runes
  let targetEntity = $state('Stripe');
  let isExecuting = $state(false);
  let statusText = $state('Ready');

  interface PipelineStep {
    name: string;
    status: 'idle' | 'running' | 'completed';
  }

  let steps = $state<PipelineStep[]>([
    { name: '1. LangGraph Planner', status: 'completed' },
    { name: '2. Exa Neural Search', status: 'completed' },
    { name: '3. Synthesis Engine', status: 'completed' },
    { name: '4. Ambiguous Dispatcher', status: 'completed' }
  ]);

  // 2. Derived State
  let completedCount = $derived(steps.filter(s => s.status === 'completed').length);

  // 3. Action Dispatcher
  function triggerWorkflow() {
    isExecuting = true;
    statusText = 'Massy is reasoning...';
    steps[0].status = 'running';
    setTimeout(() => {
      steps[0].status = 'completed';
      isExecuting = false;
      statusText = 'Workflow complete';
    }, 1500);
  }
</script>

<main class="min-h-screen p-6 bg-slate-950 text-slate-100 font-sans">
  <header class="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="p-2.5 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
        <Bot class="w-6 h-6" />
      </div>
      <div>
        <h1 class="text-lg font-bold text-white">Massy — Ambiguous AI Coworker</h1>
        <span class="text-xs text-emerald-400 font-mono">MCP Connected • {completedCount}/4 Steps Complete</span>
      </div>
    </div>
    <button 
      class="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2"
      onclick={triggerWorkflow}
      disabled={isExecuting}
    >
      {#if isExecuting}
        <RefreshCw class="w-3.5 h-3.5 animate-spin" />
      {:else}
        <Sparkles class="w-3.5 h-3.5" />
      {/if}
      <span>Run Coworker Workflow</span>
    </button>
  </header>
</main>
```

---

## 4. Verification

```bash
# Build test
pnpm run build

# Start dev server
pnpm run dev
```
