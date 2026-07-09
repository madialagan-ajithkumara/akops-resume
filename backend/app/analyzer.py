"""
Rule-based / local-ML resume analysis: skill detection, job-readiness
scoring (+ its real breakdown into ATS Compatibility / Skills Match /
Content Quality / Impact & Clarity), experience-level and length
estimates, template-based summary, strengths, skills-to-learn-next and
best career matches. Everything here is deterministic Python + the
local classifier -- no paid AI API is called anywhere in this module.
"""
import re

from .classifier import career_classifier
from .resume_gate import assess_resume_likelihood
from .skills_data import (
    CAREER_SKILLS,
    SOFT_SKILLS,
    ACTION_VERBS,
    RESUME_SECTION_HINTS,
    SKILL_ALIASES,
    master_skill_list,
)

_MASTER_SKILLS = master_skill_list()


# Skills whose plain-text match is ambiguous with an unrelated, more common
# term. If any of the "unless near" phrases appear close by, skip the match
# -- e.g. "Cisco IOS" (a switch/router OS) getting misread as the "ios"
# (Apple mobile) skill.
_AMBIGUOUS_SKILL_GUARDS = {
    "ios": ["cisco ios", "cisco", "catalyst"],
}


def _find_skills(text: str, vocabulary: list[str]) -> list[str]:
    """Case-insensitive whole-word/phrase matching against a skill vocabulary."""
    lowered = text.lower()
    found = []
    for skill in vocabulary:
        skill_lower = skill.lower()
        pattern = r"(?<![a-z0-9])" + re.escape(skill_lower) + r"(?![a-z0-9])"
        match = re.search(pattern, lowered)
        if not match:
            continue
        guards = _AMBIGUOUS_SKILL_GUARDS.get(skill_lower)
        if guards:
            window = lowered[max(0, match.start() - 20):match.end() + 20]
            if any(g in window for g in guards):
                continue
        found.append(skill)
    return found


def _canonical_lookup() -> dict[str, str]:
    """lowercase skill text -> its exact-cased canonical form, for alias resolution."""
    return {s.lower(): s for s in _MASTER_SKILLS}


_CANONICAL_BY_LOWER = None


def detect_skills(text: str) -> list[str]:
    global _CANONICAL_BY_LOWER
    if _CANONICAL_BY_LOWER is None:
        _CANONICAL_BY_LOWER = _canonical_lookup()

    found = _find_skills(text, _MASTER_SKILLS)
    found_lower = {s.lower() for s in found}

    lowered_text = text.lower()
    for alias, canonical in SKILL_ALIASES.items():
        canonical_lower = canonical.lower()
        if canonical_lower in found_lower:
            continue
        pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"
        if re.search(pattern, lowered_text):
            resolved = _CANONICAL_BY_LOWER.get(canonical_lower)
            if resolved:
                found.append(resolved)
                found_lower.add(canonical_lower)

    return found


def detect_soft_skills(text: str) -> list[str]:
    return _find_skills(text, SOFT_SKILLS)


def _count_matches(text: str, words: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for w in words if re.search(r"(?<![a-z0-9])" + re.escape(w.lower()) + r"(?![a-z0-9])", lowered))


def _score_components(text: str, detected_skills: list[str]) -> dict:
    """
    The raw, capped point components behind the overall job-readiness score.
    Kept separate from compute_job_readiness_score() so the same real numbers
    can be re-used for the ATS/Skills/Content/Impact breakdown instead of
    inventing separate, unrelated metrics.
    """
    skill_pts = min(35, len(detected_skills) * 2.5)

    verb_hits = _count_matches(text, ACTION_VERBS)
    verb_pts = min(20, verb_hits * 2)

    quantified = len(re.findall(r"\b\d{1,3}(\.\d+)?\s?%|\$\s?\d+|\b\d+\+?\s?(years|months|users|clients|servers|projects)\b", text.lower()))
    quantified_pts = min(15, quantified * 3)

    sections_present = _count_matches(text, RESUME_SECTION_HINTS)
    sections_pts = min(15, sections_present * 3)

    soft_hits = len(detect_soft_skills(text))
    soft_pts = min(10, soft_hits * 2)

    word_count = len(text.split())
    if 150 <= word_count <= 1200:
        length_pts = 5
    elif word_count > 50:
        length_pts = 2
    else:
        length_pts = 0

    return {
        "skill_pts": skill_pts,
        "verb_pts": verb_pts,
        "quantified_pts": quantified_pts,
        "sections_pts": sections_pts,
        "soft_pts": soft_pts,
        "length_pts": length_pts,
        "sections_present": sections_present,
        "word_count": word_count,
    }


