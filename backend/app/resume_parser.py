"""
Heuristic, fully-local resume-to-structured-JSON parser.

No AI API calls -- section headers and entry boundaries are detected with
regex/keyword heuristics. It won't be perfect on every resume layout (real
NER-based parsing would need a trained model), so the frontend lets the
user add/remove/edit anything this gets wrong before exporting. That
human-in-the-loop edit step is the safety net for parsing imperfection.
"""
import re

from .skills_data import CAREER_SKILLS, ACTION_VERBS
from .analyzer import detect_skills

EMAIL_RE = re.compile(r"[\w.\-+]+@[\w\-]+\.[\w.\-]+")
PHONE_RE = re.compile(r"(\+?\d[\d\-\s()]{7,}\d)")
LINKEDIN_RE = re.compile(r"(linkedin\.com/[^\s,|]+)", re.I)
GITHUB_RE = re.compile(r"(github\.com/[^\s,|]+)", re.I)

MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
DATE_RANGE_RE = re.compile(
    rf"((?:{MONTH}\s*)?\d{{4}})\s*(?:-|–|to|—)\s*((?:{MONTH}\s*)?\d{{4}}|present|current)",
    re.I,
)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
DECORATIVE_RE = re.compile(r"^[\s_\-=~•●∙\.]{4,}$")
LEADING_DECOR_RE = re.compile(r"^[\s_\-=~•●∙\.]{4,}")

SECTION_HEADERS = {
    "summary": ["summary", "professional summary", "objective", "career objective", "profile", "about me"],
    "experience": ["experience", "work experience", "professional experience", "employment history",
                   "work history", "company details"],
    "education": ["education", "education details", "academic background", "academic details"],
    "skills": ["skills", "technical skills", "skill details", "core competencies", "key skills",
               "skills & abilities", "hard skills"],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "certifications": ["certifications", "certificates", "certification", "licenses & certifications"],
}

DEGREE_KEYWORDS = [
    "b.tech", "btech", "b.e", "be ", "bachelor", "m.tech", "mtech", "m.e", "master",
    "mba", "phd", "ph.d", "diploma", "b.sc", "bsc", "m.sc", "msc", "bca", "mca",
    "hsc", "12th", "10th", "ssc", "b.com", "m.com", "associate", "undergraduate",
    "postgraduate", "post graduate", "pgdm",
]

LANGUAGE_NOISE = [
    "english", "german", "french", "spanish", "hindi", "tamil", "telugu", "kannada",
    "mandarin", "chinese", "japanese", "korean", "arabic", "portuguese", "italian",
    "russian", "native", "fluent", "conversational", "proficient", "intermediate",
]

BULLET_PREFIX_RE = re.compile(r"^[\-\*•●▪‣⁃]\s*")
BULLET_SPLIT_RE = re.compile(r"[•●▪‣⁃]")


def _split_into_bullets(line: str) -> list[str]:
    """
    Some PDFs extract several bullet points onto a single text line, e.g.
    "Did X.● Did Y.● Did Z." with no newline between them. Split on the
    bullet glyph itself (not just at line-start) so each becomes its own item.
    """
    if not BULLET_SPLIT_RE.search(line):
        return [line] if line.strip() else []
    parts = BULLET_SPLIT_RE.split(line)
    return [p.strip(" -\t") for p in parts if p.strip(" -\t")]


def _clean(line: str) -> str:
    return line.strip().strip("|,;").strip()


def _is_decorative(line: str) -> bool:
    return bool(DECORATIVE_RE.match(line.strip())) or len(line.strip()) == 0


def _strip_leading_decoration(line: str) -> str:
    """Drop a leading run of divider characters glued onto real text on the
    same line, e.g. "____________Resume Worded" -> "Resume Worded"."""
    return LEADING_DECOR_RE.sub("", line)


def _is_header(line: str) -> str | None:
    """
    Detect a section header even when it has extra words around the keyword
    (e.g. "RELEVANT WORK EXPERIENCE", "MY TECHNICAL SKILLS") -- real resumes
    rarely use the bare canonical word alone. Matching is keyword-contains
    rather than exact-equals, bounded by a short overall line length so we
    don't misfire on prose sentences that happen to mention "experience".
    """
    raw = line.strip()
    if not raw:
        return None
    check = raw.split(":", 1)[0] if ":" in raw[:40] else raw
    stripped = check.lower().rstrip(":").strip()
    if not stripped or len(stripped.split()) > 6:
        return None
    best = None
    for canonical, keywords in SECTION_HEADERS.items():
        for kw in keywords:
            pattern = r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])"
            if re.search(pattern, stripped) and (best is None or len(kw) > len(best[1])):
                best = (canonical, kw)
    return best[0] if best else None


