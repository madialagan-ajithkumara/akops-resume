"""
Minimal shared HTTP client for calling Google's Gemini API via raw REST
(urllib.request, stdlib only -- no new pip dependency). Both llm_enhance.py
(Enhanced Mode) and chat_assist.py (Resume Chat Assistant) import this for
the actual network call, but each owns its OWN daily budget guard/counter
so the two features can never starve each other's quota.

No key is ever accepted from or exposed to the browser/client -- it is
read from the GEMINI_API_KEY environment variable on the server only.
"""
import json
import os
import time
import urllib.request
import urllib.error

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
_TIMEOUT_SECONDS = 20

# Google's model endpoints occasionally return 503 ("model is currently
# experiencing high demand") or 429 (rate limited) for a moment under load --
# these are transient, not our fault and not the user's. Retry a couple of
# times with a short backoff before giving up, and turn the final failure
# into a plain-English message instead of dumping raw API JSON at the user.
_RETRYABLE_CODES = {503, 429}
_MAX_RETRIES = 2
_BACKOFF_SECONDS = 1.5


def is_configured() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY"))


def call_gemini(prompt: str, temperature: float = 0.4, max_output_tokens: int = 500) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set on the server.")

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_output_tokens},
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{GEMINI_API_URL}?key={api_key}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    last_error = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT_SECONDS) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return _extract_text(data)
        except urllib.error.HTTPError as e:
            if e.code in _RETRYABLE_CODES and attempt < _MAX_RETRIES:
                last_error = e
                time.sleep(_BACKOFF_SECONDS * (attempt + 1))
                continue
            if e.code in _RETRYABLE_CODES:
                raise RuntimeError(
                    "Google's Gemini service is temporarily overloaded. Please try again in a moment."
                ) from e
            detail = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Gemini API error {e.code}: {detail[:300]}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Could not reach Gemini API: {e.reason}") from e

    raise RuntimeError("Google's Gemini service is temporarily overloaded. Please try again in a moment.") from last_error


def _extract_text(data: dict) -> str:
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected Gemini response shape: {data}") from e