def compute_job_readiness_score(text: str, detected_skills: list[str]) -> int:
    """
    0-100 score blended from several free, local signals:
      - breadth of recognized technical skills (cap 35 pts)
      - achievement / action-verb usage (cap 20 pts)
      - quantified impact, e.g. "reduced cost by 30%" (cap 15 pts)
      - resume structure / expected sections present (cap 15 pts)
      - soft skills mentioned (cap 10 pts)
      - length sanity check (cap 5 pts)
    """
    c = _score_components(text, detected_skills)
    total = c["skill_pts"] + c["verb_pts"] + c["quantified_pts"] + c["sections_pts"] + c["soft_pts"] + c["length_pts"]
    return int(round(min(100, max(0, total))))


def score_label(score: int) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Great"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Needs Improvement"
    return "Needs Work"


def score_message(score: int) -> str:
    label = score_label(score)
    messages = {
        "Excellent": "Your resume is in excellent shape and well-aligned with what recruiters and ATS systems look for.",
        "Great": "Your resume is great, with just a few small tweaks left to make it even stronger.",
        "Good": "Your resume is good, but there are a few areas you can improve to increase your chances of getting interviews.",
        "Needs Improvement": "Your resume needs some work — a handful of key improvements would meaningfully raise your chances.",
        "Needs Work": "Your resume needs significant work before it's ready to send out — start with the suggestions below.",
    }
    return messages[label]


def compute_score_breakdown(text: str, detected_skills: list[str]) -> dict:
    """
    Real sub-scores derived from the SAME already-computed signals behind the
    overall job-readiness score (see _score_components) plus resume_gate's
    structure/contact-info signals -- nothing here is a separately invented
    number. Each is 0-100:
      - skills_match: breadth of recognized technical skills
      - impact_clarity: action-verb usage + quantified achievements
      - content_quality: structure completeness + soft skills + length
      - ats_compatibility: how parseable this resume would be for a real
        ATS -- standard section headers present, contact info detectable,
        and a sane length (real ATS tools check exactly these things)
    """
    c = _score_components(text, detected_skills)
    gate = assess_resume_likelihood(text)

    skills_match = round(c["skill_pts"] / 35 * 100)
    impact_clarity = round((c["verb_pts"] + c["quantified_pts"]) / (20 + 15) * 100)
    content_quality = round((c["sections_pts"] + c["soft_pts"] + c["length_pts"]) / (15 + 10 + 5) * 100)

    ats = 100
    if not gate["has_email"]:
        ats -= 20
    if not gate["has_phone"]:
        ats -= 10
    if gate["section_hits"] < 3:
        ats -= (3 - gate["section_hits"]) * 10
    if c["word_count"] < 150:
        ats -= 15
    elif c["word_count"] > 1200:
        ats -= 10
    ats = max(0, min(100, ats))

    return {
        "ats_compatibility": ats,
        "skills_match": skills_match,
        "content_quality": max(0, min(100, content_quality)),
        "impact_clarity": max(0, min(100, impact_clarity)),
    }


_YEARS_RE = re.compile(r"(\d{1,2})\+?\s*(?:years|yrs)\b", re.IGNORECASE)
_SENIOR_WORDS = ["senior", "lead", "principal", "staff engineer", "manager", "director", "head of", "architect"]
_ENTRY_WORDS = ["intern", "internship", "junior", "entry level", "entry-level", "graduate", "trainee", "fresher"]


def infer_experience_level(text: str) -> str:
    lowered = text.lower()
    years_found = [int(m) for m in _YEARS_RE.findall(lowered)]
    max_years = max(years_found) if years_found else None

    if max_years is not None:
        if max_years >= 8:
            return "Senior-Level"
        if max_years >= 3:
            return "Mid-Level"
        return "Entry-Level"

    if any(w in lowered for w in _SENIOR_WORDS):
        return "Senior-Level"
    if any(w in lowered for w in _ENTRY_WORDS):
        return "Entry-Level"
    return "Mid-Level"


def estimate_pages(word_count: int) -> str:
    """Rough estimate only (~500-550 words/page is typical for a resume) -- not exact pagination."""
    if word_count <= 550:
        return "1 Page"
    if word_count <= 1100:
        return "2 Pages"
    return "3+ Pages"


def build_strengths(detected_skills: list[str]) -> list[dict]:
    """Group the resume's detected skills under whichever categories they belong to,
    ranked by how many of that category's core skills were matched."""
    detected_lower = {s.lower() for s in detected_skills}
    ranked = []
    for category, data in CAREER_SKILLS.items():
        matched = [s for s in data["core"] if s.lower() in detected_lower]
        if matched:
            ranked.append({"category": category, "skills": matched})
    ranked.sort(key=lambda x: len(x["skills"]), reverse=True)
    return ranked[:5]


def build_skills_to_learn(text: str, top_categories: list[str], detected_skills: list[str], limit: int = 6) -> list[str]:
    detected_lower = {s.lower() for s in detected_skills}
    suggestions = []
    seen = set()
    for category in top_categories:
        data = CAREER_SKILLS.get(category)
        if not data:
            continue
        for skill in data["next"] + data["core"]:
            if skill.lower() not in detected_lower and skill.lower() not in seen:
                seen.add(skill.lower())
                suggestions.append(skill)
        if len(suggestions) >= limit:
            break
    return suggestions[:limit]


