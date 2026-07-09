import { useEffect, useState } from 'react'
import ResumeBuilder from './ResumeBuilder'
import ChatWidget from './ChatWidget'
import Logo from './Logo'

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

function SiteHeader() {
  return (
    <div className="site-header">
      <div className="brand-block">
        <Logo size={42} />
        <div>
          <div className="brand-text-title">AKOps <span className="grad">Resume AI</span></div>
          <div className="brand-text-sub">Powered by AKOps Labs</div>
        </div>
      </div>
      <div className="header-right">
        <a className="social-link" href="https://www.youtube.com/@AkOpsTamil" target="_blank" rel="noreferrer" aria-label="AKOps Tamil on YouTube" title="AKOps Tamil on YouTube">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.4 3.5 12 3.5 12 3.5s-7.4 0-9.4.6A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c2 .6 9.4.6 9.4.6s7.4 0 9.4-.6a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8ZM9.6 15.6V8.4L15.8 12Z"/></svg>
        </a>
        <a className="social-link" href="https://www.linkedin.com/in/ajithkumara-madialagan-256625169/" target="_blank" rel="noreferrer" aria-label="Ajithkumara Madialagan on LinkedIn" title="Ajithkumara Madialagan on LinkedIn">
          <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor"><path d="M20.45 20.45h-3.56v-5.58c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.95v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.38-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.07 2.07 0 1 1 0-4.13 2.07 2.07 0 0 1 0 4.13ZM7.12 20.45H3.56V9h3.56v11.45Z"/></svg>
        </a>
        <span className="badge">Powered by <b>AKOps Labs</b></span>
      </div>
    </div>
  )
}

function Sidebar({ mode, result, onNavigate }) {
  const items = [
    { key: 'dashboard', icon: '▦', label: 'Dashboard' },
  ]
  const analysisItems = [
    { key: 'analysis', icon: '📊', label: 'Resume Analysis' },
    { key: 'match', icon: '🎯', label: 'JD vs CV Match' },
    { key: 'builder', icon: '📝', label: 'Resume Builder' },
  ]
  const dashboardActive = !!result
  return (
    <div className="sidebar">
      {items.map((it) => (
        <button
          key={it.key}
          className={`sidebar-item ${dashboardActive ? 'active' : ''}`}
          onClick={() => onNavigate('dashboard')}
        >
          <span className="sidebar-icon">{it.icon}</span>{it.label}
        </button>
      ))}
      <div className="sidebar-section-label">ANALYSIS</div>
      {analysisItems.map((it) => (
        <button
          key={it.key}
          className={`sidebar-item ${!dashboardActive && mode === it.key ? 'active' : ''}`}
          onClick={() => onNavigate(it.key)}
        >
          <span className="sidebar-icon">{it.icon}</span>{it.label}
        </button>
      ))}
    </div>
  )
}

function Hero() {
  return (
    <div className="hero">
      <div className="brand">
        <div className="brand-title"><span className="grad">Your AI Career Assistant</span></div>
      </div>
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
      <input type="file" accept="application/pdf" onChange={(e) => onChange(e.target.files?.[0] || null)} />
      {file && <span className="filename">{file.name}</span>}
    </label>
  )
}

function TabGroup({ mode, setMode }) {
  return (
    <div className="tabs">
      <div className="tab-group">
        <button className={`tab ${mode === 'analysis' ? 'active' : ''}`} onClick={() => setMode('analysis')}>📊 Resume Analysis</button>
        <button className={`tab ${mode === 'match' ? 'active' : ''}`} onClick={() => setMode('match')}>🎯 JD vs CV Match</button>
        <button className={`tab ${mode === 'builder' ? 'active' : ''}`} onClick={() => setMode('builder')}>📝 Resume Builder</button>
      </div>
    </div>
  )
}

