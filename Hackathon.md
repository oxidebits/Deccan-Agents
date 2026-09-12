# Agents, Everywhere: Bots, Channels, & More — Global Hackathon

A global build day with **OpenAI** and **AI Tinkerers**.

- **Event Date:** Saturday, September 12, 2026
- **Global Submission Deadline:** 5:00 PM IST (Portal cutoff)
- **Format:** Focused local build day connected to one shared global competition.
- **Food & Drinks:** Provided at venue.

---

## 1. The Theme & Challenge

> **Core Theme:**  
> *"Agents are leaving the chatbox. Build an agent for a place people already work, talk, or live, then make it meaningfully more useful because of that context."*

Most agents still wait inside a separate chat window (`localhost:3000` or ChatGPT). This hackathon challenges builders to put agents directly into:
- **Workplace collaboration:** Slack, Teams, email, documents, calendars, tickets, support, or live CRM workflows.
- **Everyday mobile:** Messaging, notifications, short asynchronous interactions.
- **Web & browser:** Environments where an agent can research, navigate, transact, or manipulate live software.
- **Physical interfaces:** Voice, vision, wearables, robotics, and smart environments.

*These are illustrative examples, not separate tracks. Every project enters the single global review pool.*

---

### 1.1 The Foundational Substrate: How Agents Actually Leave the Chatbox

To put an agent into places where people already work, builders cannot simply build another sidebar. Real workplace integration relies on **4 foundational invocation & execution paradigms**:

1. **Contextual Symbols & Direct Mentions:**
   - `@mentions` (`@Massy`): Teammates tag the agent directly inside Slack threads, Ambiguous Chat channels, Google Doc comments, or Linear tickets. The host platform forwards the thread context, user role, and parent document ID directly to the agent.
   - **Slash Commands** (`/massy triage`, `/massy brief`): Familiar, structured triggers inside communication clients that allow users to dispatch workflows with predictable parameters.
   - **Channel Routing** (`#sales-dealdesk`, `#security-incidents`): Agents listen to specific operational streams rather than interrupting the entire company.

2. **Ambient & Event-Driven Triggers (Zero Manual Input):**
   - **Inbound Mail Webhooks:** Arrival of high-stakes customer inquiries or partner emails in Ambiguous Mail automatically wakes up the agent.
   - **Sheet & Record Mutations:** When a new row is added or an account enters a renewal window in Ambiguous Sheets/CRM, the agent performs background research and enriches data proactively.
   - **Calendar Schedule Watchers:** Approaching meetings trigger pre-briefing assembly 15 minutes before call time.

3. **In-Context Action Execution & Human-in-the-Loop (HITL):**
   - Agents must not dump 10 paragraphs of text into a message feed. They manipulate the actual artifacts: updating the spreadsheet cells, appending to the collaborative document, reserving calendar holds, and dropping **interactive 1-click approval cards** (`[Approve & Send]`, `[Publish to Board Pack]`).

4. **The Enabling Frameworks & Sponsor Tooling:**
   - **Ambiguous AI (Targeting the DGX Spark):** Provides the complete enterprise workplace foundation (17 apps: Docs, Sheets, Mail, CRM, Calendar, Chat) with first-class coworker identity (`@Massy`, `massy@company.com`) and native Model Context Protocol (MCP) tool routing.
   - **CopilotKit:** The open-source standard for embedding agents inside application frontends. Provides `useCopilotReadable` (giving the agent awareness of what the user has open on screen), `useCopilotAction` (allowing the agent to mutate app state), and `CopilotTextarea` (inline `@mention` completions directly in text inputs).
   - **Model Context Protocol (MCP):** The universal JSON-RPC open standard enabling clients (Ambiguous AI, Claude, Cursor) to discover and invoke tools, read resources, and execute workflows over clean stdio/SSE.
   - **Trigger.dev (v3):** Reliable serverless event orchestration, webhook listeners, and background task retry queues that execute long-running workflows without timing out the user interface.

---

## 2. Event Day Schedule

