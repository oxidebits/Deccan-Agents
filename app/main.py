from __future__ import annotations

import base64
import hashlib
import hmac
import html
import re
import time
from urllib.parse import parse_qs

import requests
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.core.runs import RunStore
from app.core.service import ContextBridgeService, load_demo_transcript
from app.core.settings import Settings

settings = Settings.from_environment()
run_store = RunStore()
service = ContextBridgeService(settings, run_store)
app = FastAPI(title="ContextBridge Enterprise", version="0.1.0")


def verify_teams_hmac(authorization: str | None, body: bytes) -> bool:
    """Verify the HMAC value Teams sends as `Authorization: HMAC <base64>`."""
    if not settings.teams_hmac_secret:
        return settings.allow_unsigned_webhooks
    if not authorization or not authorization.startswith("HMAC "):
        return False
    try:
        key = base64.b64decode(settings.teams_hmac_secret, validate=True)
    except ValueError:
        return False
    expected = base64.b64encode(hmac.new(key, body, hashlib.sha256).digest()).decode()
    supplied = authorization.removeprefix("HMAC ").strip()
    return hmac.compare_digest(supplied, expected)


def verify_slack_signature(
    signature: str | None,
    timestamp: str | None,
    body: bytes,
    signing_secret: str | None = None,
) -> bool:
    """Verify a Slack v0 request signature and reject replayed requests."""
    secret = signing_secret or settings.slack_signing_secret
    if not secret or not signature or not timestamp:
        return False
    try:
        request_time = int(timestamp)
    except ValueError:
        return False
    if abs(time.time() - request_time) > 60 * 5:
        return False
    base_string = b"v0:" + timestamp.encode() + b":" + body
    expected = "v0=" + hmac.new(secret.encode(), base_string, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def normalize_transcript(payload: dict[str, object]) -> str:
    text = str(payload.get("text") or "")
    text = re.sub(r"<at>.*?</at>", "", text, flags=re.IGNORECASE).strip()
    return text if len(text) >= 25 else load_demo_transcript(settings.project_root)


def status_url(run_id: str) -> str:
    path = f"/runs/{run_id}/view"
    return f"{settings.public_base_url}{path}" if settings.public_base_url else path


def slack_result_text(run: dict[str, object]) -> str:
    result = run.get("result") if isinstance(run.get("result"), dict) else {}
    tests = result.get("tests") if isinstance(result.get("tests"), dict) else {}
    jira = result.get("jira") if isinstance(result.get("jira"), dict) else {}
    github = result.get("github") if isinstance(result.get("github"), dict) else {}
    lines = [f"🤖 *ContextBridge run: {run['status']}*"]
    if jira:
        lines.append(f"• Jira: `{jira.get('key', 'not created')}` ({jira.get('mode', 'unknown')})")
    lines.append(f"• Validation: {'passed' if tests.get('passed') else 'failed'}")
    if github:
        if github.get("url"):
            lines.append(f"• GitHub draft PR: <{github['url']}|open pull request>")
        else:
            lines.append(f"• GitHub: {github.get('detail', github.get('mode', 'unknown'))}")
    if run.get("error"):
        lines.append(f"• Error: {run['error']}")
    lines.append(f"• Run details: {status_url(str(run['id']))}")
    return "\n".join(lines)


def complete_slack_run(run_id: str, response_url: str) -> None:
    service.execute(run_id)
    run = run_store.get(run_id)
    if not run:
        return
    try:
        requests.post(
            response_url,
            json={"response_type": "in_channel", "replace_original": True, "text": slack_result_text(run)},
            timeout=(3, 15),
        )
    except requests.RequestException:
        # The result remains available on the public status page if Slack's callback expires.
        pass


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "mode": settings.run_mode}


@app.post("/webhook")
async def handle_teams_webhook(request: Request, background_tasks: BackgroundTasks) -> JSONResponse:
    raw_body = await request.body()
    if not verify_teams_hmac(request.headers.get("Authorization"), raw_body):
        raise HTTPException(status_code=401, detail="Invalid Teams HMAC signature.")
    try:
        payload = await request.json()
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Webhook body must be JSON.") from error
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Webhook payload must be an object.")
    run_id = service.start(normalize_transcript(payload))
    background_tasks.add_task(service.execute, run_id)
    return JSONResponse(
        {
            "type": "message",
            "text": (
                "🤖 ContextBridge accepted this request and started a background run. "
                f"Demo status: {status_url(run_id)}"
            ),
        }
    )


@app.post("/slack/command")
async def handle_slack_command(request: Request, background_tasks: BackgroundTasks) -> JSONResponse:
    raw_body = await request.body()
    if not verify_slack_signature(
        request.headers.get("X-Slack-Signature"),
        request.headers.get("X-Slack-Request-Timestamp"),
        raw_body,
    ):
        raise HTTPException(status_code=401, detail="Invalid Slack signature.")
    form = parse_qs(raw_body.decode("utf-8"), keep_blank_values=True)
    if form.get("ssl_check") == ["1"]:
        return JSONResponse({})
    response_url = form.get("response_url", [""])[0]
    if not response_url:
        raise HTTPException(status_code=400, detail="Slack command lacks a response URL.")
    transcript = normalize_transcript({"text": form.get("text", [""])[0]})
    run_id = service.start(transcript)
    background_tasks.add_task(complete_slack_run, run_id, response_url)
    return JSONResponse(
        {
            "response_type": "in_channel",
            "text": (
                "🤖 ContextBridge accepted this request and started a background run. "
                f"Live status: {status_url(run_id)}"
            ),
        }
    )


@app.post("/demo/run")
def start_demo(background_tasks: BackgroundTasks) -> dict[str, str]:
    """Local-only demo trigger; it bypasses Teams authentication."""
    run_id = service.start(load_demo_transcript(settings.project_root))
    background_tasks.add_task(service.execute, run_id)
    return {"run_id": run_id, "status_url": status_url(run_id)}


@app.get("/runs/{run_id}")
def read_run(run_id: str) -> JSONResponse:
    run = run_store.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    return JSONResponse(run)


@app.get("/runs/{run_id}/view", response_class=HTMLResponse)
def view_run(run_id: str) -> HTMLResponse:
    run = run_store.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    rendered = html.escape(__import__("json").dumps(run, indent=2))
    return HTMLResponse(
        f"<html><body style='font-family:ui-monospace,monospace;max-width:980px;margin:40px auto'>"
        f"<h1>ContextBridge run {html.escape(run_id)}</h1><pre>{rendered}</pre></body></html>"
    )
