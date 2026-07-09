import { useState } from 'react'
import Icon from './Icon'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function Field({ label, value, onChange, placeholder }) {
  return (
    <div className="field">
      <label>{label}</label>
      <input value={value || ''} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} />
    </div>
  )
}

function TagList({ tags, onRemove, onAdd }) {
  const [draft, setDraft] = useState('')
  return (
    <div>
      <div className="skill-tags">
        {tags.map((t, i) => (
          <span className="skill-tag have" key={t + i}>
            {t}
            <button className="tag-x" onClick={() => onRemove(i)}>×</button>
          </span>
        ))}
      </div>
      <div className="add-row">
        <input
          placeholder="Add a skill and press Enter"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && draft.trim()) {
              onAdd(draft.trim())
              setDraft('')
            }
          }}
        />
      </div>
    </div>
  )
}

function BulletEditor({ bullets, onChange }) {
  function updateBullet(i, val) {
    const next = [...bullets]
    next[i] = val
    onChange(next)
  }
  function removeBullet(i) {
    onChange(bullets.filter((_, idx) => idx !== i))
  }
  function addBullet() {
    onChange([...bullets, ''])
  }
  return (
    <div className="bullet-editor">
      {bullets.map((b, i) => (
        <div className="bullet-row" key={i}>
          <input value={b} onChange={(e) => updateBullet(i, e.target.value)} placeholder="Describe an achievement..." />
          <button className="btn-x" onClick={() => removeBullet(i)}>×</button>
        </div>
      ))}
      <button className="btn-add-small" onClick={addBullet}><Icon.chevronDown size={12} style={{ transform: 'rotate(-90deg)' }} />Add bullet</button>
    </div>
  )
}