def build_career_matches(text: str, detected_skills: list[str] | None = None, k: int = 8) -> list[dict]:
    """
    Classify on the curated skill list, not the raw resume prose.

    The classifier is trained on short skill-keyword strings (see
    classifier.py's synthetic training docs), so at inference time it needs
    input from the same distribution. Feeding it a full paragraph of natural
    resume prose lets incidental words that coincidentally overlap with a
    category's vocabulary (e.g. "RDS", "performance", "security") outvote the
    resume's actual, dominant skill signal. Classifying on the already
    skill-detected keywords keeps the signal clean and matches how the model
    was trained.

    k defaults to 8 (not just the top few) so the frontend can show a short
    "top matches" list plus a "view detailed job matches" expansion without
    a second API round-trip.
    """
    if detected_skills is None:
        detected_skills = detect_skills(text)
    classify_input = " ".join(detected_skills) if detected_skills else text

    predictions = career_classifier.predict_top_k(classify_input, k=k)
    total = sum(p for _, p in predictions) or 1.0
    return [
        {"title": category, "match_percent": round((prob / total) * 100)}
        for category, prob in predictions
    ]


_ACRONYMS = {
    "aws", "gcp", "sql", "api", "ci/cd", "iam", "vpc", "rest api", "iot", "seo", "sem",
    "ppc", "hr", "ux", "ui", "ats", "pmp", "okrs", "dax", "vba", "nft", "sla", "slo",
    "rtos", "arm", "sdn", "hrms", "ui/ux",
}


def _display_skill(skill: str) -> str:
    lowered = skill.lower()
    if lowered in _ACRONYMS:
        return lowered.upper()
    return " ".join(w if w in ("and", "of") else w.capitalize() for w in skill.split(" "))


def build_improvement_suggestions(breakdown: dict, skills_to_learn: list[str], limit: int = 6) -> list[dict]:
    """
    Short, actionable suggestions for the "Areas to Improve" card. Every item
    here is derived from an already-computed, real signal (the score
    breakdown or the skill-gap list) -- nothing is generic filler text.
    """
    suggestions = []

    if breakdown.get("ats_compatibility", 100) < 80:
        suggestions.append({
            "title": "Improve ATS Compatibility",
            "description": "Make sure your email/phone are easy to find and use standard section headers (Experience, Education, Skills).",
        })
    if breakdown.get("impact_clarity", 100) < 70:
        suggestions.append({
            "title": "Add Quantifiable Results",
            "description": "Use numbers to show impact, e.g. \"reduced deployment time by 30%\" instead of just listing duties.",
        })
    if breakdown.get("content_quality", 100) < 70:
        suggestions.append({
            "title": "Improve Summary & Structure",
            "description": "Make your summary more specific and concise, and double-check all key sections are present.",
        })
    if breakdown.get("skills_match", 100) < 60:
        suggestions.append({
            "title": "Add More Technical Skills",
            "description": "Your resume lists fewer recognized skills than typical for the roles you're matching to.",
        })

    for skill in skills_to_learn[:4]:
        label = _display_skill(skill)
        suggestions.append({
            "title": f"Add {label}",
            "description": f"{label} shows up often in your best-fit roles but wasn't detected on your resume.",
        })

    return suggestions[:limit]


def build_summary(detected_skills: list[str], strengths: list[dict]) -> str:
    if not strengths:
        top_terms = ", ".join(detected_skills[:6]) or "a developing technical background"
        return f"Professional with early-stage experience in {top_terms}. Keep building hands-on projects to strengthen your profile."

    groups = []
    for s in strengths[:3]:
        groups.append(", ".join(s["skills"][:3]))
    joined = " | ".join(groups)
    return f"Professional with expertise in {joined}. Strong technical skills across multiple domains."


def analyze_resume(text: str) -> dict:
    detected_skills = detect_skills(text)
    strengths = build_strengths(detected_skills)
    career_matches = build_career_matches(text, detected_skills)
    top_categories = [c["title"] for c in career_matches]
    skills_to_learn = build_skills_to_learn(text, top_categories, detected_skills)
    score = compute_job_readiness_score(text, detected_skills)
    breakdown = compute_score_breakdown(text, detected_skills)
    summary = build_summary(detected_skills, strengths)
    word_count = len(text.split())

    return {
        "job_readiness_score": score,
        "score_label": score_label(score),
        "score_message": score_message(score),
        "score_breakdown": breakdown,
        "experience_level": infer_experience_level(text),
        "estimated_pages": estimate_pages(word_count),
        "file_type": "PDF",
        "summary": summary,
        "strengths": strengths,
        "skills_to_learn": skills_to_learn,
        "improvement_suggestions": build_improvement_suggestions(breakdown, skills_to_learn),
        "career_matches": career_matches,
        "detected_skills": detected_skills,
    }
