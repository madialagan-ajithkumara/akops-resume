export default function Logo({ size = 32 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" className="logo-mark" xmlns="http://www.w3.org/2000/svg">
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M50 6 L91 92 H74 L66 74 H34 L26 92 H9 L50 6 Z M50 34 L40 58 H60 L50 34 Z"
        fill="#10B981"
      />
    </svg>
  )
}
