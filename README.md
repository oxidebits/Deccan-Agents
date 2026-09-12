# Deccan Agents - Team Name

## Plan

We are building a AI Agent which lives in Teams.
Apps Connected 
- Microsoft Teams
- Github
- Jira


The communication happens on Microsoft Teams. Code is hosted on Github. And Jira for project tracking


Scenerio

The Developer is on holiday, the project manager asks the feature to implement. THe developer sees and calls the agent in teams. The AI Agent analyes the requirements , creates the task in jira, starts working on the task, completes it, makes the pull request and ask other teams members to review in teams. The team member reviews and comments and requests changes. AI Agent sees and implements the changes, and again asks for review. This happens until the team member approves the changes. Then AI Agent updates the task in jira. Once the task is completed, AI Agent updates the task in jira and closes the ticket. Notifies the team member in teams. 

To implement this workflow, set up the required accounts and credentials across **GitHub**, **Jira**, **Microsoft Teams / Azure**, and a **Local Tunnel**:

---

**1. GitHub Setup**

* **GitHub Account & Target Repository:** Ensure you have admin access to the repository where the agent will push code and create PRs.
* **Generate a Personal Access Token (PAT) or GitHub App:**
* Go to **GitHub Settings → Developer Settings → Personal access tokens → Fine-grained tokens** (or Tokens Classic).
* Generate a token with the following repository permissions:
* `Pull requests`: Read and Write
* `Issues`: Read and Write
* `Contents`: Read and Write (to create branches and commit files)


* Save the token as `GITHUB_TOKEN`.


* **Repository Webhook:**
* Go to your repository **Settings → Webhooks → Add webhook**.
* **Payload URL:** Your server endpoint (e.g., `https://<tunnel-id>.ngrok-free.app/webhooks/github`).
* **Content type:** `application/json`.
* **Events:** Check **Let me select individual events** → select **Pull request reviews** and **Issue comments**.



---

**2. Atlassian / Jira Setup**

* **Jira Cloud Instance:** You need an active Jira site (e.g., `[https://your-org.atlassian.net](https://your-org.atlassian.net)`) and a project key (e.g., `PROJ`).
* **Generate an Atlassian API Token:**
* Log in to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens).
* Click **Create API token**, label it (e.g., `LangGraph-Agent`), and copy the value immediately.
* Save the credentials:
* `JIRA_SERVER` (e.g., `[https://your-org.atlassian.net](https://your-org.atlassian.net)`)
* `JIRA_EMAIL` (the Atlassian account email address)
* `JIRA_API_TOKEN`




* **Jira Webhook (Optional if only reading/writing via API):**
* Go to **Jira Settings (gear icon) → System → Webhooks** (under Advanced).
* Click **Create a Webhook**, add your URL (`https://<tunnel-id>.ngrok-free.app/webhooks/jira`), and check **Issue: created / updated** if you need incoming trigger events from Jira tickets.



---

**3. Microsoft Teams & Azure Bot Setup**

* **Microsoft 365 Tenant & Teams Account:** A Microsoft account with permission to install custom apps in Teams.
* **Azure Portal Account:**
* Sign in to the [Azure Portal](https://www.google.com/search?q=https://portal.azure.com).
* Go to **Create a resource** → search for **Azure Bot** → click **Create**.
* Configure:
* **Bot handle:** Name of your bot (e.g., `devagent-bot`).
* **Pricing tier:** Free (F0).
* **Type of App:** Multi Tenant.


* Click **Review + create**.


* **Get App ID and Client Secret:**
* Open your created Azure Bot resource → go to **Configuration**.
* Note the **Microsoft App ID**.
* Next to App ID, click **Manage Password** (opens Certificates & Secrets in Entra ID) → click **New client secret** → copy the **Value** (`MICROSOFT_APP_PASSWORD`).
* In the Bot **Configuration** page, set **Messaging endpoint** to:
`https://<tunnel-id>.ngrok-free.app/api/messages`


* **Enable the Teams Channel:**
* Under the Azure Bot menu, select **Channels** → click **Microsoft Teams** → accept the terms and click **Apply**.


* **Install Bot into Teams:**
* Open **Teams Developer Portal** (or use App Studio in Teams).
* Create a new app, configure the bot using your **Microsoft App ID**, set the scope to **Team** and **Personal**, and click **Publish to your Org** or **Preview in Teams**.



---

**4. Local Tunnel Account (for Development)**

Because Microsoft Teams and GitHub require publicly accessible HTTPS URLs for webhooks, create a tunnel account to test your local machine:

* Sign up at **ngrok.com** (or install **Cloudflare Tunnel**).
* Install the CLI: `brew install ngrok` or download from the dashboard.
* Authenticate your agent: `ngrok config add-authtoken <your-ngrok-token>`.
* Run: `ngrok http 8000` to get your public HTTPS forwarding URL.

---

**Summary Checklist of Environment Variables**

```env
# GitHub
GITHUB_TOKEN=ghp_xxxx
GITHUB_REPO=organization/repo-name

# Jira
JIRA_SERVER=https://your-org.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=PROJ

# Microsoft Teams / Azure Bot
MICROSOFT_APP_ID=xxxx-xxxx-xxxx-xxxx
MICROSOFT_APP_PASSWORD=your_azure_client_secret

# LLM API
OPENAI_API_KEY=your_llm_key  # or ANTHROPIC_API_KEY / AZURE_OPENAI_API_KEY

```
