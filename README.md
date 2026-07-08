# AKOps Resume AI

Free, self-hosted resume analysis and JD-vs-CV matching. **No paid AI/LLM API calls anywhere** — the whole "Job Readiness Score", career-match, and skill-gap logic runs on a small local ML model (TF-IDF + Logistic Regression) plus deterministic scoring rules, so there's no per-request token cost, ever.

## How the "AI" works here (and why there's no API bill)

- **Skill detection**: keyword/phrase matching against a curated open skill taxonomy (`backend/app/skills_data.py`, ~25 career tracks: DevOps, Data Science, Frontend, Cybersecurity, etc.)
- **Career-match classifier**: a TF-IDF + Logistic Regression model (`backend/app/classifier.py`) trained at server startup in under a second, entirely in memory, from that taxonomy. No GPU, no external calls.
- **Job Readiness Score**: rule-based (skill breadth, action verbs, quantified achievements, resume structure, soft skills, length).
- **JD vs CV Match**: classic TF-IDF cosine similarity between the JD and the resume text — the same core technique real ATS tools use.
- **PDF parsing**: `pypdf`, fully local.

> Note: we originally intended to train the classifier on the public Kaggle "UpdatedResumeDataSet" (962 labeled resumes). The sandbox this was built in blocks bulk downloads from raw.githubusercontent.com, so the taxonomy above was hand-curated from well-known public skill sets for the same ~25 job categories instead. If you want to train on the real dataset, download `UpdatedResumeDataSet.csv` from Kaggle yourself and call `career_classifier.train_from_csv("path.csv")` in `backend/app/classifier.py` — no other code changes needed.

## Project structure

```
akops-resume-ai/
  backend/          FastAPI app (Python)
    app/
      main.py        API routes: /api/analyze, /api/match, /api/health
      classifier.py   local TF-IDF + LogisticRegression career classifier
      analyzer.py     skill detection, scoring, summary, strengths
      matcher.py      JD vs CV cosine-similarity matching
      skills_data.py  open skill taxonomy (25 career tracks)
      pdf_utils.py    PDF text extraction
    requirements.txt
    render.yaml       one-click Render free-tier deploy config
  frontend/          React (Vite) app, same purple/dark AKOps theme
    src/App.jsx
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
