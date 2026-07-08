import { useState, useRef } from 'react'
import ResumeBuilder from './ResumeBuilder'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function Badge() {
  return (
    <div className="topbar">
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
    </div>
  )
}

function Dropzone({ file, onChange }) {
  const inputRef = useRef(null)
  return (
    <label className="dropzone" onClick={() => inputRef.current?.click()}>
      📎 {file ? 'Change PDF Resume' : 'Choose PDF Resume'}
      <input
        ref={inputRef}
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
      <div className="score-number">{score}</div>
      <div className="score-suffix">/100</div>
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

function CareerMatches({ matches }) {
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

export default function App() {
  const [mode, setMode] = useState('analysis') // 'analysis' | 'match'
  const [file, setFile] = useState(null)
  const [jdText, setJdText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

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
      <Badge />
      <Hero />

      {!result && mode !== 'builder' && (
        <>
          <div className="tabs">
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

            <button className="btn-primary" disabled={!canSubmit} onClick={handleSubmit}>
              {loading ? (<><span className="spinner" />Analyzing...</>) : mode === 'analysis' ? '✨ Analyze Resume' : '🎯 Check JD Match'}
            </button>

            {error && <div className="error-box">{error}</div>}
          </div>
        </>
      )}

      {mode === 'builder' && (
        <>
          <div className="tabs">
            <button className={`tab ${mode === 'analysis' ? 'active' : ''}`} onClick={() => setMode('analysis')}>
              📊 Resume Analysis
            </button>
            <button className={`tab ${mode === 'match' ? 'active' : ''}`} onClick={() => setMode('match')}>
              🎯 JD vs CV Match
            </button>
            <button className={`tab active`} onClick={() => setMode('builder')}>
              📝 Resume Builder
            </button>
          </div>
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
          <StrengthsAndLearn strengths={result.strengths} skillsToLearn={result.skills_to_learn} />
          <CareerMatches matches={result.career_matches} />
          <div className="reset-row">
            <button className="btn-ghost" onClick={reset}>↺ Analyze another resume</button>
          </div>
        </>
      )}

      <div className="footer">Built with ❤ by <b>AKOps</b> · free & open, no AI subscription needed</div>
    </div>
  )
}
