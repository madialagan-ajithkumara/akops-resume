import { useEffect, useRef, useState } from 'react'
import Icon from './Icon'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const GREETING = "Hi! I'm the AkOps Assistant. Ask me anything about resumes, job applications, interviews, or how to use this site — that's what I'm here for."

export default function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [configured, setConfigured] = useState(true) // assume yes until health check says otherwise
  const [messages, setMessages] = useState([{ role: 'assistant', text: GREETING }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const scrollRef = useRef(null)

  useEffect(() => {
    fetch(`${API_URL}/api/health`)
      .then((r) => r.json())
      .then((d) => setConfigured(!!d.chat_configured))
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, open, loading])

  async function send() {
    const text = input.trim()
    if (!text || loading) return
    setError('')
    setInput('')
    const history = messages.map((m) => ({ role: m.role, text: m.text }))
    setMessages((m) => [...m, { role: 'user', text }])
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Something went wrong.')
      setMessages((m) => [...m, { role: 'assistant', text: data.reply }])
    } catch (e) {
      setError(e.message || 'Network error — please try again.')
    } finally {
      setLoading(false)
    }
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="chat-widget">
      {open && (
        <div className="chat-panel">
          <div className="chat-header">
            <div>
              <div className="chat-header-title"><Icon.chat size={14} />AkOps Assistant</div>
              <div className="chat-header-sub">Resume & career questions only</div>
            </div>
            <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat"><Icon.close size={16} /></button>
          </div>

          <div className="chat-messages" ref={scrollRef}>
            {messages.map((m, i) => (
              <div className={`chat-bubble ${m.role}`} key={i}>{m.text}</div>
            ))}
            {loading && <div className="chat-bubble assistant chat-typing"><span /><span /><span /></div>}
            {!configured && (
              <div className="chat-bubble assistant chat-note">
                The chat assistant isn't turned on for this site yet — the site owner needs to add a free Gemini API key. In the meantime, try the Resume Analysis tool above!
              </div>
            )}
          </div>

          {error && <div className="chat-error">{error}</div>}

          <div className="chat-input-row">
            <input
              className="chat-input"
              placeholder={configured ? 'Ask about your resume...' : 'Chat assistant not configured yet'}
              value={input}
              disabled={!configured || loading}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
            />
            <button className="chat-send" disabled={!configured || loading || !input.trim()} onClick={send} aria-label="Send">
              <Icon.send size={14} />
            </button>
          </div>
        </div>
      )}

      <button className="chat-fab" onClick={() => setOpen((o) => !o)} aria-label="Open resume chat assistant">
        {open ? <Icon.close size={22} /> : <Icon.chat size={22} />}
      </button>
    </div>
  )
}
