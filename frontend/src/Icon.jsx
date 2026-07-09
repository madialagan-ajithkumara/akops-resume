/*
 * Minimal line-icon set (Lucide-style, stroke-based) used throughout the
 * app instead of emoji, for a consistent, professional SaaS look.
 * Each icon is a small inline SVG so there are no external requests,
 * font-icon dependencies, or bundle-size surprises.
 */
const base = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.8,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
}

function Svg({ size = 18, children, ...rest }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base} {...rest}>
      {children}
    </svg>
  )
}

export const Icon = {
  chart: (p) => <Svg {...p}><path d="M3 3v18h18" /><rect x="7" y="12" width="3" height="6" /><rect x="12" y="8" width="3" height="10" /><rect x="17" y="5" width="3" height="13" /></Svg>,
  target: (p) => <Svg {...p}><circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="5" /><circle cx="12" cy="12" r="1" /></Svg>,
  file: (p) => <Svg {...p}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6" /></Svg>,
  upload: (p) => <Svg {...p}><path d="M12 16V4" /><path d="M6 10l6-6 6 6" /><path d="M4 20h16" /></Svg>,
  shield: (p) => <Svg {...p}><path d="M12 2 4 5v6c0 5 3.5 8.5 8 11 4.5-2.5 8-6 8-11V5Z" /></Svg>,
  lock: (p) => <Svg {...p}><rect x="4" y="11" width="16" height="9" rx="2" /><path d="M8 11V7a4 4 0 0 1 8 0v4" /></Svg>,
  check: (p) => <Svg {...p}><path d="M20 6 9 17l-5-5" /></Svg>,
  checkCircle: (p) => <Svg {...p}><circle cx="12" cy="12" r="9" /><path d="M8.5 12.5l2.3 2.3L16 9.5" /></Svg>,
  alert: (p) => <Svg {...p}><path d="M12 3 2 20h20Z" /><path d="M12 9v5" /><path d="M12 17.5v.01" /></Svg>,
  trending: (p) => <Svg {...p}><path d="M3 17l6-6 4 4 8-8" /><path d="M15 7h6v6" /></Svg>,
  download: (p) => <Svg {...p}><path d="M12 4v12" /><path d="M6 12l6 6 6-6" /><path d="M4 20h16" /></Svg>,
  share: (p) => <Svg {...p}><circle cx="6" cy="12" r="2.5" /><circle cx="17" cy="6" r="2.5" /><circle cx="17" cy="18" r="2.5" /><path d="M8.2 10.8l6.7-3.6" /><path d="M8.2 13.2l6.7 3.6" /></Svg>,
  save: (p) => <Svg {...p}><path d="M5 4h11l3 3v13H5z" /><path d="M8 4v6h8V4" /><path d="M8 20v-6h8v6" /></Svg>,
  refresh: (p) => <Svg {...p}><path d="M3 12a9 9 0 0 1 15.3-6.4L21 8" /><path d="M21 3v5h-5" /><path d="M21 12a9 9 0 0 1-15.3 6.4L3 16" /><path d="M3 21v-5h5" /></Svg>,
  swap: (p) => <Svg {...p}><path d="M7 4v13" /><path d="M3 13l4 4 4-4" /><path d="M17 20V7" /><path d="M21 11l-4-4-4 4" /></Svg>,
  sparkle: (p) => <Svg {...p}><path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18" /></Svg>,
  chat: (p) => <Svg {...p}><path d="M21 15a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z" /></Svg>,
  close: (p) => <Svg {...p}><path d="M18 6 6 18" /><path d="M6 6l12 12" /></Svg>,
  send: (p) => <Svg {...p}><path d="M22 2 11 13" /><path d="M22 2 15 22l-4-9-9-4Z" /></Svg>,
  chevronLeft: (p) => <Svg {...p}><path d="M15 18l-6-6 6-6" /></Svg>,
  chevronRight: (p) => <Svg {...p}><path d="M9 18l6-6-6-6" /></Svg>,
  chevronDown: (p) => <Svg {...p}><path d="M6 9l6 6 6-6" /></Svg>,
  youtube: (p) => <Svg {...p} strokeWidth="0" fill="currentColor"><path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.4 3.5 12 3.5 12 3.5s-7.4 0-9.4.6A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c2 .6 9.4.6 9.4.6s7.4 0 9.4-.6a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8ZM9.6 15.6V8.4L15.8 12Z" /></Svg>,
  linkedin: (p) => <Svg {...p} strokeWidth="0" fill="currentColor"><path d="M20.45 20.45h-3.56v-5.58c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.95v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.38-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.07 2.07 0 1 1 0-4.13 2.07 2.07 0 0 1 0 4.13ZM7.12 20.45H3.56V9h3.56v11.45Z" /></Svg>,
  user: (p) => <Svg {...p}><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 4-6 8-6s8 2 8 6" /></Svg>,
  brief: (p) => <Svg {...p}><rect x="3" y="7" width="18" height="13" rx="2" /><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /></Svg>,
  grad: (p) => <Svg {...p}><path d="M22 10 12 5 2 10l10 5 10-5Z" /><path d="M6 12v5c0 1.5 3 3 6 3s6-1.5 6-3v-5" /></Svg>,
  award: (p) => <Svg {...p}><circle cx="12" cy="8" r="5" /><path d="M8.5 12.5 7 21l5-3 5 3-1.5-8.5" /></Svg>,
  clock: (p) => <Svg {...p}><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 3" /></Svg>,
}

export default Icon
