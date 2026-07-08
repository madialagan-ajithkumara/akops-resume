from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from .pdf_utils import extract_text_from_pdf
from .analyzer import analyze_resume
from .matcher import match_resume_to_jd
from .resume_parser import parse_resume
from .schemas import ExportRequest
from .export_pdf import build_resume_pdf
from .export_docx import build_resume_docx

app = FastAPI(title="AKOps Resume AI", version="1.1.0")

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
    return text


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(resume: UploadFile = File(...)):
    text = _pdf_to_text(resume)
    result = analyze_resume(text)
    return result


@app.post("/api/match")
async def match(resume: UploadFile = File(...), job_description: str = Form(...)):
    if not job_description or len(job_description.split()) < 5:
        raise HTTPException(status_code=400, detail="Please paste a fuller job description.")
    text = _pdf_to_text(resume)
    base = analyze_resume(text)
    match_result = match_resume_to_jd(text, job_description)
    return {**base, **match_result}


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
