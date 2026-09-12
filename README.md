# ContextBridge Enterprise

ContextBridge is a two-hour hackathon prototype that turns a Microsoft Teams outgoing-webhook mention into an auditable engineering run:

1. Teams receives a synchronous acknowledgement in under five seconds.
2. A background run performs Tier 1 requirement triage and Tier 2 peer review through OpenRouter, or deterministic fixtures when `RUN_MODE=MOCK` or a provider fails.
3. A simulated Jira ticket is recorded, then an audited fixed patch adds a bearer-protected `GET /premium` endpoint to `mock_repo`.
4. The local mock repository is compiled and unit-tested.
5. A unique `contextbridge/demo-<run-id>` branch is created locally; with GitHub credentials configured, the same patch and tests are published as a real draft PR. Otherwise GitHub is reported honestly as simulated.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Start a deterministic local run:

```bash
curl -X POST http://127.0.0.1:8000/demo/run
```

Open the returned `status_url`, appending `/view` for a presenter-friendly page. The API result identifies every live, simulated, fallback, and failed integration. Run tests with:

```bash
python3 -m unittest discover -s tests -v
```

## Teams setup

Expose the app with an HTTPS tunnel, for example `ngrok http 8000`, then configure its `/webhook` URL as the Teams Outgoing Webhook callback. Copy the HMAC key Teams provides into `TEAMS_HMAC_SECRET` and set `ALLOW_UNSIGNED_WEBHOOKS=false`. Teams sends `Authorization: HMAC <base64-signature>` and the app validates the raw request body before accepting it.

For the local curl/demo route only, `ALLOW_UNSIGNED_WEBHOOKS=true` is convenient. Do not use that setting with a public tunnel.

## Live integrations

Set `RUN_MODE=LIVE` and `OPENROUTER_API_KEY` to run the configured Llama triage and DeepSeek review calls. Any provider or JSON-format failure falls back to the stored demo specification and marks the run as degraded.

## GitHub account and repository setup

This prototype uses two deliberately separate repositories:

- **Agent repository:** this project source (`app/`, `tests/`, documentation, and configuration). Add your existing repository as this workspace's `origin` and push the implementation there.
- **Demo repository:** only the runtime patch produced in `mock_repo`. The app creates a unique draft PR against this repository and never writes to its base branch.

On macOS, install and authenticate the GitHub CLI once:

```bash
brew install gh
gh auth login
gh auth status
```

Choose `GitHub.com`, `HTTPS`, and **Login with a web browser** in the prompts. For the agent repository, replace the URL and run:

```bash
git remote add origin https://github.com/OWNER/EXISTING-AGENT-REPOSITORY.git
git branch -M main
git add .
git commit -m "Build ContextBridge Enterprise prototype"
git push -u origin main
```

Create a clean remote repository for the walkthrough, initialized with a README so it has a `main` branch:

```bash
gh repo create contextbridge-demo --private --add-readme
```

Then run `gh auth token`, copy its output, and place it with the repository values in the local `.env` file:

```bash
RUN_MODE=LIVE
GITHUB_TOKEN=PASTE_THE_OUTPUT_OF_GH_AUTH_TOKEN_HERE
GITHUB_REPOSITORY=OWNER/contextbridge-demo
GITHUB_BASE_BRANCH=main
```

For a fine-grained token, grant the demo repository **Contents: Read and write** and **Pull requests: Read and write**. Keep `.env` local; it is ignored by git.

Jira is deliberately simulated as `PROJ-901` in this prototype, avoiding an OAuth/account blocker while keeping the end-to-end status truthful.
