from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .pdf_utils import extract_text_from_pdf
from .analyzer import analyze_resume
from .matcher import match_resume_to_jd

app = FastAPI(title="AKOps Resume AI", version="1.0.0")

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
