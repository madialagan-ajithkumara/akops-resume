import { useEffect, useState } from 'react'
import ResumeBuilder from './ResumeBuilder'
import ChatWidget from './ChatWidget'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function BackgroundOrbs() {
  return (
    <>
      <div className="bg-orb one" />
      <div className="bg-orb two" />
      <div className="bg-orb three" />
    </>
  )
}

function Badge() {
  return (
    <div className="topbar">
      <a className="social-link" href="https://www.youtube.com/@AkOpsTamil" target="_blank" rel="noreferrer" aria-label="AKOps Tamil on YouTube" title="AKOps Tamil on YouTube">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.4 3.5 12 3.5 12 3.5s-7.4 0-9.4.6A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c2 .6 9.4.6 9.4.6s7.4 0 9.4-.6a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8ZM9.6 15.6V8.4L15.8 12Z"/></svg>
      </a>
      <a className="social-link" href="https://www.linkedin.com/in/ajithkumara-madialagan-256625169/" target="_blank" rel="noreferrer" aria-label="Ajithkumara Madialagan on LinkedIn" title="Ajithkumara Madialagan on LinkedIn">
        <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor"><path d="M20.45 20.45h-3.56v-5.58c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.95v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.38-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.07 2.07 0 1 1 0-4.13 2.07 2.07 0 0 1 0 4.13ZM7.12 20.45H3.56V9h3.56v11.45Z"/></svg>
      </a>
      <span className="badge">Powered by <b>AKOps</b></span>
    </div>
  )
}

function Hero() {
  return (
    <div className="hero">
      <div className="brand">
        <div className="brand-icon">⚡</div>
        <div className="brand-title"><span className="grad">AKOps</span> Resume AI</div>
      </div>
      <div className="tagline">YOUR AI CAREER ASSISTANT</div>
      <p className="hero-subtitle">
        Get an instant, honest score on your resume, see exactly how well it matches any job
        description, and rebuild it into a polished PDF or Word doc — all in under a minute.
      </p>
    </div>
  )
}

function TrustBar() {
  return (
    <div className="trust-bar">
      <span className="trust-chip">🔒 <b>Your CV is never stored</b></span>
      <span className="trust-chip">⚡ <b>Instant local AI</b> — no wait</span>
      <span className="trust-chip">💯 <b>100% free</b>, no sign-up</span>
    </div>
  )
}

function HowItWorks() {
  const steps = [
    { n: 1, title: 'Upload your resume', body: 'Drop in a PDF — nothing is saved on our servers.' },
    { n: 2, title: 'Get instant AI insights', body: 'A local ML model scores it and finds your best-fit career matches.' },
    { n: 3, title: 'Improve & download', body: 'Fix gaps, then export a polished, ATS-friendly PDF or Word doc.' },
  ]
  return (
    <div className="how-it-works">
      {steps.map((s) => (
        <div className="how-step" key={s.n}>
          <div className="num">{s.n}</div>
          <h4>{s.title}</h4>
          <p>{s.body}</p>
        </div>
      ))}
    </div>
  )
}

function Dropzone({ file, onChange }) {
  return (
    <label className="dropzone">
      <span className="dropzone-label">📎 {file ? 'Change PDF Resume' : 'Choose PDF Resume'}</span>
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => onChange(e.target.files?.[0] || null)}
      />
      {file && <span className="filename">{file.name}</span>}
    </label>
  )
}

function ScoreCard({ score }) {
  return (
    <div className="score-card">
      <div className="score-label">JOB READINESS SCORE</div>
      <div className="score-ring-wrap">
        <div className="score-ring" style={{ '--pct': score }}>
          <div className="score-ring-inner">
            <div className="score-number">{score}</div>
            <div className="score-suffix">/ 100</div>
          </div>
        </div>
      </div>
    </div>
  )
}

function SummaryCard({ summary }) {
  return (
    <div className="card">
      <div className="card-title">📋 Summary</div>
      <div className="summary-text">{summary}</div>
    </div>
  )
}

function StrengthsAndLearn({ strengths, skillsToLearn }) {
  return (
    <div className="grid-2" style={{ marginBottom: 22 }}>
      <div className="card">
        <div className="card-title">✅ Your Strengths</div>
        <div className="pill-list">
          {strengths.length === 0 && <div className="pill learn">Add more recognizable skills to your resume to surface strengths here.</div>}
          {strengths.map((s) => (
            <div className="pill" key={s.category}>
              {s.category} ({s.skills.slice(0, 3).join(', ')})
            </div>
          ))}
        </div>
      </div>
      <div className="card">
        <div className="card-title">📚 Skills To Learn Next</div>
        <div className="pill-list">
          {skillsToLearn.map((s) => (
            <div className="pill learn" key={s}>{s}</div>
          ))}
        </div>
      </div>
    </div>
  )
}