def _extract_contact(text: str, lines: list[str]) -> dict:
    email_m = EMAIL_RE.search(text)
    phone_m = PHONE_RE.search(text)
    linkedin_m = LINKEDIN_RE.search(text)
    github_m = GITHUB_RE.search(text)

    name = ""
    for line in lines[:15]:
        c = _clean(line)
        if not c:
            continue
        # Some templates pack "Name • Title • City • Phone • Email" onto one line.
        if "•" in c and (EMAIL_RE.search(c) or PHONE_RE.search(c)):
            first_seg = _clean(c.split("•")[0])
            if first_seg and len(first_seg.split()) <= 6 and not EMAIL_RE.search(first_seg) and not any(ch.isdigit() for ch in first_seg):
                name = first_seg
                break
            continue
        if len(c.split()) > 6:
            continue
        if EMAIL_RE.search(c) or PHONE_RE.search(c) or _is_header(c):
            continue
        if any(ch.isdigit() for ch in c):
            continue
        name = c
        break

    return {
        "name": name or "Your Name",
        "email": email_m.group(0) if email_m else "",
        "phone": phone_m.group(0).strip() if phone_m else "",
        "linkedin": linkedin_m.group(0) if linkedin_m else "",
        "github": github_m.group(0) if github_m else "",
    }


def _split_sections(lines: list[str]) -> dict:
    sections: dict[str, list[str]] = {k: [] for k in SECTION_HEADERS}
    sections["preamble"] = []
    current = "preamble"
    for line in lines:
        if _is_decorative(line):
            continue
        header = _is_header(line)
        if header:
            current = header
            # Keep inline content that rides on the same line as the header,
            # e.g. "Hard Skills: Security Auditing, Dependency Scanning".
            if ":" in line:
                after = line.split(":", 1)[1].strip()
                if len(after) > 3:
                    sections[current].append(after)
            continue
        if line.strip():
            sections[current].append(line)
    return sections


def _parse_skills(section_lines: list[str], full_text: str) -> list[dict]:
    raw = " ".join(section_lines) if section_lines else ""
    tokens = set()
    if raw:
        for chunk in re.split(r"[,;|\n]| - ", raw):
            chunk = _clean(chunk)
            low = chunk.lower()
            if not chunk or len(chunk) >= 40:
                continue
            if any(noise in low for noise in LANGUAGE_NOISE):
                continue
            tokens.add(chunk)

    # Always scan the FULL resume text for known skills -- many resumes only
    # mention half their tools in prose (experience bullets), not in a
    # dedicated skills list, so limiting detection to the skills section
    # alone misses most of the real signal.
    recognized = set(s.lower() for s in detect_skills(full_text))

    candidates = []
    for category, data in CAREER_SKILLS.items():
        matched = [s for s in (data["core"] + data["next"]) if s.lower() in recognized]
        if matched:
            candidates.append({"category": category, "skills": matched})

    candidates.sort(key=lambda c: len(c["skills"]), reverse=True)
    strong = [c for c in candidates if len(c["skills"]) >= 2]
    grouped = (strong or candidates)[:6]

    used = set()
    for c in grouped:
        used.update(s.lower() for s in c["skills"])

    leftover = sorted({t for t in tokens if t.lower() not in used and len(t) > 1})
    if leftover:
        grouped.append({"category": "Other", "skills": leftover[:20]})

    if not grouped and tokens:
        grouped.append({"category": "Skills", "skills": sorted(tokens)[:25]})

    return grouped


def _blocks_from_lines(lines: list[str]) -> list[list[str]]:
    """Split a section's lines into entries using blank-ish boundaries and date-range hints."""
    lines = [l for l in lines if not _is_decorative(l)]
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        starts_new = bool(DATE_RANGE_RE.search(line)) and current and not BULLET_PREFIX_RE.match(line)
        if starts_new:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks if blocks else ([lines] if lines else [])


def _looks_like_bullet_sentence(line: str) -> bool:
    words = line.strip().split()
    if not words:
        return False
    first_word = words[0].strip(".,").lower()
    return (
        BULLET_PREFIX_RE.match(line) is not None
        or first_word in ACTION_VERBS
        or line.strip().endswith(".")
        or len(words) > 12
    )


