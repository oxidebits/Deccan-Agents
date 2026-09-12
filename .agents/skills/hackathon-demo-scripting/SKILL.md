---
name: hackathon-demo-scripting
description: >-
  Script, storyboard, and produce high-impact 2-minute hackathon demo videos and project submissions.
  Use this skill whenever planning the video presentation, elevator pitch, demo choreography,
  or judging rubric alignment for AI hackathons (especially AI Tinkerers and OpenAI).
---

# Hackathon Demo Scripting & 120-Second Submission Blueprint

> [!IMPORTANT]
> **SUBMISSION GUARDRAIL:**
> Judges evaluate the 120-second video first. Videos exceeding 2 minutes lose points.
> Do NOT load binary MP4 files into context; inspect timestamps and subtitles via text scripts.

---

## 1. The Winning 120-Second Video Architecture

| Time Window | Section | On-Screen Action | Spoken Script Focus |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:18** (18s) | **The Hook** | 10 open tabs, lost context across chat, email, and CRM. | *"Agents trapped in chat windows force humans to act as manual data mules."* |
| **0:18 – 0:35** (17s) | **The Solution** | Ambiguous AI workspace opening with `@Massy` avatar. | *"Introducing Massy — an autonomous AI coworker living natively in Ambiguous AI via MCP."* |
| **0:35 – 1:25** (50s) | **Core Live Demo** | 1-Click Lead Triage: Mail $\rightarrow$ Exa search $\rightarrow$ Docs $\rightarrow$ CRM $\rightarrow$ Chat approval. | *"Watch Massy triage an enterprise inquiry, ground with Exa, and publish directly to Docs and CRM."* |
| **1:25 – 1:45** (20s) | **Architecture & Rigor** | FastMCP + LangGraph StateGraph + LangSmith Trace Waterfall + Eval Harness Scorecard. | *"Powered by FastMCP, LangGraph, and Exa — fully observable via LangSmith and verified by a 4-pillar eval harness."* |
| **1:45 – 2:00** (15s) | **The Close** | GitHub repository & Ambiguous live screen. | *"Building the future where agents aren't chatbots, but true teammates. Thank you!"* |

---

## 2. Canonical 120-Second Script (Word-for-Word)

> **[0:00 - 0:18] THE HOOK**  
> *"Today, every AI agent forces you into an isolated chat sidebar. You have to copy-paste context back and forth between your email, CRM, spreadsheets, and research documents. But what if your agent lived directly inside the tools where your team already works?"*  
>  
> **[0:18 - 0:35] THE PRODUCT**  
> *"Meet **Massy**, an autonomous coworker built natively for Ambiguous AI using the Model Context Protocol. Massy isn't a chatbot — it has its own workspace identity, shares our team data, and takes real actions across Docs, Sheets, Mail, CRM, and Chat."*  
>  
> **[0:35 - 1:25] THE LIVE DEMO**  
> *"Here’s an authentic workflow. An inbound email arrives from the VP of Payments at a Fortune 500 retailer evaluating Stripe vs Adyen. In Ambiguous Chat, I trigger Massy: 'Triage this inquiry and prepare a Deal Desk briefing.'*  
> *Behind the scenes, Massy’s LangGraph state machine plans the research and calls Exa to crawl verified pricing tiers from the live web. It formats an executive briefing dossier in Ambiguous Docs, updates the CRM deal stage, and drops an interactive notification card in #sales-dealdesk with a 1-click human approval button. No tab switching, no manual data entry."*  
>  
> **[1:25 - 1:45] UNDER THE HOOD & TECHNICAL RIGOR**  
> *"Under the hood, Massy is engineered for enterprise reliability:  
> 1. Ambiguous AI for native coworker identity and multi-app access,  
> 2. Model Context Protocol (MCP) for clean stdio JSON-RPC tool orchestration,  
> 3. Exa API for real-time neural search,  
> 4. LangGraph for deterministic state transitions, and  
> 5. LangSmith observability paired with a 4-pillar evaluation harness verifying tool precision, grounding citations, and sub-3-second latency across every run."*  
>  
> **[1:45 - 2:00] THE CLOSE**  
> *"Massy isn't an assistant in a sidecar; it's a team member in the room. Our code, test suites, and eval harness are open source and available right now on GitHub. Thank you!"*

---

## 3. Submission Metadata Formula

- **Title:** `Massy — Autonomous Deal & Market Intelligence Coworker for Ambiguous AI`
- **Short Tagline (140 chars):** `Autonomous AI coworker in Ambiguous AI via FastMCP, LangGraph state machines, Exa search, with LangSmith tracing & eval harness.`
- **GitHub URL:** Relative repo with passing Playwright, Pytest, and Eval Harness suites.
- **Evaluation Proof:** Include LangSmith project link (`https://smith.langchain.com/...`) and terminal eval scorecard output.