function CareerMatchFeedback({ detectedSkills, topCategory }) {
  const [categories, setCategories] = useState([])
  const [state, setState] = useState('idle') // idle | correcting | sent
  const [chosen, setChosen] = useState('')

  useEffect(() => {
    fetch(`${API_URL}/api/categories`)
      .then((r) => r.json())
      .then((d) => setCategories(d.categories || []))
      .catch(() => {})
  }, [])

  async function sendFeedback(correctCategory) {
    try {
      await fetch(`${API_URL}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ detected_skills: detectedSkills, correct_category: correctCategory }),
      })
    } catch {
      // best-effort — feedback failing silently shouldn't break the page
    }
    setState('sent')
  }

  if (state === 'sent') {
    return <div className="feedback-thanks">✓ Thanks — that helps the model improve for the next person.</div>
  }

  return (
    <div className="feedback-row">
      {state === 'idle' && (
        <>
          <span className="feedback-label">Was "{topCategory}" the right top match?</span>
          <button className="feedback-btn" onClick={() => sendFeedback(topCategory)}>👍</button>
          <button className="feedback-btn" onClick={() => setState('correcting')}>👎</button>
        </>
      )}
      {state === 'correcting' && (
        <div className="feedback-correct-row">
          <span className="feedback-label">What should it have been?</span>
          <select className="feedback-select" value={chosen} onChange={(e) => setChosen(e.target.value)}>
            <option value="">Choose a category...</option>
            {categories.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <button className="feedback-btn picked" disabled={!chosen} onClick={() => sendFeedback(chosen)}>Submit</button>
        </div>
      )}
    </div>
  )
}

function CareerMatches({ matches, detectedSkills }) {
  return (
    <div className="card">
      <div className="card-title">🚀 Best Career Matches</div>
      {matches.map((m) => (
        <div className="match-row" key={m.title}>
          <div className="match-title">{m.title}</div>
          <div className="match-bar-track">
            <div className="match-bar-fill" style={{ width: `${m.match_percent}%` }} />
          </div>
          <div className="match-pct">{m.match_percent}%</div>
        </div>
      ))}
      {matches.length > 0 && (
        <CareerMatchFeedback detectedSkills={detectedSkills} topCategory={matches[0].title} />
      )}
    </div>
  )
}

function EnhancedCard({ result }) {
  if (!result.enhanced_available) {
    if (result.enhanced_error) {
      return (
        <div className="card enhanced-note">
          <div className="card-title">🤖 Enhanced AI Summary</div>
          <div className="summary-text" style={{ color: 'var(--text-faint)' }}>{result.enhanced_error}</div>
        </div>
      )
    }
    return null
  }
  return (
    <div className="card enhanced-card">
      <div className="card-title">🤖 Enhanced AI Summary</div>
      <div className="summary-text">{result.enhanced_summary}</div>
      {result.enhanced_tips && result.enhanced_tips.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 8, textAlign: 'center' }}>Suggested improvements</div>
          <div className="pill-list">
            {result.enhanced_tips.map((tip, i) => (
              <div className="pill" key={i}>{tip}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function JdMatchCard({ matchPercent, matched, missing }) {
  return (
    <div className="card">
      <div className="jd-match-banner">
        <div>
          <div className="card-title" style={{ justifyContent: 'flex-start' }}>🎯 JD Match Score</div>
          <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>How well this resume lines up with the job description</div>
        </div>
        <div className="big grad" style={{ background: 'var(--gradient)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent' }}>
          {matchPercent}%
        </div>
      </div>
      <div style={{ marginTop: 18 }}>
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 6 }}>Matched skills</div>
        <div className="skill-tags">
          {matched.length === 0 && <span style={{ color: 'var(--text-faint)', fontSize: 13 }}>No direct skill overlap detected.</span>}
          {matched.map((s) => <span className="skill-tag have" key={s}>{s}</span>)}
        </div>
      </div>
      <div style={{ marginTop: 16 }}>
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 6 }}>Missing skills from JD</div>
        <div className="skill-tags">
          {missing.length === 0 && <span style={{ color: 'var(--text-faint)', fontSize: 13 }}>None — great coverage!</span>}
          {missing.map((s) => <span className="skill-tag missing" key={s}>{s}</span>)}
        </div>
      </div>
    </div>
  )
}

function TabGroup({ mode, setMode }) {
  return (
    <div className="tabs">
      <div className="tab-group">
        <button className={`tab ${mode === 'analysis' ? 'active' : ''}`} onClick={() => setMode('analysis')}>
          📊 Resume Analysis
        </button>
        <button className={`tab ${mode === 'match' ? 'active' : ''}`} onClick={() => setMode('match')}>
          🎯 JD vs CV Match
        </button>
        <button className={`tab ${mode === 'builder' ? 'active' : ''}`} onClick={() => setMode('builder')}>
          📝 Resume Builder
        </button>
      </div>
    </div>
  )
}

export default function App() {
  const [mode, setMode] = useState('analysis') // 'analysis' | 'match' | 'builder'
  const [file, setFile] = useState(null)
  const [jdText, setJdText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [enhanced, setEnhanced] = useState(false)

  const canSubmit = file && (mode === 'analysis' || jdText.trim().length > 20) && !loading

  async function handleSubmit() {
    setError('')
    setLoading(true)
    setResult(null)
    try {
      const form = new FormData()
      form.append('resume', file)
      const endpoint = mode === 'analysis' ? '/api/analyze' : '/api/match'
      if (mode === 'match') form.append('job_description', jdText)
      form.append('enhanced', enhanced ? 'true' : 'false')

      const res = await fetch(`${API_URL}${endpoint}`, { method: 'POST', body: form })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Something went wrong analyzing that resume.')
      setResult(data)
    } catch (e) {
      setError(e.message || 'Network error — is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  function reset() {
    setResult(null)
    setError('')
    setFile(null)
    setJdText('')
  }

  return (
    <div className="page">
      <BackgroundOrbs />
      <Badge />
      <Hero />

      {!result && (
        <>
          <TrustBar />
          {mode !== 'builder' && <HowItWorks />}
        </>
      )}

      {!result && mode !== 'builder' && (
        <>
          <TabGroup mode={mode} setMode={setMode} />

          <div className="card">
            <Dropzone file={file} onChange={setFile} />

            {mode === 'match' && (
              <>
                <div className="section-label">📄 PASTE JOB DESCRIPTION BELOW</div>
                <textarea
                  className="jd-input"
                  placeholder={"Paste the full Job Description here...\n\nExample:\nWe are looking for a DevOps Engineer with 3+ years experience in Kubernetes, Docker, AWS, CI/CD pipelines..."}
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                />
              </>
            )}

            <label className="enhanced-toggle">
              <input type="checkbox" checked={enhanced} onChange={(e) => setEnhanced(e.target.checked)} />
              <span>✨ Try Enhanced AI Summary <span className="badge-optional">optional</span></span>
            </label>

            <button className="btn-primary" disabled={!canSubmit} onClick={handleSubmit}>
              {loading ? (<><span className="spinner" />Analyzing...</>) : mode === 'analysis' ? '✨ Analyze Resume' : '🎯 Check JD Match'}
            </button>

            {error && <div className="error-box">{error}</div>}
          </div>
        </>
      )}

      {mode === 'builder' && (
        <>
          <TabGroup mode={mode} setMode={setMode} />
          <ResumeBuilder />
        </>
      )}

      {result && (
        <>
          <ScoreCard score={result.job_readiness_score} />
          {mode === 'match' && (
            <JdMatchCard matchPercent={result.match_percent} matched={result.matched_skills} missing={result.missing_skills} />
          )}
          <SummaryCard summary={result.summary} />
          <EnhancedCard result={result} />
          <StrengthsAndLearn strengths={result.strengths} skillsToLearn={result.skills_to_learn} />
          <CareerMatches matches={result.career_matches} detectedSkills={result.detected_skills} />
          <div className="reset-row">
            <button className="btn-ghost" onClick={reset}>↺ Analyze another resume</button>
          </div>
        </>
      )}

      <div className="footer">
        <div className="footer-trust">
          <span className="trust-chip">🔒 Privacy-first</span>
          <span className="trust-chip">⚡ Zero AI token cost</span>
          <span className="trust-chip">💯 Free forever</span>
        </div>
        Built with ❤ by <b>AKOps</b> · free & open, no AI subscription needed
      </div>

      <ChatWidget />
    </div>
  )
}
