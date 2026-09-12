"""Exa AI Neural Search Client for live technical grounding."""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

def log(msg: str) -> None:
    sys.stderr.write(f"[EXA CLIENT] {msg}\n")
    sys.stderr.flush()

def _load_fallback_grounding() -> List[Dict[str, str]]:
    mock_path = Path(__file__).resolve().parent.parent.parent / "mock_data.json"
    if mock_path.exists():
        try:
            with open(mock_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("scenario_1_dev", {}).get("exa_grounding", [])
        except Exception as e:
            log(f"Error loading fallback grounding: {e}")
    return [
        {
            "title": "OAuth 2.0 and JWT Refresh Token Best Practices",
            "url": "https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation",
            "summary": "Refresh token rotation issues a new refresh token every time the current refresh token is exchanged. Blacklist revoked tokens with Redis TTL."
        }
    ]

def search_technical_docs(query: str, num_results: int = 2) -> List[Dict[str, str]]:
    """Performs real-time neural search via Exa AI to retrieve verified technical citations."""
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        log("EXA_API_KEY not set. Using offline fallback citations.")
        return _load_fallback_grounding()

    try:
        from exa_py import Exa
        exa = Exa(api_key=api_key)
        log(f"Executing Exa neural search for: '{query}'")
        res = exa.search(
            query,
            type="neural",
            num_results=num_results
        )

        results: List[Dict[str, str]] = []
        for item in res.results:
            text = getattr(item, "text", "") or getattr(item, "highlights", "") or ""
            if isinstance(text, list):
                text = " ".join(text)
            snippet = str(text).strip()[:350]
            results.append({
                "title": getattr(item, "title", "Technical Documentation"),
                "url": getattr(item, "url", ""),
                "summary": snippet
            })
        
        if results:
            log(f"Exa search returned {len(results)} high-signal citations.")
            return results
        return _load_fallback_grounding()

    except Exception as e:
        log(f"Exa search encountered error: {e}. Falling back to cached citations.")
        return _load_fallback_grounding()
