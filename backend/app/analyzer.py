"""
Rule-based / local-ML resume analysis: skill detection, job-readiness
scoring, template-based summary, strengths, skills-to-learn-next and
best career matches. Everything here is deterministic Python + the
local classifier -- no paid AI API is called anywhere in this module.
"""
import re

from .classifier import career_classifier
from .skills_data import (
    CAREER_SKILLS,
    SOFT_SKILLS,
    ACTION_VERBS,
    RESUME_SECTION_HINTS,
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


def detect_skills(text: str) -> list[str]:
    return _find_skills(text, _MASTER_SKILLS)


def detect_soft_skills(text: str) -> list[str]:
    return _find_skills(text, SOFT_SKILLS)


def _count_matches(text: str, words: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for w in words if re.search(r"(?<![a-z0-9])" + re.escape(w.lower()) + r"(?![a-z0-9])", lowered))


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
    score = 0.0

    skill_pts = min(35, len(detected_skills) * 2.5)
    score += skill_pts

    verb_hits = _count_matches(text, ACTION_VERBS)
    score += min(20, verb_hits * 2)

    quantified = len(re.findall(r"\b\d{1,3}(\.\d+)?\s?%|\$\s?\d+|\b\d+\+?\s?(years|months|users|clients|servers|projects)\b", text.lower()))
    score += min(15, quantified * 3)

    sections_present = _count_matches(text, RESUME_SECTION_HINTS)
    score += min(15, sections_present * 3)

    soft_hits = len(detect_soft_skills(text))
    score += min(10, soft_hits * 2)

    word_count = len(text.split())
    if 150 <= word_count <= 1200:
        score += 5
    elif word_count > 50:
        score += 2

    return int(round(min(100, max(0, score))))


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


def build_career_matches(text: str, detected_skills: list[str] | None = None, k: int = 5) -> list[dict]:
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
    summary = build_summary(detected_skills, strengths)

    return {
        "job_readiness_score": score,
        "summary": summary,
        "strengths": strengths,
        "skills_to_learn": skills_to_learn,
        "career_matches": career_matches,
        "detected_skills": detected_skills,
    }
