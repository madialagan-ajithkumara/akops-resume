export default function Logo({ size = 32 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" className="logo-mark" xmlns="http://www.w3.org/2000/svg">
      <rect width="100" height="100" rx="22" fill="#10B981" />
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M50 20 L77 78 H63.5 L58 65 H42 L36.5 78 H23 L50 20 Z M50 42 L44 57 H56 L50 42 Z"
        fill="#0F172A"
      />
    </svg>
  )
}