function ScorePanel({ result }) {
  const score = result.job_readiness_score
  const b = result.score_breakdown || {}
  const rows = [
    { label: 'ATS Compatibility', pct: b.ats_compatibility },
    { label: 'Skills Match', pct: b.skills_match },
    { label: 'Content Quality', pct: b.content_quality },
    { label: 'Impact & Clarity', pct: b.impact_clarity },
  ]
  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div className="score-panel">
        <div className="score-card">
          <div className="score-label">OVERALL RESUME SCORE</div>
          <div className="score-ring-wrap">
            <div className="score-ring" style={{ '--pct': score }}>
              <div className="score-ring-inner">
                <div className="score-number">{score}</div>
                <div className="score-suffix">/ 100</div>
              </div>
            </div>
          </div>
          <div className="score-status-label">{result.score_label}</div>
          <div className="score-status-msg">{result.score_message}</div>
        </div>
        <div className="breakdown-panel">
          {rows.map((r) => (
            <div className="breakdown-row" key={r.label}>
              <div className="breakdown-label">{r.label}</div>
              <div className="breakdown-track"><div className="breakdown-fill" style={{ width: `${r.pct || 0}%` }} /></div>
              <div className="breakdown-pct">{r.pct || 0}%</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function SummaryPanel({ result, analyzedAt }) {
  return (
    <div className="card summary-panel">
      <div className="card-title">📋 Summary</div>
      <div className="summary-text">{result.summary}</div>
      <div className="stat-chip-grid">
        <div className="stat-chip"><div className="stat-chip-top">💼 EXPERIENCE LEVEL</div><div className="stat-chip-value">{result.experience_level}</div></div>
        <div className="stat-chip"><div className="stat-chip-top">📄 RESUME LENGTH</div><div className="stat-chip-value">{result.estimated_pages}</div></div>
        <div className="stat-chip"><div className="stat-chip-top">🗂️ FILE TYPE</div><div className="stat-chip-value">{result.file_type}</div></div>
        <div className="stat-chip"><div className="stat-chip-top">📅 ANALYZED ON</div><div className="stat-chip-value">{analyzedAt}</div></div>
      </div>
    </div>
  )
}

function StrengthsAndImprove({ strengths, suggestions }) {
  return (
    <div className="grid-2" style={{ marginBottom: 20 }}>
      <div className="card">
        <div className="card-title">✅ Your Strengths</div>
        {strengths.length === 0 && <div className="summary-text">Add more recognizable skills to your resume to surface strengths here.</div>}
        {strengths.map((s) => (
          <div className="info-item" key={s.category}>
            <div className="info-item-icon good">✓</div>
            <div>
              <div className="info-item-title">{s.category}</div>
              <div className="info-item-desc">{s.skills.slice(0, 4).join(', ')}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="card">
        <div className="card-title">⚠️ Areas To Improve</div>
        {suggestions.length === 0 && <div className="summary-text">Nothing major — this resume covers the fundamentals well.</div>}
        {suggestions.map((s, i) => (
          <div className="info-item" key={i}>
            <div className="info-item-icon warn">!</div>
            <div>
              <div className="info-item-title">{s.title}</div>
              <div className="info-item-desc">{s.description}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function CareerMatchFeedback({ detectedSkills, topCategory }) {
  const [categories, setCategories] = useState([])
  const [state, setState] = useState('idle')
  const [chosen, setChosen] = useState('')

  useEffect(() => {
    fetch(`${API_URL}/api/categories`).then((r) => r.json()).then((d) => setCategories(d.categories || [])).catch(() => {})
  }, [])

  async function sendFeedback(correctCategory) {
    try {
      await fetch(`${API_URL}/api/feedback`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ detected_skills: detectedSkills, correct_category: correctCategory }),
      })
    } catch {}
    setState('sent')
  }

  if (state === 'sent') return <div className="feedback-thanks">✓ Thanks — that helps the model improve for the next person.</div>

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
  const [showAll, setShowAll] = useState(false)
  const visible = showAll ? matches : matches.slice(0, 5)
  return (
    <div className="card">
      <div className="card-title">🚀 Best Job Matches</div>
      {visible.map((m) => (
        <div className="match-row" key={m.title}>
          <div className="match-title">{m.title}</div>
          <div className="match-bar-track"><div className="match-bar-fill" style={{ width: `${m.match_percent}%` }} /></div>
          <div className="match-pct">{m.match_percent}%</div>
        </div>
      ))}
      {matches.length > 5 && (
        <div className="view-more-row">
          <button className="btn-outline" onClick={() => setShowAll((v) => !v)}>
            {showAll ? '↑ Show fewer matches' : `→ View Detailed Job Matches (${matches.length})`}
          </button>
        </div>
      )}
      {matches.length > 0 && <CareerMatchFeedback detectedSkills={detectedSkills} topCategory={matches[0].title} />}
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
          <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 8 }}>Suggested improvements</div>
          <div className="pill-list">
            {result.enhanced_tips.map((tip, i) => <div className="pill" key={i}>{tip}</div>)}
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
        <div className="big">{matchPercent}%</div>
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

function FileManageAndReport({ file, analyzedAt, onReplace, onReanalyze, reanalyzing, onDownload, onSave, onShare, downloading }) {
  return (
    <div className="card" style={{ padding: 0 }}>
      <div className="file-manage-row">
        <div className="file-manage-left">
          <div className="file-icon">📄</div>
          <div>
            <div className="file-manage-name">{file?.name || 'Current Resume'}</div>
            <div className="file-manage-meta">Uploaded on {analyzedAt}</div>
          </div>
        </div>
        <div className="file-manage-actions">
          <button className="btn-ghost" onClick={onReplace}>⤴ Replace File</button>
          <button className="btn-primary" style={{ width: 'auto', margin: 0, padding: '11px 20px' }} disabled={reanalyzing} onClick={onReanalyze}>
            {reanalyzing ? (<><span className="spinner" />Re-analyzing...</>) : '↻ Re-analyze Resume'}
          </button>
        </div>
      </div>
      <div className="report-actions-row">
        <button className="btn-outline" disabled={downloading} onClick={onDownload}>⬇ {downloading ? 'Building PDF...' : 'Download Report'}</button>
        <button className="btn-outline" onClick={onShare}>🔗 Share Report</button>
        <button className="btn-outline" disabled={downloading} onClick={onSave}>💾 Save Report</button>
      </div>
    </div>
  )
}

function Toast({ message }) {
  if (!message) return null
  return <div className="toast">{message}</div>
}

export default function App() {
  const [mode, setMode] = useState('analysis')
  const [file, setFile] = useState(null)
  const [jdText, setJdText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [enhanced, setEnhanced] = useState(false)
  const [analyzedAt, setAnalyzedAt] = useState('')
  const [downloading, setDownloading] = useState(false)
  const [toast, setToast] = useState('')

  const canSubmit = file && (mode === 'analysis' || jdText.trim().length > 20) && !loading

  useEffect(() => {
    if (!toast) return
    const t = setTimeout(() => setToast(''), 2500)
    return () => clearTimeout(t)
  }, [toast])

  async function handleSubmit() {
    setError('')
    setLoading(true)
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
      setAnalyzedAt(new Date().toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }))
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

  function navigate(target) {
    if (target === 'dashboard') {
      if (!result) setMode('analysis')
      return
    }
    if (target === 'builder') {
      setResult(null)
      setMode('builder')
      return
    }
    reset()
    setMode(target)
  }

  async function downloadReport() {
    setDownloading(true)
    try {
      const res = await fetch(`${API_URL}/api/analysis-report`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ result, resume_filename: file?.name || '' }),
      })
      if (!res.ok) throw new Error('Could not build the report.')
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'resume-analysis-report.pdf'
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } catch (e) {
      setToast(e.message || 'Download failed.')
    } finally {
      setDownloading(false)
    }
  }

  async function shareReport() {
    const top = result.career_matches?.[0]
    const text = `My resume scored ${result.job_readiness_score}/100 (${result.score_label}) on AKOps Resume AI!${top ? `\nTop career match: ${top.title} (${top.match_percent}%)` : ''}\n\nAnalyze yours free at AKOps Resume AI.`
    if (navigator.share) {
      try { await navigator.share({ title: 'My Resume Analysis', text }) } catch {}
      return
    }
    try {
      await navigator.clipboard.writeText(text)
      setToast('Summary copied to clipboard!')
    } catch {
      setToast('Could not copy — try downloading the report instead.')
    }
  }

  return (
    <div>
      <BackgroundOrbs />
      <SiteHeader />
      <div className="app-shell">
        <Sidebar mode={mode} result={result} onNavigate={navigate} />
        <div className="main-content">
          <div className="page">
            {!result && (
              <>
                <Hero />
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

            {mode === 'builder' && !result && (
              <>
                <TabGroup mode={mode} setMode={setMode} />
                <ResumeBuilder />
              </>
            )}

            {result && (
              <>
                <ScorePanel result={result} />
                {mode === 'match' && (
                  <JdMatchCard matchPercent={result.match_percent} matched={result.matched_skills} missing={result.missing_skills} />
                )}
                <SummaryPanel result={result} analyzedAt={analyzedAt} />
                <EnhancedCard result={result} />
                <StrengthsAndImprove strengths={result.strengths} suggestions={result.improvement_suggestions || []} />
                <CareerMatches matches={result.career_matches} detectedSkills={result.detected_skills} />
                <FileManageAndReport
                  file={file}
                  analyzedAt={analyzedAt}
                  onReplace={reset}
                  onReanalyze={handleSubmit}
                  reanalyzing={loading}
                  onDownload={downloadReport}
                  onSave={downloadReport}
                  onShare={shareReport}
                  downloading={downloading}
                />
                <div className="reset-row">
                  <button className="btn-ghost" onClick={reset}>↺ Analyze another resume</button>
                </div>
              </>
            )}

            <div className="footer">
              <div className="footer-trust-v2">
                <div className="footer-trust-item"><div className="footer-trust-icon">🔒</div><div className="footer-trust-title">Privacy First</div><div className="footer-trust-sub">Your data is always protected</div></div>
                <div className="footer-trust-item"><div className="footer-trust-icon">🖥️</div><div className="footer-trust-title">Local AI Processing</div><div className="footer-trust-sub">Analysis happens on secure servers</div></div>
                <div className="footer-trust-item"><div className="footer-trust-icon">🚫</div><div className="footer-trust-title">No Resume Storage</div><div className="footer-trust-sub">We never store your resume</div></div>
              </div>
              Built with ❤ by <b>AKOps Labs</b> · Free & open, no AI subscription needed
            </div>
          </div>
        </div>
      </div>

      <ChatWidget />
      <Toast message={toast} />
    </div>
  )
}
