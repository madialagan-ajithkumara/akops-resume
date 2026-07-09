"""
"Is this actually a resume?" sanity gate.

Without this, any PDF with enough overlapping vocabulary (industry reports,
whitepapers, survey results, textbooks...) can score highly and get matched
to a career track, purely because it happens to mention the same technical
words a resume in that field would. A database industry report full of
"SQL", "PostgreSQL", "Oracle" is a good example -- lots of skill-keyword
overlap, zero resemblance to an actual CV.

This is a deliberately simple, explainable point-based heuristic (no extra
ML model, no extra cost) combining several independently weak signals so
that no single false signal misfires alone:
  - resume length is short (a few hundred to ~1500 words); reports/
    whitepapers are typically much longer
  - a resume almost always has an email and/or phone number near the top
  - reports/whitepapers use recognizable report language ("key findings",
    "methodology", "respondents", "copyright", "all rights reserved"...)
  - resumes usually contain at least one typical section header
    (experience, education, skills...)
"""
import re

from .skills_data import RESUME_SECTION_HINTS

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"(\+?\d[\d\-\s().]{8,}\d)")

# Phrases that show up constantly in reports, whitepapers, surveys, and
# research summaries, but essentially never in an individual's resume.
REPORT_KEYWORDS = [
    "table of contents", "key findings", "executive summary", "survey",
    "respondents", "methodology", "copyright", "all rights reserved",
    "whitepaper", "white paper", "confidential", "proprietary",
    "this report", "annual report", "state of the", "sample size",
    "n=", "case study", "market research", "industry report",
]

REJECT_THRESHOLD = 4


def assess_resume_likelihood(text: str) -> dict:
    lowered = text.lower()
    word_count = len(text.split())

    has_email = bool(_EMAIL_RE.search(text))
    has_phone = bool(_PHONE_RE.search(text))
    report_hits = sum(1 for kw in REPORT_KEYWORDS if kw in lowered)
    section_hits = sum(1 for s in RESUME_SECTION_HINTS if re.search(r"(?<![a-z])" + re.escape(s) + r"(?![a-z])", lowered))

    score = 0
    reasons = []

    if word_count > 2500:
        score += 2
        reasons.append("much longer than a typical resume")
    elif word_count > 1500:
        score += 1
        reasons.append("longer than a typical resume")

    if not has_email and not has_phone:
        score += 2
        reasons.append("no email or phone number found")
    elif not has_email:
        score += 1

    if report_hits >= 4:
        score += 3
        reasons.append("reads like a report/whitepaper, not a CV")
    elif report_hits >= 2:
        score += 1

    if section_hits == 0:
        score += 1
        reasons.append("no resume sections (experience, education, skills...) detected")

    return {
        "is_resume": score < REJECT_THRESHOLD,
        "score": score,
        "reasons": reasons,
        "word_count": word_count,
        "has_email": has_email,
        "has_phone": has_phone,
        "report_hits": report_hits,
        "section_hits": section_hits,
    }


def looks_like_resume(text: str) -> bool:
    return assess_resume_likelihood(text)["is_resume"]