| Time (Local) | Activity | Details |
| :--- | :--- | :--- |
| **10:00 – 10:30 a.m.** | Arrival & Check-in | Doors open, breakfast/food, meet builders |
| **10:30 – 11:00 a.m.** | Global Opening Broadcast | Challenge briefing, starter kits, builder credits walkthrough |
| **11:00 – 11:15 a.m.** | Team Formation | Finalize teams or confirm solo build status |
| **11:15 a.m. – 3:30 p.m.** | **Build Sprint** | Core coding and agent development window |
| **3:30 – 4:00 p.m.** | **Submission Window** | Finalize GitHub repo, 2-min video, and submit in portal |
| **4:00 – 4:45 p.m.** | Local Show-and-Tell | Informal sharing and peer demos (no local formal judging) |
| **4:45 – 5:00 p.m.** | Wrap & Group Photo | Community closing |

---

## 3. Official Global Judging Rubric (Scored 1 to 5)

Projects are evaluated globally by judges across **4 core criteria (1–5 scale)**:

| Criterion | What Judges Evaluate | Scoring Benchmark (1 to 5) |
| :--- | :--- | :--- |
| **1. Core Requirements & Functionality** | Does the project deliver a working agent inside a place where people work, talk, or live? Does the core workflow function end to end? | **1:** Does not run or non-functional.<br>**2:** Partial run, but core workflow/integration broken.<br>**3:** Basic end-to-end flow works with bugs.<br>**4:** Works reliably with only minor issues.<br>**5:** Robust, reliable, fully functional in its native environment. |
| **2. Innovation & Theme Alignment** | Does the project explore a compelling new interaction? Does the environment materially improve what the agent can do? | **1:** Generic chatbot or wrapper; environment is irrelevant.<br>**2:** Agent appears in environment, but only as a cosmetic skin.<br>**3:** Clearly addresses theme; environment adds real value.<br>**4:** Environment shapes core workflow and enables original UX.<br>**5:** Groundbreaking new agent pattern impossible in a standalone chatbox. |
| **3. Technical Execution & Integration** | Code quality, architecture, reliability, tool calling, data handling, and depth of environment integration. | **1:** Conceptual/mocked; little technical execution.<br>**2:** Superficial, unstable integration.<br>**3:** Solid technical execution with some rough edges.<br>**4:** Well-engineered, reliable, effective data & tool integration.<br>**5:** Exceptional engineering, robust orchestration, failure handling, and deep architecture. |
| **4. Usefulness & Agentic Experience** | Does the project create clear value for intended users? Is the agent intuitive, native, effective, and controllable? | **1:** Unclear use case; little meaningful value.<br>**2:** Recognizable use case, but basic prompt/response.<br>**3:** Useful, understandable, agent takes meaningful actions.<br>**4:** Solves a clear problem, feels native, strong human-AI collaboration.<br>**5:** Substantial value, intelligent contextual awareness, clear user control. |

---

## 4. Build Eligibility & Rules

- **Net-New Build Requirement:** Every submitted project must be a net-new build created during the official hackathon period.
- **Allowed Pre-Existing Assets:** Teams may use existing templates, reusable components, libraries, prompts, starter code, or design systems. However, the submitted project and its core functionality must be built during the event.
- **Exclusivity:** A pre-existing project cannot be resubmitted or extended as a new hackathon entry. Builders should be prepared to explain what was created during the hackathon.
- **Solo & Teams:** Builders may work solo or in teams of up to 5 members.

---

## 5. Submission Requirements (Hard Deadline: 3:30–4:00 PM)

Every team must complete all 5 submission items in the portal before the deadline:

1. **Project Title:** A clear, memorable name.
2. **Written Description:** What was built, target audience, and why the environment context matters.
3. **Public GitHub Repository:** Working code that can be reviewed and tested.
4. **Two-Minute Demo Video:** Concise video demonstrating the live project in action (hard 120s limit).
5. **Social Media Post:** Public post on X/LinkedIn tagging event partners.

---

## 6. Global Prizes

