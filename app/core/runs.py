from __future__ import annotations

import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class Run:
    id: str
    transcript: str
    status: str = "queued"
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class RunStore:
    def __init__(self) -> None:
        self._runs: dict[str, Run] = {}
        self._lock = threading.Lock()

    def create(self, transcript: str) -> Run:
        run = Run(id=uuid.uuid4().hex, transcript=transcript)
        with self._lock:
            self._runs[run.id] = run
        return run

    def update(self, run_id: str, *, status: str, result: dict[str, Any] | None = None, error: str | None = None) -> None:
        with self._lock:
            run = self._runs[run_id]
            run.status = status
            run.updated_at = _now()
            if result is not None:
                run.result = result
            run.error = error

    def get(self, run_id: str) -> dict[str, Any] | None:
        with self._lock:
            run = self._runs.get(run_id)
            return asdict(run) if run else None

