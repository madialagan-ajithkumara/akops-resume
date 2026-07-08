# AKOps Resume AI

Free, self-hosted resume analysis and JD-vs-CV matching. **No paid AI/LLM API calls anywhere** — the whole "Job Readiness Score", career-match, and skill-gap logic runs on a small local ML model (TF-IDF + Logistic Regression) plus deterministic scoring rules, so there's no per-request token cost, ever.

## How the "AI" works here (and why there's no API bill)

- **Skill detection**: keyword/phrase matching against a curated open skill taxonomy (`backend/app/skills_data.py`, ~25 career tracks: DevOps, Data Science, Frontend, Cybersecurity, etc.)
- **Career-match classifier**: a TF-IDF + Logistic Regression model (`backend/app/classifier.py`) trained at server startup in under a second, entirely in memory, from that taxonomy. No GPU, no external calls.
- **Job Readiness Score**: rule-based (skill breadth, action verbs, quantified achievements, resume structure, soft skills, length).
- **JD vs CV Match**: classic TF-IDF cosine similarity between the JD and the resume text — the same core technique real ATS tools use.
- **PDF parsing**: `pypdf`, fully local.

> Note: we originally intended to train the classifier on the public Kaggle "UpdatedResumeDataSet" (962 labeled resumes). The sandbox this was built in blocks bulk downloads from raw.githubusercontent.com, so the taxonomy above was hand-curated from well-known public skill sets for the same ~25 job categories instead. If you want to train on the real dataset, download `UpdatedResumeDataSet.csv` from Kaggle yourself and call `career_classifier.train_from_csv("path.csv")` in `backend/app/classifier.py` — no other code changes needed.

## Resume Builder (new): parse, edit, export

A third tab, **Resume Builder**, lets someone upload a CV and get it back as structured, editable sections instead of just a score:

- Upload a PDF -> `backend/app/resume_parser.py` heuristically splits it into **Contact, Summary, Skills (grouped by category via the same taxonomy), Experience, Education, Projects, Certifications** -- no AI call, just regex/keyword section + entry detection.
- The frontend (`frontend/src/ResumeBuilder.jsx`) renders every section as editable fields/lists: add or remove a skill, a bullet point, a whole job entry, a category, anything.
- Resume parsing from plain PDF text is inherently imperfect (no bold/font cues survive extraction) -- the edit step is the safety net, not a nice-to-have.
- **Download as PDF or Word**: `backend/app/export_pdf.py` (reportlab) and `export_docx.py` (python-docx) render the edited data into a clean, single-column, ATS-friendly resume template (accent-colored section headers, consistent spacing) -- good to actually send to employers.

## Project structure

```
akops-resume-ai/
  backend/          FastAPI app (Python)
    app/
      main.py        API routes: /api/analyze, /api/match, /api/parse, /api/export, /api/health
      classifier.py   local TF-IDF + LogisticRegression career classifier
      analyzer.py     skill detection, scoring, summary, strengths
      matcher.py      JD vs CV cosine-similarity matching
      resume_parser.py   heuristic CV -> structured sections parser
      schemas.py      pydantic models for the editable resume JSON
      export_pdf.py   structured resume -> polished PDF (reportlab)
      export_docx.py  structured resume -> polished Word doc (python-docx)
      skills_data.py  open skill taxonomy (25 career tracks)
      pdf_utils.py    PDF text extraction
    requirements.txt
    render.yaml       one-click Render free-tier deploy config
  frontend/          React (Vite) app, same purple/dark AKOps theme
    src/App.jsx
    src/ResumeBuilder.jsx   parse -> edit -> download UI
    src/index.css
    vercel.json
```

## Run it locally

Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend (in a second terminal):
```bash
cd frontend
npm install
npm run dev
```
Open the printed localhost URL. The frontend defaults to calling `http://localhost:8000`.

## Deploy for free

**Backend -> Render (free web service)**
1. Push this repo to GitHub.
2. On [render.com](https://render.com), New -> Web Service -> connect the repo, root directory `backend`.
3. Render will read `render.yaml` automatically (Python, free plan, `uvicorn` start command already set).
4. Note the deployed URL, e.g. `https://akops-resume-ai-backend.onrender.com`.

*Free-tier caveat: Render's free web services spin down after ~15 min idle and take ~30-50s to wake on the next request — totally fine for a personal/free tool, just expect a cold-start delay occasionally.*

**Frontend -> Vercel (free) or Netlify (free)**
1. On [vercel.com](https://vercel.com), New Project -> import the repo, root directory `frontend`.
2. Add an environment variable `VITE_API_URL` = your Render backend URL from above.
3. Deploy. Vercel builds with `npm run build` and serves `dist/` automatically (config already in `vercel.json`).

Both plans are $0/month — no credit card required for either Render's or Vercel's free tier at time of writing (verify current terms on their pricing pages, they do change).

## Zero-cost guarantee

There is no OpenAI/Anthropic/any paid LLM key anywhere in this codebase. Every "smart" feature (career match, score, skill gaps, JD match) is local Python + scikit-learn + regex. You can run this forever for free (aside from normal hosting-tier limits).