### Placement Prizes
- 🥇 **First Place:**
  - **$10,000** in OpenAI credits for the team
  - **Mac mini** for every team member
  - **$1,000** in Exa credits for the team
  - Exa swag
- 🥈 **Second Place:**
  - **$5,000** in OpenAI credits for the team
  - **Ray-Ban Meta smart glasses** for every team member
  - **$500** in Exa credits for the team
  - Exa swag
- 🥉 **Third Place:**
  - **$2,500** in OpenAI credits for the team
  - **LOOI Robot** for every team member
  - **$250** in Exa credits for the team
  - Exa swag

### Sponsor Category Prizes
- ⚡ **Best Use of Ambiguous AI:** One **NVIDIA DGX Spark** for the winning team
- 🎧 **Best Use of CopilotKit:** A pair of **purple AirPods Max** for every team member

---

## 7. Sponsors & Infrastructure Partners

| Sponsor / Partner | Role | Key Technology & Value |
| :--- | :--- | :--- |
| **OpenAI** | Marquee Sponsor | Frontier LLMs (GPT-4o, o-series reasoning, Realtime APIs) |
| **Ambiguous AI** | Sponsor | 17 integrated productivity apps (Docs, Mail, Chat, CRM, Sheets, Calendar) with MCP/CLI agent coworker integration |
| **Exa AI** | Sponsor | Neural search, company intelligence, and web content extraction API |
| **Trigger.dev** | Sponsor | Background jobs, workflow queuing, and long-running task orchestration |
| **CopilotKit** | Sponsor | In-app agentic application framework, generative UI, and AG-UI/A2A protocol |
| **OpenRouter** | Sponsor | Multi-model routing gateway across top AI providers |
| **Auth0** | Sponsor | Identity, authentication, and secure agent login workflows |
| **Mozilla.ai** | Sponsor | Open-source, trustworthy AI tools and infrastructure |
| **Google Cloud Run** | Sponsor | Managed serverless container hosting and scalable deployment |

---

## 8. Five Core Workplace Workflows (Input Prompt $\rightarrow$ Architecture Flow $\rightarrow$ Multi-App Output)

These 5 reference workflows demonstrate the exact end-to-end lifecycle: how a natural-language workplace trigger connects across the technical stack (OpenAI reasoning, Exa search, FastMCP) to produce concrete outputs in Ambiguous AI apps.

---

### Workflow 1: Inbound Enterprise Deal Desk Triage
* **User Input / Inbound Email:**
  > *"We just received an inbound email from the VP of Engineering at a Fortune 500 retailer: 'Evaluating migration from legacy billing to Stripe or Adyen; need pricing tiers and SLA comparisons.' Research Stripe vs Adyen enterprise pricing, check recent acquisition news, and prepare our Deal Desk briefing."*
* **The Execution Flow:**
  `Ambiguous Mail` $\rightarrow$ `LangGraph Planner` $\rightarrow$ `Exa Neural Search` (crawls verified pricing benchmarks & news) $\rightarrow$ `FastMCP stdio`
* **The Tangible Outputs:**
  1. 📄 **Ambiguous Docs:** Creates `Briefing: Stripe vs Adyen Enterprise 2026` with executive summary, pricing breakdown table, and citations.
  2. 💼 **Ambiguous CRM:** Creates lead `Acme Retail Corp`, assigns tier `Tier 1 Enterprise ($75k ARR)`, and attaches briefing link.
  3. 💬 **Ambiguous Chat:** Posts in `#sales-dealdesk`: *"Inbound triaged. Full doc prepared, CRM deal stage set to 'Qualified'. 1-click to review."*

---

### Workflow 2: Account Retention & Vendor Risk Radar
* **User Input / Chat Trigger:**
  > *"Customer Success alerted that a key enterprise account is reconsidering Datadog renewal due to surprise cloud billing. Crawl recent outage reports, pricing restructure backlash, and top open-source alternatives (Grafana/Prometheus). Update our retention risk score and draft an objection-handling email."*
