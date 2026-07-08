"""
Generate a clean, single-column, ATS-friendly resume PDF from structured
data -- fully local via reportlab, no external service.
"""
import io

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, HRFlowable,
)

ACCENT = colors.HexColor("#7c1fd1")
DARK = colors.HexColor("#1a1a1a")
GRAY = colors.HexColor("#555555")

NAME_STYLE = ParagraphStyle("Name", fontName="Helvetica-Bold", fontSize=22, textColor=DARK, spaceAfter=2)
CONTACT_STYLE = ParagraphStyle("Contact", fontName="Helvetica", fontSize=9.5, textColor=GRAY, spaceAfter=10)
SECTION_STYLE = ParagraphStyle("Section", fontName="Helvetica-Bold", fontSize=11.5, textColor=ACCENT,
                               spaceBefore=12, spaceAfter=4, letterSpacing=1)
BODY_STYLE = ParagraphStyle("Body", fontName="Helvetica", fontSize=10, textColor=DARK, leading=14, alignment=TA_LEFT)
ENTRY_TITLE_STYLE = ParagraphStyle("EntryTitle", fontName="Helvetica-Bold", fontSize=10.5, textColor=DARK, spaceAfter=1)
ENTRY_SUB_STYLE = ParagraphStyle("EntrySub", fontName="Helvetica-Oblique", fontSize=9.5, textColor=GRAY, spaceAfter=3)
BULLET_STYLE = ParagraphStyle("Bullet", fontName="Helvetica", fontSize=9.8, textColor=DARK, leading=13)


def _contact_line(contact) -> str:
    parts = [p for p in [contact.email, contact.phone, contact.linkedin, contact.github, contact.location] if p]
    return "  |  ".join(parts)


def build_resume_pdf(resume) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=LETTER,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
    )
    story = []

    story.append(Paragraph(resume.contact.name or "Your Name", NAME_STYLE))
    contact_line = _contact_line(resume.contact)
    if contact_line:
        story.append(Paragraph(contact_line, CONTACT_STYLE))
    story.append(HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=6))

    if resume.summary:
        story.append(Paragraph("SUMMARY", SECTION_STYLE))
        story.append(Paragraph(resume.summary, BODY_STYLE))

    if resume.skill_categories:
        story.append(Paragraph("SKILLS", SECTION_STYLE))
        for cat in resume.skill_categories:
            if not cat.skills:
                continue
            line = f"<b>{cat.category}:</b> {', '.join(cat.skills)}"
            story.append(Paragraph(line, BODY_STYLE))

    if resume.experience:
        story.append(Paragraph("EXPERIENCE", SECTION_STYLE))
        for entry in resume.experience:
            header = entry.title or "Role"
            if entry.company:
                header += f" — {entry.company}"
            story.append(Paragraph(header, ENTRY_TITLE_STYLE))
            if entry.dates:
                story.append(Paragraph(entry.dates, ENTRY_SUB_STYLE))
            if entry.bullets:
                items = [ListItem(Paragraph(b, BULLET_STYLE), leftIndent=8) for b in entry.bullets]
                story.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=14, spaceAfter=6))
            else:
                story.append(Spacer(1, 6))

    if resume.projects:
        story.append(Paragraph("PROJECTS", SECTION_STYLE))
        for entry in resume.projects:
            story.append(Paragraph(entry.title, ENTRY_TITLE_STYLE))
            if entry.bullets:
                items = [ListItem(Paragraph(b, BULLET_STYLE), leftIndent=8) for b in entry.bullets]
                story.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=14, spaceAfter=6))

    if resume.education:
        story.append(Paragraph("EDUCATION", SECTION_STYLE))
        for entry in resume.education:
            header = entry.degree or "Degree"
            if entry.institution:
                header += f" — {entry.institution}"
            story.append(Paragraph(header, ENTRY_TITLE_STYLE))
            if entry.dates:
                story.append(Paragraph(entry.dates, ENTRY_SUB_STYLE))

    if resume.certifications:
        story.append(Paragraph("CERTIFICATIONS", SECTION_STYLE))
        items = [ListItem(Paragraph(c, BULLET_STYLE), leftIndent=8) for c in resume.certifications]
        story.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=14))

    doc.build(story)
    return buf.getvalue()
