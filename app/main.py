from __future__ import annotations

import base64
import hashlib
import hmac
import html
import re

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


def normalize_transcript(payload: dict[str, object]) -> str:
    text = str(payload.get("text") or "")
    text = re.sub(r"<at>.*?</at>", "", text, flags=re.IGNORECASE).strip()
    return text if len(text) >= 25 else load_demo_transcript(settings.project_root)


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
                f"Demo status: `/runs/{run_id}`."
            ),
        }
    )


@app.post("/demo/run")
def start_demo(background_tasks: BackgroundTasks) -> dict[str, str]:
    """Local-only demo trigger; it bypasses Teams authentication."""
    run_id = service.start(load_demo_transcript(settings.project_root))
    background_tasks.add_task(service.execute, run_id)
    return {"run_id": run_id, "status_url": f"/runs/{run_id}"}


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

