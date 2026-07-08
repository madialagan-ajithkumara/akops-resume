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

SECTION_HEADERS = {
    "summary": ["summary", "professional summary", "objective", "career objective", "profile", "about me"],
    "experience": ["experience", "work experience", "professional experience", "employment history",
                   "work history", "company details"],
    "education": ["education", "education details", "academic background", "academic details"],
    "skills": ["skills", "technical skills", "skill details", "core competencies", "key skills",
               "skills & abilities"],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "certifications": ["certifications", "certificates", "certification", "licenses & certifications"],
}

DEGREE_KEYWORDS = [
    "b.tech", "btech", "b.e", "be ", "bachelor", "m.tech", "mtech", "m.e", "master",
    "mba", "phd", "ph.d", "diploma", "b.sc", "bsc", "m.sc", "msc", "bca", "mca",
    "hsc", "12th", "10th", "ssc", "b.com", "m.com",
]

BULLET_PREFIX_RE = re.compile(r"^[\-\*•●▪‣⁃]\s*")


def _clean(line: str) -> str:
    return line.strip().strip("|,;").strip()


def _is_header(line: str) -> str | None:
    stripped = line.strip().lower().rstrip(":").strip()
    if not stripped or len(stripped.split()) > 5:
        return None
    for canonical, keywords in SECTION_HEADERS.items():
        if stripped in keywords:
            return canonical
    return None


def _extract_contact(text: str, lines: list[str]) -> dict:
    email_m = EMAIL_RE.search(text)
    phone_m = PHONE_RE.search(text)
    linkedin_m = LINKEDIN_RE.search(text)
    github_m = GITHUB_RE.search(text)

    name = ""
    for line in lines[:15]:
        c = _clean(line)
        if not c or len(c.split()) > 6:
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
        header = _is_header(line)
        if header:
            current = header
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
            if chunk and len(chunk) < 40:
                tokens.add(chunk)

    source_text = raw if raw else full_text
    recognized = set(s.lower() for s in detect_skills(source_text))

    candidates = []
    for category, data in CAREER_SKILLS.items():
        matched = [s for s in (data["core"] + data["next"]) if s.lower() in recognized]
        if matched:
            candidates.append({"category": category, "skills": matched})

    # Keep only the categories this resume actually leans into: prefer ones with
    # multiple matched skills so a single shared skill (e.g. "python") doesn't
    # spam every tangentially-related category.
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
            c = _clean(BULLET_PREFIX_RE.sub("", line))
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
        joined = " ".join(block)
        date_m = DATE_RANGE_RE.search(joined)
        year_m = re.search(r"\b(19|20)\d{2}\b", joined)
        dates = ""
        if date_m:
            dates = f"{date_m.group(1)} - {date_m.group(2)}"
        elif year_m:
            dates = year_m.group(0)

        degree = ""
        lower = joined.lower()
        for kw in DEGREE_KEYWORDS:
            if kw in lower:
                idx = lower.find(kw)
                degree = joined[idx:idx + 60].split("  ")[0].strip(" .,-")
                break

        institution = ""
        for line in block:
            c = _clean(line)
            if c and c != degree and not DATE_RANGE_RE.search(c) and len(c.split()) <= 12:
                institution = c
                break

        if degree or institution:
            entries.append({"degree": degree or "Degree", "institution": institution, "dates": dates})
    return entries[:6]


def _parse_projects(lines: list[str]) -> list[dict]:
    entries = []
    for block in _blocks_from_lines(lines):
        if not block:
            continue
        title = _clean(BULLET_PREFIX_RE.sub("", block[0]))
        bullets = [
            _clean(BULLET_PREFIX_RE.sub("", line))
            for line in block[1:]
            if _clean(line) and not _is_header(line)
        ]
        if title:
            entries.append({"title": title, "bullets": bullets[:6]})
    return entries[:6]


def _parse_flat_list(lines: list[str]) -> list[str]:
    items = []
    for line in lines:
        for chunk in re.split(r"[,|\n]", line):
            c = _clean(BULLET_PREFIX_RE.sub("", chunk))
            if c:
                items.append(c)
    return items[:10]


def parse_resume(text: str) -> dict:
    lines = [l for l in text.split("\n")]
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
