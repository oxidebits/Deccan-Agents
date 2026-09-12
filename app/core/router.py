from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import requests

from app.core.settings import Settings


class OpenRouterError(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelResult:
    value: dict[str, Any]
    source: str


class OpenRouterManager:
    """Two-stage OpenRouter adapter with deterministic demo fallbacks."""

    endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def execute_triage(self, transcript: str) -> ModelResult:
        if self.settings.run_mode != "LIVE" or not self.settings.openrouter_api_key:
            return ModelResult(self._fixture_specification(transcript), "fixture")
        prompt = (
            "Analyze this engineering-channel transcript. Return only a JSON object with "
            "title, description, acceptance_criteria (an array of strings), and priority. "
            "Do not propose code.\n\nTranscript:\n" + transcript
        )
        try:
            content = self._chat(self.settings.triage_model, prompt, temperature=0.1)
            parsed = self._parse_json_object(content)
            self._validate_specification(parsed)
            return ModelResult(parsed, "openrouter")
        except (OpenRouterError, ValueError, KeyError, TypeError):
            return ModelResult(self._fixture_specification(transcript), "fixture-fallback")

    def execute_review(self, specification: dict[str, Any]) -> ModelResult:
        fixture = {
            "decision": "approved",
            "checks": [
                "Unauthenticated requests return 401.",
                "A valid demo bearer token returns 200.",
                "The patch changes only the demo application endpoint.",
            ],
        }
        if self.settings.run_mode != "LIVE" or not self.settings.openrouter_api_key:
            return ModelResult(fixture, "fixture")
        prompt = (
            "Act as a concise peer reviewer. Review the following feature specification "
            "for a fixed FastAPI bearer-token demo patch. Return only JSON with decision "
            "and checks (array of strings).\n\n" + json.dumps(specification)
        )
        try:
            content = self._chat(self.settings.review_model, prompt, temperature=0.1)
            parsed = self._parse_json_object(content)
            if not isinstance(parsed.get("checks"), list):
                raise ValueError("review checks must be a list")
            return ModelResult(parsed, "openrouter")
        except (OpenRouterError, ValueError, KeyError, TypeError):
            return ModelResult(fixture, "fixture-fallback")

    def _chat(self, model: str, prompt: str, temperature: float) -> str:
        response = requests.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": 700,
            },
            timeout=(3, 20),
        )
        if not response.ok:
            raise OpenRouterError(f"OpenRouter returned HTTP {response.status_code}")
        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as error:
            raise OpenRouterError("OpenRouter returned an unexpected response") from error
        if not isinstance(content, str):
            raise OpenRouterError("OpenRouter returned non-text content")
        return content

    @staticmethod
    def _parse_json_object(content: str) -> dict[str, Any]:
        cleaned = content.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
        try:
            value = json.loads(cleaned)
        except json.JSONDecodeError as error:
            # Reasoning models may preface an otherwise valid final JSON object with text.
            first_object = cleaned.find("{")
            if first_object < 0:
                raise ValueError("model did not return JSON") from error
            try:
                value, _ = json.JSONDecoder().raw_decode(cleaned[first_object:])
            except json.JSONDecodeError as nested_error:
                raise ValueError("model did not return a valid JSON object") from nested_error
        if not isinstance(value, dict):
            raise ValueError("model did not return an object")
        return value

    @staticmethod
    def _validate_specification(specification: dict[str, Any]) -> None:
        if not all(isinstance(specification.get(key), str) for key in ("title", "description")):
            raise ValueError("specification lacks title or description")
        if not isinstance(specification.get("acceptance_criteria"), list):
            raise ValueError("specification lacks acceptance criteria")

    @staticmethod
    def _fixture_specification(transcript: str) -> dict[str, Any]:
        return {
            "title": "Add premium subscription validation endpoint",
            "description": (
                "Add a protected FastAPI endpoint that demonstrates premium access only "
                "for callers presenting the configured bearer token. Source context: "
                + transcript[:280]
            ),
            "acceptance_criteria": [
                "GET /premium returns 401 without a valid Authorization bearer token.",
                "GET /premium returns 200 for the configured demo premium token.",
                "The local verification suite passes before a draft PR is created.",
            ],
            "priority": "P0",
        }
