import { useEffect, useRef, useState } from 'react'
import ResumeBuilder from './ResumeBuilder'
import ChatWidget from './ChatWidget'
import Logo from './Logo'
import Icon from './Icon'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const NAV_ITEMS = [
  { key: 'analysis', icon: Icon.chart, label: 'Resume Analysis' },
  { key: 'match', icon: Icon.target, label: 'JD Match' },
  { key: 'builder', icon: Icon.file, label: 'Resume Builder' },
]

function SiteHeader({ mode, onNavigate, onHome }) {
  return (
    <div className="site-header">
      <div className="site-header-inner">
        <button className="brand-block" onClick={onHome} aria-label="Go to home">
          <Logo size={32} />
          <div className="brand-text-title">AKOps <span className="grad">Resume AI</span></div>
        </button>

        <nav className="top-nav">
          {NAV_ITEMS.map((it) => (
            <button
              key={it.key}
              className={`top-nav-item ${mode === it.key ? 'active' : ''}`}
              onClick={() => onNavigate(it.key)}
            >
              <it.icon size={15} />{it.label}
            </button>
          ))}
        </nav>

        <div className="header-right">
          <a className="social-link" href="https://www.youtube.com/@AkOpsTamil" target="_blank" rel="noreferrer" aria-label="AKOps Tamil on YouTube" title="YouTube">
            <Icon.youtube size={16} />
          </a>
          <a className="social-link" href="https://www.linkedin.com/in/ajithkumara-madialagan-256625169/" target="_blank" rel="noreferrer" aria-label="Ajithkumara Madialagan on LinkedIn" title="LinkedIn">
            <Icon.linkedin size={15} />
          </a>
          <span className="header-powered">Powered by <b>AKOps Labs</b></span>
        </div>
      </div>
    </div>
  )
}

function BottomNav({ mode, onNavigate }) {
  return (
    <div className="bottom-nav">
      <div className="bottom-nav-row">
        {NAV_ITEMS.map((it) => (
          <button
            key={it.key}
            className={`bottom-nav-item ${mode === it.key ? 'active' : ''}`}
            onClick={() => onNavigate(it.key)}
          >
            <it.icon size={19} />{it.label}
          </button>
        ))}
      </div>
    </div>
  )
}

