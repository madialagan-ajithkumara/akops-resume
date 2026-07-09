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
import urllib.request
import urllib.error

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
_TIMEOUT_SECONDS = 20


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
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Gemini API error {e.code}: {detail[:300]}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Could not reach Gemini API: {e.reason}") from e

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected Gemini response shape: {data}") from e
