from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    output: str


class CodexLocalRunner:
    """Applies one intentionally constrained, reviewable patch to the demo repo."""

    def __init__(self, target_dir: Path, premium_token: str) -> None:
        self.target_dir = target_dir
        self.premium_token = premium_token

    def prepare_repository(self) -> None:
        if not (self.target_dir / ".git").exists():
            (self.target_dir / "tests").mkdir(parents=True, exist_ok=True)
            self._write(self.target_dir / "app.py", self._baseline_application())
            self._write(self.target_dir / "tests" / "test_app.py", self._baseline_tests())
            self._run_git("init", "-b", "main")
            self._run_git("config", "user.email", "relay-demo@example.invalid")
            self._run_git("config", "user.name", "Relay Demo")
            self._run_git("add", "app.py", "tests/test_app.py")
            self._run_git("commit", "-m", "Initialize Relay mock application")
        else:
            # mock_repo is disposable demo state. Each run starts from its committed baseline.
            self._run_git("checkout", "-f", "main")

    def apply_fixed_premium_patch(self) -> Path:
        self.prepare_repository()
        self._write(self.target_dir / "app.py", self._patched_application())
        self._write(self.target_dir / "tests" / "test_app.py", self._patched_tests())
        return self.target_dir / "app.py"

    def execute_test_suite(self) -> ValidationResult:
        commands = [
            [sys.executable, "-m", "py_compile", "app.py"],
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        ]
        outputs: list[str] = []
        for command in commands:
            completed = subprocess.run(
                command,
                cwd=self.target_dir,
                capture_output=True,
                text=True,
                check=False,
                env={**os.environ, "DEMO_PREMIUM_TOKEN": self.premium_token},
            )
            outputs.append(completed.stdout + completed.stderr)
            if completed.returncode != 0:
                return ValidationResult(False, "\n".join(outputs).strip())
        return ValidationResult(True, "\n".join(outputs).strip())

    def create_run_branch(self, run_id: str) -> str:
        branch = f"relay/demo-{run_id[:8]}"
        self._run_git("checkout", "-b", branch)
        self._run_git("add", "app.py", "tests/test_app.py")
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.target_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        if status.stdout.strip():
            self._run_git("commit", "-m", "Add premium subscription validation endpoint")
        return branch

    def patched_app_source(self) -> str:
        return (self.target_dir / "app.py").read_text(encoding="utf-8")

    def patched_test_source(self) -> str:
        return (self.target_dir / "tests" / "test_app.py").read_text(encoding="utf-8")

    def _run_git(self, *args: str) -> None:
        subprocess.run(
            ["git", *args], cwd=self.target_dir, capture_output=True, text=True, check=True
        )

    @staticmethod
    def _write(path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")

    @staticmethod
    def _baseline_application() -> str:
        return '''from fastapi import FastAPI

app = FastAPI(title="Mock Business Application")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "healthy"}
'''

    @staticmethod
    def _baseline_tests() -> str:
        return '''import unittest

from app import read_root


class RootTests(unittest.TestCase):
    def test_root_is_healthy(self) -> None:
        self.assertEqual(read_root(), {"status": "healthy"})


if __name__ == "__main__":
    unittest.main()
'''

    def _patched_application(self) -> str:
        default_token_literal = repr(self.premium_token)
        return f'''import os

from fastapi import FastAPI, Header, HTTPException, status

app = FastAPI(title="Mock Business Application")
EXPECTED_PREMIUM_TOKEN = os.getenv("DEMO_PREMIUM_TOKEN", {default_token_literal})


@app.get("/")
def read_root() -> dict[str, str]:
    return {{"status": "healthy"}}


@app.get("/premium")
def premium_access(authorization: str | None = Header(default=None)) -> dict[str, str]:
    expected_header = f"Bearer {{EXPECTED_PREMIUM_TOKEN}}"
    if authorization != expected_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid premium bearer token is required.",
        )
    return {{"status": "premium access granted"}}
'''

    @staticmethod
    def _patched_tests() -> str:
        return '''import os
import unittest

from fastapi import HTTPException

from app import premium_access, read_root


class PremiumAccessTests(unittest.TestCase):
    def test_root_is_healthy(self) -> None:
        self.assertEqual(read_root(), {"status": "healthy"})

    def test_premium_rejects_missing_token(self) -> None:
        with self.assertRaises(HTTPException) as error:
            premium_access(None)
        self.assertEqual(error.exception.status_code, 401)

    def test_premium_accepts_configured_token(self) -> None:
        self.assertEqual(
            premium_access(f"Bearer {os.environ['DEMO_PREMIUM_TOKEN']}"),
            {"status": "premium access granted"},
        )


if __name__ == "__main__":
    unittest.main()
'''
