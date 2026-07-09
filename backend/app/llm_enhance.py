"""
Optional "Enhanced Mode": if the site owner sets a GEMINI_API_KEY environment
variable (their own free-tier key from Google AI Studio), this calls Gemini
to produce a sharper, more human-written summary and improvement tips on top
of the local analysis. Completely optional -- if no key is configured, every
other feature in this app keeps working exactly as before, for free.

This is the ONLY place in the codebase that ever calls an external AI API,
and it never runs unless the server operator explicitly opts in by setting
the environment variable. No key is ever accepted from or exposed to the
browser/client.
"""
import json
import os
import threading
import urllib.request
import urllib.error
from datetime import datetime, timezone

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
_TIMEOUT_SECONDS = 20

# gemini-2.5-flash-lite's free tier is ~1,000 requests/day at the time this was
# written (Google can change this without notice -- check ai.google.dev/gemini-api/docs/pricing).
# Default to well under that so a burst of traffic never actually exhausts the
# key or gets it rate-limited by Google; the site owner can raise/lower this
# via an env var. This counter is in-memory, so it resets whenever the server
# restarts (e.g. Render free tier spinning down after idle) -- an approximate
# daily budget, not a precise one, but enough to keep behavior predictable
# under real public traffic instead of only failing after Gemini rejects calls.
DAILY_LIMIT = int(os.environ.get("GEMINI_DAILY_LIMIT", "200"))

_lock = threading.Lock()
_usage_date = None
_usage_count = 0


def is_configured() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY"))


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _reset_if_new_day():
    global _usage_date, _usage_count
    today = _today()
    if _usage_date != today:
        _usage_date = today
        _usage_count = 0


def remaining_quota() -> int:
    with _lock:
        _reset_if_new_day()
        return max(0, DAILY_LIMIT - _usage_count)


def has_quota_remaining() -> bool:
    return remaining_quota() > 0


def is_available() -> bool:
    """Configured AND still within today's free-tier safety budget."""
    return is_configured() and has_quota_remaining()


def _record_usage():
    global _usage_count
    with _lock:
        _reset_if_new_day()
        _usage_count += 1


def _call_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set on the server.")

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 500},
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


def enhance_analysis(resume_text: str, base_result: dict) -> dict:
    """
    Ground the LLM in our own deterministic findings (score, detected skills,
    top career match) so it writes *about* real, already-computed facts
    rather than inventing new ones from scratch.
    """
    skills = ", ".join(base_result.get("detected_skills", [])[:20]) or "no specific skills detected"
    top_match = base_result.get("career_matches", [{}])[0].get("title", "unclear")
    score = base_result.get("job_readiness_score", 0)

    prompt = (
        "You are a career coach reviewing a resume. Here is factual data already "
        "computed by a separate analysis tool -- do not contradict it:\n"
        f"- Job readiness score: {score}/100\n"
        f"- Detected skills: {skills}\n"
        f"- Best-fit career track: {top_match}\n\n"
        "Resume text (may be imperfectly extracted from a PDF):\n"
        f"{resume_text[:4000]}\n\n"
        "Write two things, clearly separated by a line that says exactly '---':\n"
        "1. A polished, specific 2-3 sentence professional summary of this candidate "
        "(natural language, no bullet points).\n"
        "2. Three concrete, specific improvement tips as a numbered list, based on "
        "what's actually missing or weak in this resume."
    )

    if not has_quota_remaining():
        raise RuntimeError(
            f"Enhanced mode has hit today's free usage budget ({DAILY_LIMIT} requests). "
            "It resets daily -- the local analysis above is still fully accurate in the meantime."
        )

    raw = _call_gemini(prompt)
    _record_usage()
    if "---" in raw:
        summary_part, tips_part = raw.split("---", 1)
    else:
        summary_part, tips_part = raw, ""

    tips = [line.strip(" .\t") for line in tips_part.strip().split("\n") if line.strip()]
    tips = [re_strip_numbering(t) for t in tips if t]

    return {
        "enhanced_summary": summary_part.strip(),
        "enhanced_tips": tips[:5],
        "enhanced_model": GEMINI_MODEL,
    }


def re_strip_numbering(line: str) -> str:
    import re
    return re.sub(r"^\s*\d+[\.\)]\s*", "", line).strip()
