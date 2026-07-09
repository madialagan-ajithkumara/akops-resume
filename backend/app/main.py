from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from .pdf_utils import extract_text_from_pdf
from .analyzer import analyze_resume
from .matcher import match_resume_to_jd
from .resume_parser import parse_resume
from .schemas import ExportRequest, ChatRequest, FeedbackRequest
from .export_pdf import build_resume_pdf
from .export_docx import build_resume_docx
from .classifier import career_classifier
from .skills_data import CAREER_SKILLS
from . import llm_enhance, chat_assist, gemini_client
from .resume_gate import assess_resume_likelihood

app = FastAPI(title="AKOps Resume AI", version="1.2.0")

# CORS: allow the frontend (any origin, since this is a free public tool with no auth)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _pdf_to_text(upload: UploadFile) -> str:
    if upload.content_type not in ("application/pdf", "application/x-pdf") and not upload.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume.")
    data = upload.file.read()
    text = extract_text_from_pdf(data)
    if not text or len(text.split()) < 10:
        raise HTTPException(status_code=422, detail="Couldn't read text from that PDF. Try a text-based (not scanned/image) PDF.")

    gate = assess_resume_likelihood(text)
    if not gate["is_resume"]:
        raise HTTPException(
            status_code=422,
            detail=(
                "This doesn't look like a resume/CV (" + "; ".join(gate["reasons"]) + "). "
                "Please upload your resume as a PDF instead."
            ),
        )
    return text


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "enhanced_mode_configured": llm_enhance.is_configured(),
        "enhanced_mode_quota_remaining_today": llm_enhance.remaining_quota() if llm_enhance.is_configured() else None,
        "chat_configured": gemini_client.is_configured(),
        "chat_quota_remaining_today": chat_assist.remaining_quota() if gemini_client.is_configured() else None,
        "career_match_feedback_count": career_classifier.feedback_count(),
    }


@app.get("/api/categories")
def categories():
    """Career-track names, used by the frontend's feedback-correction dropdown."""
    return {"categories": list(CAREER_SKILLS.keys())}


def _maybe_enhance(result: dict, text: str, enhanced: bool) -> dict:
    """
    Attach optional AI-enhanced insights. Never breaks the request: if
    enhanced mode wasn't requested, isn't configured, or the call fails for
    any reason, the reliable local analysis is still returned untouched.
    """
    if not enhanced:
        return result
    if not llm_enhance.is_configured():
        return {**result, "enhanced_available": False,
                "enhanced_error": "Enhanced mode isn't configured on this server yet."}
    try:
        extra = llm_enhance.enhance_analysis(text, result)
        return {**result, "enhanced_available": True, **extra}
    except Exception as e:
        return {**result, "enhanced_available": False, "enhanced_error": str(e)[:300]}


@app.post("/api/analyze")
async def analyze(resume: UploadFile = File(...), enhanced: bool = Form(False)):
    text = _pdf_to_text(resume)
    result = analyze_resume(text)
    return _maybe_enhance(result, text, enhanced)


@app.post("/api/match")
async def match(resume: UploadFile = File(...), job_description: str = Form(...), enhanced: bool = Form(False)):
    if not job_description or len(job_description.split()) < 5:
        raise HTTPException(status_code=400, detail="Please paste a fuller job description.")
    text = _pdf_to_text(resume)
    base = analyze_resume(text)
    match_result = match_resume_to_jd(text, job_description)
    combined = {**base, **match_result}
    return _maybe_enhance(combined, text, enhanced)


@app.post("/api/parse")
async def parse(resume: UploadFile = File(...)):
    """Parse an uploaded PDF into structured, editable resume-builder sections."""
    text = _pdf_to_text(resume)
    return parse_resume(text)


@app.post("/api/export")
async def export(payload: ExportRequest):
    """Render the (possibly user-edited) structured resume as a downloadable PDF or DOCX."""
    fmt = (payload.format or "pdf").lower()
    filename_base = (payload.resume.contact.name or "resume").strip().replace(" ", "_") or "resume"

    if fmt == "docx":
        content = build_resume_docx(payload.resume)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{filename_base}.docx"
    elif fmt == "pdf":
        content = build_resume_pdf(payload.resume)
        media_type = "application/pdf"
        filename = f"{filename_base}.pdf"
    else:
        raise HTTPException(status_code=400, detail="format must be 'pdf' or 'docx'")

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/feedback")
async def feedback(payload: FeedbackRequest):
    """
    Continuous learning, in-memory only: fold a user-confirmed correction
    (already-detected skills -> the career category they say is right) back
    into the classifier and retrain immediately. No CV text or personal info
    is ever involved -- only skill keywords already extracted locally. This
    lives in process memory and resets on server restart (see classifier.py).
    """
    try:
        career_classifier.add_feedback(" ".join(payload.detected_skills), payload.correct_category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok", "feedback_count": career_classifier.feedback_count()}


@app.post("/api/chat")
async def chat(payload: ChatRequest):
    """Resume Chat Assistant -- scoped strictly to resume/career questions (see chat_assist.py)."""
    if not gemini_client.is_configured():
        raise HTTPException(status_code=503, detail="The chat assistant isn't configured on this server yet.")
    try:
        text = chat_assist.reply(payload.message, payload.history)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=429, detail=str(e))
    return {"reply": text, "quota_remaining": chat_assist.remaining_quota()}
