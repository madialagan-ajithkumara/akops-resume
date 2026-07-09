"""
Render an already-computed Resume Analysis result (score, breakdown,
summary, strengths, career matches...) into a clean one-page PDF report,
fully local via reportlab -- no external service, no new AI call. This
powers the "Download Report" / "Save Report" buttons on the dashboard.

Takes the same JSON /api/analyze or /api/match already returned to the
browser -- nothing is re-computed or re-stored server-side.
"""
import io
from datetime import datetime, timezone

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, ListFlowable, ListItem,
)

ACCENT = colors.HexColor("#16a34a")
DARK = colors.HexColor("#111827")
GRAY = colors.HexColor("#555555")
TRACK = colors.HexColor("#e5e7eb")

TITLE_STYLE = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=20, textColor=DARK, spaceAfter=2)
SUB_STYLE = ParagraphStyle("Sub", fontName="Helvetica", fontSize=9.5, textColor=GRAY, spaceAfter=10)
SECTION_STYLE = ParagraphStyle("Section", fontName="Helvetica-Bold", fontSize=12, textColor=ACCENT, spaceBefore=14, spaceAfter=6)
BODY_STYLE = ParagraphStyle("Body", fontName="Helvetica", fontSize=10, textColor=DARK, leading=14)
SCORE_STYLE = ParagraphStyle("Score", fontName="Helvetica-Bold", fontSize=34, textColor=ACCENT)
SCORE_LABEL_STYLE = ParagraphStyle("ScoreLabel", fontName="Helvetica-Bold", fontSize=11, textColor=DARK)
BULLET_STYLE = ParagraphStyle("Bullet", fontName="Helvetica", fontSize=9.8, textColor=DARK, leading=13)


def _bar_row(label: str, pct: int) -> list:
    pct = max(0, min(100, int(pct or 0)))
    bar = Table(
        [[""]],
        colWidths=[2.6 * inch * pct / 100],
        rowHeights=[8],
    )
    bar.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT)]))
    track = Table([[bar]], colWidths=[2.6 * inch], rowHeights=[8])
    track.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TRACK),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return [Paragraph(label, BODY_STYLE), track, Paragraph(f"{pct}%", BODY_STYLE)]


def build_analysis_report_pdf(result: dict, resume_filename: str = "") -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=LETTER,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
    )
    story = []

    story.append(Paragraph("AKOps Resume AI — Analysis Report", TITLE_STYLE))
    generated = datetime.now(timezone.utc).strftime("%B %d, %Y")
    sub = f"Generated {generated}"
    if resume_filename:
        sub += f"  ·  {resume_filename}"
    story.append(Paragraph(sub, SUB_STYLE))
    story.append(HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=10))

    score = result.get("job_readiness_score", 0)
    label = result.get("score_label", "")
    story.append(Table(
        [[Paragraph(f"{score}<font size=14>/100</font>", SCORE_STYLE), Paragraph(label, SCORE_LABEL_STYLE)]],
        colWidths=[2 * inch, 3.5 * inch],
    ))
    if result.get("score_message"):
        story.append(Paragraph(result["score_message"], BODY_STYLE))

    breakdown = result.get("score_breakdown") or {}
    if breakdown:
        story.append(Spacer(1, 10))
        rows = [
            _bar_row("ATS Compatibility", breakdown.get("ats_compatibility", 0)),
            _bar_row("Skills Match", breakdown.get("skills_match", 0)),
            _bar_row("Content Quality", breakdown.get("content_quality", 0)),
            _bar_row("Impact & Clarity", breakdown.get("impact_clarity", 0)),
        ]
        t = Table(rows, colWidths=[1.5 * inch, 2.6 * inch, 0.6 * inch])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t)

    if result.get("match_percent") is not None:
        story.append(Paragraph("JD Match Score", SECTION_STYLE))
        story.append(Paragraph(f"{result['match_percent']}% match with the pasted job description.", BODY_STYLE))

    if result.get("summary"):
        story.append(Paragraph("Summary", SECTION_STYLE))
        story.append(Paragraph(result["summary"], BODY_STYLE))

    strengths = result.get("strengths") or []
    if strengths:
        story.append(Paragraph("Strengths", SECTION_STYLE))
        items = [ListItem(Paragraph(f"<b>{s['category']}</b>: {', '.join(s['skills'][:5])}", BULLET_STYLE)) for s in strengths]
        story.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=14, spaceAfter=6))

    skills_to_learn = result.get("skills_to_learn") or []
    if skills_to_learn:
        story.append(Paragraph("Skills to Learn Next", SECTION_STYLE))
        story.append(Paragraph(", ".join(skills_to_learn), BODY_STYLE))

    matches = result.get("career_matches") or []
    if matches:
        story.append(Paragraph("Best Career Matches", SECTION_STYLE))
        items = [ListItem(Paragraph(f"{m['title']} — {m['match_percent']}%", BULLET_STYLE)) for m in matches[:8]]
        story.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=14))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.6, color=TRACK, spaceAfter=6))
    story.append(Paragraph(
        "Generated locally by AKOps Resume AI — free, self-hosted resume analysis. "
        "No AI subscription used to produce this score.",
        SUB_STYLE,
    ))

    doc.build(story)
    return buf.getvalue()