def _parse_experience(lines: list[str]) -> list[dict]:
    entries = []
    for block in _blocks_from_lines(lines):
        if not block:
            continue
        header_line = block[0]
        date_m = DATE_RANGE_RE.search(header_line)
        dates = f"{date_m.group(1)} - {date_m.group(2)}" if date_m else ""
        header_clean = DATE_RANGE_RE.sub("", header_line).strip(" -|,")

        title, company = "", ""
        rest_of_block = block[1:]
        if header_clean and not _looks_like_bullet_sentence(header_clean):
            title, company = header_clean, ""
            for sep in [" at ", " - ", " – ", "|", ","]:
                if sep in header_clean:
                    parts = header_clean.split(sep, 1)
                    title, company = parts[0].strip(), parts[1].strip()
                    break
        else:
            # First line is already a bullet/sentence, not a "Title - Company" header;
            # keep it as the first bullet instead of misreading it as a job title.
            rest_of_block = block

        bullets = []
        for line in rest_of_block:
            for fragment in _split_into_bullets(line):
                c = _clean(BULLET_PREFIX_RE.sub("", fragment))
                if c and not _is_header(c):
                    bullets.append(c)

        if title or company or bullets:
            entries.append({
                "title": title or "Role",
                "company": company,
                "dates": dates,
                "bullets": bullets[:8],
            })
    return entries[:8]


def _parse_education(lines: list[str]) -> list[dict]:
    entries = []
    for block in _blocks_from_lines(lines):
        joined = " ".join(_clean(l) for l in block if _clean(l))
        if not joined:
            continue

        date_m = DATE_RANGE_RE.search(joined)
        year_m = YEAR_RE.search(joined)
        if date_m:
            dates = f"{date_m.group(1)} - {date_m.group(2)}"
        elif year_m:
            dates = year_m.group(0)
        else:
            dates = ""

        degree = ""
        lower = joined.lower()
        degree_idx = None
        for kw in DEGREE_KEYWORDS:
            if kw in lower:
                degree_idx = lower.find(kw)
                degree = joined[degree_idx:degree_idx + 60].strip(" .,-")
                break

        # Institution: whatever text comes before the year/degree, whichever is first --
        # handles both normal multi-line entries and PDFs that glue
        # "Institution Name 2019Bachelor of Science" onto a single line.
        cut_idx = len(joined)
        if year_m:
            cut_idx = min(cut_idx, year_m.start())
        if degree_idx is not None:
            cut_idx = min(cut_idx, degree_idx)
        candidate = joined[:cut_idx].strip(" .,-")
        institution = candidate if candidate and len(candidate.split()) <= 14 else ""

        if not institution and not degree:
            # Fall back to the raw first line if nothing else was extractable.
            institution = _clean(block[0])[:80] if block else ""

        if degree or institution:
            entries.append({"degree": degree or "Degree", "institution": institution, "dates": dates})
    return entries[:6]


def _parse_projects(lines: list[str]) -> list[dict]:
    entries = []
    for block in _blocks_from_lines(lines):
        if not block:
            continue
        title = _clean(BULLET_PREFIX_RE.sub("", block[0]))
        bullets = []
        for line in block[1:]:
            for fragment in _split_into_bullets(line):
                c = _clean(BULLET_PREFIX_RE.sub("", fragment))
                if c and not _is_header(c):
                    bullets.append(c)
        if title:
            entries.append({"title": title, "bullets": bullets[:6]})
    return entries[:6]


def _parse_flat_list(lines: list[str]) -> list[str]:
    items = []
    for line in lines:
        if _is_decorative(line):
            continue
        for chunk in re.split(r"[,|\n]", line):
            c = _clean(BULLET_PREFIX_RE.sub("", chunk))
            if c:
                items.append(c)
    return items[:10]


def parse_resume(text: str) -> dict:
    lines = [_strip_leading_decoration(l) for l in text.split("\n")]
    contact = _extract_contact(text, [l for l in lines if l.strip()])
    sections = _split_sections(lines)

    summary = " ".join(_clean(l) for l in sections["summary"] if _clean(l))
    if not summary:
        preamble_text = " ".join(_clean(l) for l in sections["preamble"] if _clean(l) and l != contact["name"])
        preamble_text = EMAIL_RE.sub("", preamble_text)
        preamble_text = PHONE_RE.sub("", preamble_text)
        if len(preamble_text) > 40:
            summary = preamble_text[:600]

    return {
        "contact": contact,
        "summary": summary,
        "skill_categories": _parse_skills(sections["skills"], text),
        "experience": _parse_experience(sections["experience"]),
        "education": _parse_education(sections["education"]),
        "projects": _parse_projects(sections["projects"]),
        "certifications": _parse_flat_list(sections["certifications"]),
    }