* **The Execution Flow:**
  `Ambiguous Chat` (`@Massy`) $\rightarrow$ `LangGraph Multi-Query Node` $\rightarrow$ `Exa Domain-Filtered Search` (Reddit, Hacker News, status feeds) $\rightarrow$ `FastMCP Handlers`
* **The Tangible Outputs:**
  1. 💼 **Ambiguous CRM:** Updates account health score from `Healthy (92)` $\rightarrow$ `At-Risk (64)` with annotated cost breakdown.
  2. ✉️ **Ambiguous Mail:** Drafts high-conviction email reply highlighting customized ROI and volume discount options for 1-click human approval.
  3. 💬 **Ambiguous Chat:** Replies in thread with 3 major customer pain points and links to the drafted email.

---

### Workflow 3: M&A & Competitor Intelligence Dossier
* **User Input / Slack or Chat Trigger:**
  > *"Leadership needs a rapid competitive dossier: 'What are the top 3 AI agent infrastructure startups funded in Q3 2026? Extract their target customers, pricing models, and key integrations. Prepare a comparison grid for our product strategy review.' "*
* **The Execution Flow:**
  `Ambiguous Chat` $\rightarrow$ `LangGraph Planner` $\rightarrow$ `Exa API` (`find_similar_and_contents` + neural news filter) $\rightarrow$ `LangGraph Synthesizer`
* **The Tangible Outputs:**
  1. 📊 **Ambiguous Sheets:** Populates `Competitor_Matrix_Q3_2026` with columns: *Company*, *Funding*, *Target Persona*, *Pricing Model*, *Core Integrations*, *Source URL*.
  2. 📄 **Ambiguous Docs:** Generates executive synthesis highlighting whitespace opportunities for our platform.
  3. 💬 **Ambiguous Chat:** Posts bulleted takeaway with direct hyperlink to the new spreadsheet.

---

### Workflow 4: Executive Board Staff Meeting Briefing
* **User Input / Calendar Event Trigger:**
  > *"Tomorrow is our monthly Board of Directors meeting. Scan industry news and research papers for: 'Enterprise bottlenecks in agentic AI deployments 2026'. Compile 3 verified case studies via Exa, outline compliance risks, and draft 4 strategic priorities for our slide deck."*
* **The Execution Flow:**
  `Ambiguous Calendar` (upcoming event listener) $\rightarrow$ `LangGraph Background Task` $\rightarrow$ `Exa Search` (academic & tech press highlights) $\rightarrow$ `Structured Output Parser`
* **The Tangible Outputs:**
  1. 📄 **Ambiguous Docs:** Creates `Board Memo: Enterprise Agentic Adoption & Risks (Sept 2026)`.
  2. 📅 **Ambiguous Calendar:** Attaches the generated Board Memo link directly to tomorrow's meeting invite.
  3. 💬 **Ambiguous Chat:** Direct-messages the founder/CEO: *"Board memo generated with 3 verified case studies and compliance notes. Ready for review."*

---

### Workflow 5: Proactive Partner Inbound & Meeting Dispatch
* **User Input / Inbound Email Trigger:**
  > *"Incoming email from Tech Lead at potential integration partner: 'Loved your MCP server demo. Can we sync for 20 minutes this Thursday afternoon to discuss a co-marketing integration?' "*
* **The Execution Flow:**
  `Ambiguous Mail` (ambient listener) $\rightarrow$ `Intent Classifier` $\rightarrow$ `Ambiguous Calendar Availability Check` $\rightarrow$ `FastMCP Schedule Tool`
* **The Tangible Outputs:**
  1. 📅 **Ambiguous Calendar:** Places a tentative calendar hold: `Hold: Partner Integration Sync (20 min)`.
  2. ✉️ **Ambiguous Mail:** Pre-fills a professional reply: *"Hi [Name], we'd love to connect. I've reserved Thursday at 2:30 PM or 4:00 PM EST. Let me know which works."*
  3. 💬 **Ambiguous Chat:** Drops notification card with an interactive **"Send Email & Confirm Hold"** button for 1-click human execution.