export default function ResumeBuilder() {
  const [file, setFile] = useState(null)
  const [resume, setResume] = useState(null)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState('')
  const [error, setError] = useState('')

  async function handleParse() {
    if (!file) return
    setError('')
    setLoading(true)
    try {
      const form = new FormData()
      form.append('resume', file)
      const res = await fetch(`${API_URL}/api/parse`, { method: 'POST', body: form })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Could not parse that resume.')
      setResume(data)
    } catch (e) {
      setError(e.message || 'Network error — is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  async function handleExport(format) {
    if (!resume) return
    setExporting(format)
    setError('')
    try {
      const res = await fetch(`${API_URL}/api/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume, format }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || 'Export failed.')
      }
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${(resume.contact.name || 'resume').replace(/\s+/g, '_')}.${format}`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError(e.message || 'Export failed.')
    } finally {
      setExporting('')
    }
  }

  function updateContact(key, value) {
    setResume((r) => ({ ...r, contact: { ...r.contact, [key]: value } }))
  }

  function updateSummary(value) {
    setResume((r) => ({ ...r, summary: value }))
  }

  // -- skills --
  function addCategory() {
    setResume((r) => ({ ...r, skill_categories: [...r.skill_categories, { category: 'New Category', skills: [] }] }))
  }
  function removeCategory(i) {
    setResume((r) => ({ ...r, skill_categories: r.skill_categories.filter((_, idx) => idx !== i) }))
  }
  function renameCategory(i, name) {
    setResume((r) => {
      const next = [...r.skill_categories]
      next[i] = { ...next[i], category: name }
      return { ...r, skill_categories: next }
    })
  }
  function addSkill(catIdx, skill) {
    setResume((r) => {
      const next = [...r.skill_categories]
      next[catIdx] = { ...next[catIdx], skills: [...next[catIdx].skills, skill] }
      return { ...r, skill_categories: next }
    })
  }
  function removeSkill(catIdx, skillIdx) {
    setResume((r) => {
      const next = [...r.skill_categories]
      next[catIdx] = { ...next[catIdx], skills: next[catIdx].skills.filter((_, i) => i !== skillIdx) }
      return { ...r, skill_categories: next }
    })
  }

  // -- generic list helpers for experience / education / projects --
  function addEntry(field, blank) {
    setResume((r) => ({ ...r, [field]: [...r[field], blank] }))
  }
  function removeEntry(field, idx) {
    setResume((r) => ({ ...r, [field]: r[field].filter((_, i) => i !== idx) }))
  }
  function updateEntry(field, idx, patch) {
    setResume((r) => {
      const next = [...r[field]]
      next[idx] = { ...next[idx], ...patch }
      return { ...r, [field]: next }
    })
  }

  // -- certifications (flat strings) --
  function addCert(value) {
    setResume((r) => ({ ...r, certifications: [...r.certifications, value] }))
  }
  function removeCert(idx) {
    setResume((r) => ({ ...r, certifications: r.certifications.filter((_, i) => i !== idx) }))
  }

  if (!resume) {
    return (
      <div className="section">
        <div className="section-head">
          <div className="section-title"><Icon.file size={17} />Resume Builder</div>
          <div className="section-sub">Parse your resume into editable sections, then export a polished PDF or Word doc.</div>
        </div>
        <div className="card">
          <label className="dropzone">
            <div className="dropzone-icon"><Icon.upload size={19} /></div>
            <span className="dropzone-label">{file ? 'Change PDF Resume' : 'Drag & drop your resume here'}</span>
            <span className="dropzone-hint">{file ? file.name : 'or click to choose a PDF to build/edit'}</span>
            <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          </label>
          <button className="btn-primary" disabled={!file || loading} onClick={handleParse}>
            {loading ? (<><span className="spinner" />Reading your resume...</>) : (<><Icon.sparkle size={15} />Parse Into Editable Sections</>)}
          </button>
          {error && <div className="error-box"><Icon.alert size={15} />{error}</div>}
          <p className="hint-text">
            We'll pull out your contact info, summary, skills (grouped by category), experience, education,
            projects and certifications so you can edit, add, or remove anything before downloading a
            freshly formatted resume.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="section">
      <div className="card">
        <div className="card-title"><Icon.user size={15} />Contact</div>
        <div className="field-grid">
          <Field label="Full name" value={resume.contact.name} onChange={(v) => updateContact('name', v)} />
          <Field label="Email" value={resume.contact.email} onChange={(v) => updateContact('email', v)} />
          <Field label="Phone" value={resume.contact.phone} onChange={(v) => updateContact('phone', v)} />
          <Field label="Location" value={resume.contact.location} onChange={(v) => updateContact('location', v)} />
          <Field label="LinkedIn" value={resume.contact.linkedin} onChange={(v) => updateContact('linkedin', v)} />
          <Field label="GitHub" value={resume.contact.github} onChange={(v) => updateContact('github', v)} />
        </div>
      </div>

      <div className="card">
        <div className="card-title"><Icon.file size={15} />Summary</div>
        <textarea className="jd-input" style={{ minHeight: 100 }} value={resume.summary} onChange={(e) => updateSummary(e.target.value)} />
      </div>

      <div className="card">
        <div className="card-title"><Icon.chart size={15} />Skills by Category</div>
        {resume.skill_categories.map((cat, i) => (
          <div className="entry-card" key={i}>
            <div className="entry-head">
              <input className="entry-title-input" value={cat.category} onChange={(e) => renameCategory(i, e.target.value)} />
              <button className="btn-x" onClick={() => removeCategory(i)}>Remove</button>
            </div>
            <TagList tags={cat.skills} onRemove={(si) => removeSkill(i, si)} onAdd={(s) => addSkill(i, s)} />
          </div>
        ))}
        <button className="btn-add-small" onClick={addCategory}>+ Add skill category</button>
      </div>

      <div className="card">
        <div className="card-title"><Icon.brief size={15} />Experience</div>
        {resume.experience.map((entry, i) => (
          <div className="entry-card" key={i}>
            <div className="field-grid">
              <Field label="Title" value={entry.title} onChange={(v) => updateEntry('experience', i, { title: v })} />
              <Field label="Company" value={entry.company} onChange={(v) => updateEntry('experience', i, { company: v })} />
              <Field label="Dates" value={entry.dates} onChange={(v) => updateEntry('experience', i, { dates: v })} />
            </div>
            <BulletEditor bullets={entry.bullets} onChange={(b) => updateEntry('experience', i, { bullets: b })} />
            <button className="btn-x" onClick={() => removeEntry('experience', i)}>Remove this role</button>
          </div>
        ))}
        <button className="btn-add-small" onClick={() => addEntry('experience', { title: '', company: '', dates: '', bullets: [] })}>
          + Add experience
        </button>
      </div>

      <div className="card">
        <div className="card-title"><Icon.trending size={15} />Projects</div>
        {resume.projects.map((entry, i) => (
          <div className="entry-card" key={i}>
            <Field label="Project title" value={entry.title} onChange={(v) => updateEntry('projects', i, { title: v })} />
            <BulletEditor bullets={entry.bullets} onChange={(b) => updateEntry('projects', i, { bullets: b })} />
            <button className="btn-x" onClick={() => removeEntry('projects', i)}>Remove project</button>
          </div>
        ))}
        <button className="btn-add-small" onClick={() => addEntry('projects', { title: '', bullets: [] })}>+ Add project</button>
      </div>

      <div className="card">
        <div className="card-title"><Icon.grad size={15} />Education</div>
        {resume.education.map((entry, i) => (
          <div className="entry-card" key={i}>
            <div className="field-grid">
              <Field label="Degree" value={entry.degree} onChange={(v) => updateEntry('education', i, { degree: v })} />
              <Field label="Institution" value={entry.institution} onChange={(v) => updateEntry('education', i, { institution: v })} />
              <Field label="Dates" value={entry.dates} onChange={(v) => updateEntry('education', i, { dates: v })} />
            </div>
            <button className="btn-x" onClick={() => removeEntry('education', i)}>Remove</button>
          </div>
        ))}
        <button className="btn-add-small" onClick={() => addEntry('education', { degree: '', institution: '', dates: '' })}>+ Add education</button>
      </div>

      <div className="card">
        <div className="card-title"><Icon.award size={15} />Certifications</div>
        <TagList tags={resume.certifications} onRemove={removeCert} onAdd={addCert} />
      </div>

      <div className="card">
        <div className="card-title"><Icon.download size={15} />Download Your Polished Resume</div>
        <div className="download-row">
          <button className="btn-primary" disabled={!!exporting} onClick={() => handleExport('pdf')}>
            {exporting === 'pdf' ? (<><span className="spinner" />Building PDF...</>) : (<><Icon.file size={15} />Download as PDF</>)}
          </button>
          <button className="btn-primary" disabled={!!exporting} onClick={() => handleExport('docx')}>
            {exporting === 'docx' ? (<><span className="spinner" />Building Word doc...</>) : (<><Icon.file size={15} />Download as Word</>)}
          </button>
        </div>
        {error && <div className="error-box"><Icon.alert size={15} />{error}</div>}
      </div>

      <div className="reset-row">
        <button className="btn-ghost" onClick={() => { setResume(null); setFile(null) }}><Icon.refresh size={14} />Start over with another resume</button>
      </div>
    </div>
  )
}
