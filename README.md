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
      main.py        API routes: /api/analyze, /api/match, /api/parse, /api/export, /api/feedback, /api/categories, /api/chat, /api/health
      classifier.py   local TF-IDF + LogisticRegression career classifier + in-memory add_feedback() continuous learning
      analyzer.py     skill detection, scoring, summary, strengths
      matcher.py      JD vs CV cosine-similarity matching
      resume_parser.py   heuristic CV -> structured sections parser
      schemas.py      pydantic models for the editable resume JSON, chat, and feedback requests
      export_pdf.py   structured resume -> polished PDF (reportlab)
      export_docx.py  structured resume -> polished Word doc (python-docx)
      skills_data.py  open skill taxonomy (25 career tracks) + skill alias/synonym map
      pdf_utils.py    PDF text extraction
      gemini_client.py   shared low-level Gemini REST caller (used by both features below)
      llm_enhance.py  OPTIONAL: Enhanced Mode summary/tips if GEMINI_API_KEY is set; unused otherwise
      chat_assist.py  OPTIONAL: Resume Chat Assistant widget, scoped to resume/career questions only
    requirements.txt
    render.yaml       one-click Render free-tier deploy config
  frontend/          React (Vite) app, same purple/dark AKOps theme
    src/App.jsx
    src/ResumeBuilder.jsx   parse -> edit -> download UI
    src/ChatWidget.jsx      floating bottom-left chat assistant
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

There is no OpenAI/Anthropic/any paid LLM key required anywhere in this codebase. Every core feature (career match, score, skill gaps, JD match, resume parsing/export) is local Python + scikit-learn + regex. You can run this forever for free (aside from normal hosting-tier limits).

## Optional: Enhanced Mode (free Gemini API)

There's an opt-in "✨ Try Enhanced AI Summary" checkbox in the UI that, when enabled by the site owner, calls Google's Gemini API for a more natural-language summary and improvement tips layered on top of the local analysis. It's off by default and the app is fully functional without it.

To turn it on:
1. Get a free API key at [aistudio.google.com](https://aistudio.google.com/apikey) (no credit card needed for the free tier).
2. In Render, go to your backend service -> Environment -> add `GEMINI_API_KEY` = your key.
3. Redeploy. `/api/health` will now report `"enhanced_mode_configured": true`.

This uses `gemini-2.5-flash-lite`, which has a generous free daily quota. The key lives only on your backend server (`backend/app/llm_enhance.py`) — it's never sent to or requested from the browser, and every other feature keeps working with zero cost if you skip this step. If the key is missing, invalid, or the API is unreachable, the app quietly falls back to the local analysis instead of breaking the request.

**Traffic safety net:** the backend tracks its own daily usage and proactively stops calling Gemini once it's used `GEMINI_DAILY_LIMIT` requests that day (default 200, well under Google's free-tier cap, so a burst of visitors can never get your key rate-limited). Once the budget is hit, users just see "today's free AI bonus is used up" and get the regular local analysis instead — nothing breaks. Raise or lower the budget by setting `GEMINI_DAILY_LIMIT` in Render's environment variables. Note this counter lives in memory, so it resets whenever the server restarts (e.g. Render's free tier spinning down after ~15 min idle) -- it's an approximate daily budget, not a database-backed exact one, which is intentional to keep this feature free and dependency-free.

**The important part for scale:** none of this affects the rest of the app. Resume Analysis, JD Matching, and the Resume Builder (parse/edit/export) have no usage ceiling at all — they're local computation, so however many people use the site, that part costs $0 and never degrades. Enhanced Mode is deliberately the only piece with a ceiling, and it fails soft.

## Resume Chat Assistant (bottom-left widget)

A floating 💬 button (bottom-left of the site) opens a small chat panel powered by the same free Gemini key as Enhanced Mode — but scoped strictly to resume/career/job-search questions via a system prompt (`backend/app/chat_assist.py`). Off-topic questions ("write me code", "what's the weather") are politely declined by the model itself; no keyword filter is needed to enforce this.

It uses the **same `GEMINI_API_KEY`** as Enhanced Mode but a **separate daily budget**, `GEMINI_CHAT_DAILY_LIMIT` (default 300), so a busy chat widget can never starve Enhanced Mode's quota, or vice versa. Nothing sent through the chat is stored server-side — each request is stateless; the browser resends the recent conversation history with every message. If `GEMINI_API_KEY` isn't set, the widget still appears but tells visitors it isn't turned on yet.

## Continuous learning for career matches (in-memory)

Under "Best Career Matches," visitors can confirm 👍 or correct 👎 the top match. A correction lets them pick the right career track from a dropdown; that (skills-only, no CV text, no personal info) example is folded straight back into the TF-IDF + Logistic Regression classifier and it retrains immediately (`backend/app/classifier.py`, `add_feedback()`), typically in well under a second.

This is genuine online learning — the model's predictions really do improve within the server's running lifetime — but it's **in-memory only**, so it resets whenever the process restarts (e.g. Render's free tier spinning down after ~15 min idle, or a redeploy). That's a deliberate tradeoff: Render's free tier has no persistent disk, and persisting real feedback data anywhere permanent would mean standing up an external database. Keeping it in-memory means zero new infrastructure, zero new cost, and it never touches the "we never store your CV" promise — feedback only ever carries already-detected skill keywords plus the category a visitor picked, nothing else.

If you outgrow this later, the natural upgrade path is to give the backend a free external Postgres (e.g. Supabase's free tier, which doesn't auto-expire the way Render's free Postgres does) and persist the feedback rows there so learning survives restarts.
