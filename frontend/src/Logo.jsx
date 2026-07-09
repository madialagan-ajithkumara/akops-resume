export default function Logo({ size = 42 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" className="logo-mark" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="logoGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#16a34a" />
          <stop offset="1" stopColor="#4ade80" />
        </linearGradient>
      </defs>
      <rect width="100" height="100" rx="24" fill="url(#logoGrad)" />
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M50 18 L79 80 H64.5 L58.5 66 H41.5 L35.5 80 H21 L50 18 Z M50 42 L43 58 H57 L50 42 Z"
        fill="#fff"
      />
    </svg>
  )
}