function ScorePreview() {
  const rows = [
    { label: 'ATS Compatibility', pct: 92 },
    { label: 'Skills Match', pct: 88 },
    { label: 'Impact & Clarity', pct: 79 },
  ]
  return (
    <div className="score-preview">
      <div className="score-preview-head">
        <span className="score-preview-title">Sample Analysis</span>
        <span className="score-preview-live"><span className="score-preview-dot" />Preview</span>
      </div>
      <div className="score-preview-body">
        <div className="score-preview-ring">
          <div className="score-ring" style={{ '--pct': 87 }}>
            <div className="score-ring-inner"><div className="score-preview-number">87</div></div>
          </div>
        </div>
        <div className="score-preview-bars">
          {rows.map((r) => (
            <div className="score-preview-bar-row" key={r.label}>
              <span className="score-preview-bar-label">{r.label}</span>
              <div className="score-preview-track"><div className="score-preview-fill" style={{ width: `${r.pct}%` }} /></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function Hero({ onUploadClick }) {
  return (
    <div className="hero-section">
      <div className="container">
        <div className="hero-grid">
          <div>
            <span className="eyebrow"><Icon.shield size={12} />Local AI · No Resume Storage</span>
            <h1 className="hero-heading">Know exactly how your resume<br className="hero-break" /> performs <span className="accent">before</span> you apply</h1>
            <p className="hero-desc">Instant ATS scoring, job-description matching, and a resume builder — all running on local ML with zero AI subscription cost.</p>
            <div className="hero-cta-row">
              <button className="btn-hero" onClick={onUploadClick}><Icon.upload size={16} />Upload Resume</button>
              <span className="hero-meta">No sign-up · Free forever</span>
            </div>
          </div>
          <ScorePreview />
        </div>
      </div>
    </div>
  )
}

function TrustMetrics() {
  const metrics = [
    { icon: Icon.sparkle, label: 'Free Beta Access' },
    { icon: Icon.shield, label: 'Privacy First' },
    { icon: Icon.award, label: '25+ Career Paths' },
    { icon: Icon.clock, label: '<60s Analysis' },
  ]
  return (
    <div className="metrics-strip">
      <div className="container">
        <div className="metrics-row">
          {metrics.map((m) => (
            <div className="metric-item" key={m.label}>
              <m.icon size={15} />
              <span>{m.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function Dropzone({ file, onChange }) {
  const [dragActive, setDragActive] = useState(false)

  function handleDrop(e) {
    e.preventDefault()
    setDragActive(false)
    const dropped = e.dataTransfer.files?.[0]
    if (dropped) onChange(dropped)
  }

  return (
    <label
      className={`dropzone ${dragActive ? 'drag-active' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
      onDragLeave={() => setDragActive(false)}
      onDrop={handleDrop}
    >
      <div className="dropzone-icon"><Icon.upload size={19} /></div>
      <span className="dropzone-label">{file ? 'Change PDF Resume' : 'Drag & drop your resume here'}</span>
      <span className="dropzone-hint">{file ? file.name : 'or click to choose a PDF'}</span>
      <input type="file" accept="application/pdf" onChange={(e) => onChange(e.target.files?.[0] || null)} />
    </label>
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
          <div className="score-label">Overall Resume Score</div>
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
      <div className="card-title"><Icon.file size={15} />Summary</div>
      <div className="summary-text">{result.summary}</div>
      <div className="stat-chip-grid">
        <div className="stat-chip"><div className="stat-chip-top"><Icon.brief size={12} />Experience</div><div className="stat-chip-value">{result.experience_level}</div></div>
        <div className="stat-chip"><div className="stat-chip-top"><Icon.file size={12} />Length</div><div className="stat-chip-value">{result.estimated_pages}</div></div>
        <div className="stat-chip"><div className="stat-chip-top"><Icon.file size={12} />File Type</div><div className="stat-chip-value">{result.file_type}</div></div>
        <div className="stat-chip"><div className="stat-chip-top"><Icon.clock size={12} />Analyzed</div><div className="stat-chip-value">{analyzedAt}</div></div>
      </div>
    </div>
  )
}

function StrengthsAndImprove({ strengths, suggestions }) {
  return (
    <div className="grid-2" style={{ marginBottom: 16 }}>
      <div className="card">
        <div className="card-title"><Icon.checkCircle size={15} />Strengths</div>
        {strengths.length === 0 && <div className="summary-text">Add more recognizable skills to your resume to surface strengths here.</div>}
        {strengths.map((s) => (
          <div className="info-item" key={s.category}>
            <div className="info-item-icon good"><Icon.check size={13} /></div>
            <div>
              <div className="info-item-title">{s.category}</div>
              <div className="info-item-desc">{s.skills.slice(0, 4).join(', ')}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="card">
        <div className="card-title"><Icon.alert size={15} />Areas to Improve</div>
        {suggestions.length === 0 && <div className="summary-text">Nothing major — this resume covers the fundamentals well.</div>}
        {suggestions.map((s, i) => (
          <div className="info-item" key={i}>
            <div className="info-item-icon warn"><Icon.alert size={13} /></div>
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

  if (state === 'sent') return <div className="feedback-thanks"><Icon.check size={13} />Thanks — that helps the model improve for the next person.</div>

  return (
    <div className="feedback-row">
      {state === 'idle' && (
        <>
          <span className="feedback-label">Was "{topCategory}" the right top match?</span>
          <button className="feedback-btn" onClick={() => sendFeedback(topCategory)}>Yes</button>
          <button className="feedback-btn" onClick={() => setState('correcting')}>No</button>
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
      <div className="card-title"><Icon.trending size={15} />Best Job Matches</div>
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
            {showAll ? 'Show fewer matches' : `View all ${matches.length} matches`}
            <Icon.chevronDown size={14} style={{ transform: showAll ? 'rotate(180deg)' : 'none' }} />
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
          <div className="card-title"><Icon.sparkle size={15} />Enhanced AI Summary</div>
          <div className="summary-text" style={{ color: 'var(--text-faint)' }}>{result.enhanced_error}</div>
        </div>
      )
    }
    return null
  }
  return (
    <div className="card enhanced-card">
      <div className="card-title"><Icon.sparkle size={15} />Enhanced AI Summary</div>
      <div className="summary-text">{result.enhanced_summary}</div>
      {result.enhanced_tips && result.enhanced_tips.length > 0 && (
        <div style={{ marginTop: 14 }}>
          <div style={{ fontWeight: 700, fontSize: 12.5, marginBottom: 7 }}>Suggested improvements</div>
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
          <div className="card-title" style={{ marginBottom: 4 }}><Icon.target size={15} />JD Match Score</div>
          <div style={{ color: 'var(--text-faint)', fontSize: 12.5 }}>How well this resume lines up with the job description</div>
        </div>
        <div className="big">{matchPercent}%</div>
      </div>
      <div style={{ marginTop: 16 }}>
        <div style={{ fontWeight: 700, fontSize: 12.5, marginBottom: 6 }}>Matched skills</div>
        <div className="skill-tags">
          {matched.length === 0 && <span style={{ color: 'var(--text-faint)', fontSize: 12 }}>No direct skill overlap detected.</span>}
          {matched.map((s) => <span className="skill-tag have" key={s}>{s}</span>)}
        </div>
      </div>
      <div style={{ marginTop: 14 }}>
        <div style={{ fontWeight: 700, fontSize: 12.5, marginBottom: 6 }}>Missing skills from JD</div>
        <div className="skill-tags">
          {missing.length === 0 && <span style={{ color: 'var(--text-faint)', fontSize: 12 }}>None — great coverage!</span>}
          {missing.map((s) => <span className="skill-tag missing" key={s}>{s}</span>)}
        </div>
      </div>
    </div>
  )
}

function JdImprovementsCard({ missing }) {
  if (!missing || missing.length === 0) {
    return (
      <div className="card">
        <div className="card-title"><Icon.alert size={15} />How to Improve for This JD</div>
        <div className="summary-text">Great coverage — no missing skills detected from this job description.</div>
      </div>
    )
  }
  return (
    <div className="card">
      <div className="card-title"><Icon.alert size={15} />How to Improve for This JD</div>
      {missing.map((skill) => (
        <div className="info-item" key={skill}>
          <div className="info-item-icon warn"><Icon.alert size={13} /></div>
          <div>
            <div className="info-item-title">Add {skill}</div>
            <div className="info-item-desc">This skill appears in the job description but wasn't found on your resume.</div>
          </div>
        </div>
      ))}
    </div>
  )
}

function FileManageAndReport({ file, analyzedAt, onReplace, onReanalyze, reanalyzing, onDownload, onSave, onShare, downloading }) {
  return (
    <div className="card" style={{ padding: 0 }}>
      <div className="file-manage-row">
        <div className="file-manage-left">
          <div className="file-icon"><Icon.file size={16} /></div>
          <div>
            <div className="file-manage-name">{file?.name || 'Current Resume'}</div>
            <div className="file-manage-meta">Uploaded on {analyzedAt}</div>
          </div>
        </div>
        <div className="file-manage-actions">
          <button className="btn-ghost" onClick={onReplace}><Icon.upload size={14} />Replace File</button>
          <button className="btn-primary inline" disabled={reanalyzing} onClick={onReanalyze}>
            {reanalyzing ? (<><span className="spinner" />Re-analyzing...</>) : (<><Icon.refresh size={14} />Re-analyze</>)}
          </button>
        </div>
      </div>
      <div className="report-actions-row">
        <button className="btn-outline" disabled={downloading} onClick={onDownload}><Icon.download size={14} />{downloading ? 'Building PDF...' : 'Download Report'}</button>
        <button className="btn-outline" onClick={onShare}><Icon.share size={14} />Share Report</button>
        <button className="btn-outline" disabled={downloading} onClick={onSave}><Icon.save size={14} />Save Report</button>
      </div>
    </div>
  )
}

// ---- Quick feedback survey (posts to a Google Form, no backend/database needed) ----
// Setup: create a Google Form with these 3 questions, grab its formResponse URL and each
// question's entry.XXXXXX ID (right-click a form field > Inspect, or open the form's
// pre-filled-link generator), then paste them in below.
const FEEDBACK_FORM_ACTION = 'https://docs.google.com/forms/d/e/1FAIpQLSftTW79XZWbaqt_2i2AZGW7tW1Dm3gD8NNC1kzeLCIIym5XqA/formResponse'
const FEEDBACK_ENTRY_IDS = {
  accurate: 'entry.1053407393',
  recommend: 'entry.16786293',
  nextFeature: 'entry.1499971786',
}
const FEEDBACK_STORAGE_KEY = 'akops_feedback_done'

function FeedbackSurvey() {
  const [dismissed, setDismissed] = useState(() => {
    try { return localStorage.getItem(FEEDBACK_STORAGE_KEY) === '1' } catch { return false }
  })
  const [answers, setAnswers] = useState({ accurate: '', recommend: '', nextFeature: '' })
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState(false)

  if (dismissed) return null

  function pick(key, value) {
    setAnswers((a) => ({ ...a, [key]: value }))
  }

  function persistDismiss() {
    try { localStorage.setItem(FEEDBACK_STORAGE_KEY, '1') } catch {}
    setDismissed(true)
  }

  async function submit() {
    setSubmitting(true)
    try {
      const body = new URLSearchParams()
      body.append(FEEDBACK_ENTRY_IDS.accurate, answers.accurate)
      body.append(FEEDBACK_ENTRY_IDS.recommend, answers.recommend)
      body.append(FEEDBACK_ENTRY_IDS.nextFeature, answers.nextFeature)
      await fetch(FEEDBACK_FORM_ACTION, { method: 'POST', mode: 'no-cors', body })
    } catch {
      // fire-and-forget: even if this fails, don't block or alarm the user
    } finally {
      setSubmitting(false)
      setDone(true)
      try { localStorage.setItem(FEEDBACK_STORAGE_KEY, '1') } catch {}
    }
  }

  const allAnswered = answers.accurate && answers.recommend && answers.nextFeature

  if (done) {
    return (
      <div className="card feedback-card">
        <div className="feedback-thanks"><Icon.check size={15} />Thanks — that helps shape what's next.</div>
      </div>
    )
  }

  return (
    <div className="card feedback-card">
      <div className="feedback-head">
        <div className="card-title" style={{ marginBottom: 0 }}><Icon.sparkle size={15} />Quick feedback (15 seconds)</div>
        <button className="feedback-dismiss" onClick={persistDismiss} aria-label="Dismiss feedback survey"><Icon.close size={14} /></button>
      </div>

      <div className="feedback-q">
        <div className="feedback-q-title">Was the result accurate?</div>
        <div className="feedback-options">
          {['Yes', 'Partially', 'No'].map((opt) => (
            <button
              key={opt}
              className={`feedback-opt ${answers.accurate === opt ? 'selected' : ''}`}
              onClick={() => pick('accurate', opt)}
            >
              {opt}
            </button>
          ))}
        </div>
      </div>

      <div className="feedback-q">
        <div className="feedback-q-title">Would you recommend this tool?</div>
        <div className="feedback-options">
          {['Yes', 'No'].map((opt) => (
            <button
              key={opt}
              className={`feedback-opt ${answers.recommend === opt ? 'selected' : ''}`}
              onClick={() => pick('recommend', opt)}
            >
              {opt}
            </button>
          ))}
        </div>
      </div>

      <div className="feedback-q">
        <div className="feedback-q-title">What feature would you like next?</div>
        <div className="feedback-options">
          {['AI Career Coach', 'DevOps Roadmap', 'Cloud Skills Assessment', 'Resume Builder Improvements'].map((opt) => (
            <button
              key={opt}
              className={`feedback-opt ${answers.nextFeature === opt ? 'selected' : ''}`}
              onClick={() => pick('nextFeature', opt)}
            >
              {opt}
            </button>
          ))}
        </div>
      </div>

      <button className="btn-primary inline" disabled={!allAnswered || submitting} onClick={submit}>
        {submitting ? (<><span className="spinner" />Sending...</>) : 'Submit feedback'}
      </button>
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
  const uploadRef = useRef(null)

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
    if (target === 'builder') {
      setResult(null)
      setMode('builder')
      return
    }
    reset()
    setMode(target)
  }

  function goHome() {
    reset()
    setMode('analysis')
  }

  function scrollToUpload() {
    uploadRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
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
      <SiteHeader mode={mode} onNavigate={navigate} onHome={goHome} />

      {!result && mode === 'analysis' && <Hero onUploadClick={scrollToUpload} />}
      {!result && mode === 'analysis' && <TrustMetrics />}

      <div className="page">
        {!result && mode !== 'builder' && (
          <div className="section" ref={uploadRef}>
            <div className="section-head">
              <div className="section-title"><Icon.upload size={17} />{mode === 'analysis' ? 'Upload Your Resume' : 'Match Against a Job Description'}</div>
              <div className="section-sub">{mode === 'analysis' ? 'Get an instant score, skill breakdown, and career matches.' : 'See exactly what overlaps and what\'s missing.'}</div>
            </div>
            <div className="card">
              <Dropzone file={file} onChange={setFile} />

              {mode === 'match' && (
                <>
                  <div className="section-label">Paste job description</div>
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
                <span>Try Enhanced AI Summary <span className="badge-optional">optional</span></span>
              </label>

              <button className="btn-primary" disabled={!canSubmit} onClick={handleSubmit}>
                {loading ? (<><span className="spinner" />Analyzing...</>) : mode === 'analysis' ? (<><Icon.sparkle size={15} />Analyze Resume</>) : (<><Icon.target size={15} />Check JD Match</>)}
              </button>

              {error && <div className="error-box"><Icon.alert size={15} />{error}</div>}
            </div>
          </div>
        )}

        {mode === 'builder' && !result && <ResumeBuilder />}

        {result && mode === 'match' && (
          <div className="section">
            <JdMatchCard matchPercent={result.match_percent} matched={result.matched_skills} missing={result.missing_skills} />
            <JdImprovementsCard missing={result.missing_skills} />
            <EnhancedCard result={result} />
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
            <FeedbackSurvey />
            <div className="reset-row">
              <button className="btn-ghost" onClick={reset}><Icon.refresh size={14} />Check another resume</button>
            </div>
          </div>
        )}

        {result && mode === 'analysis' && (
          <div className="section">
            <ScorePanel result={result} />
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
            <FeedbackSurvey />
            <div className="reset-row">
              <button className="btn-ghost" onClick={reset}><Icon.refresh size={14} />Analyze another resume</button>
            </div>
          </div>
        )}
      </div>

      <div className="footer">
        <div className="container footer-inner">
          <div className="footer-trust">
            <span className="footer-trust-item"><Icon.lock size={14} />Privacy First</span>
            <span className="footer-trust-item"><Icon.shield size={14} />No Resume Storage</span>
          </div>
          <div>Powered by <b>AKOps Labs</b></div>
        </div>
      </div>

      <BottomNav mode={mode} onNavigate={navigate} />
      <ChatWidget />
      <Toast message={toast} />
    </div>
  )
}
