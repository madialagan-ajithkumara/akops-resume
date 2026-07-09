export default function Logo({ size = 32 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" className="logo-mark" xmlns="http://www.w3.org/2000/svg">
      <rect width="100" height="100" rx="22" fill="#10B981" />
      <ellipse cx="32" cy="50" rx="22" ry="18" fill="none" stroke="#0F172A" strokeWidth="7" />
      <ellipse cx="68" cy="50" rx="22" ry="18" fill="none" stroke="#0F172A" strokeWidth="7" />
      <text
        x="32"
        y="51"
        textAnchor="middle"
        dominantBaseline="central"
        fontFamily="Sora, Inter, sans-serif"
        fontWeight="800"
        fontSize="21"
        fill="#0F172A"
      >
        A
      </text>
      <text
        x="68"
        y="51"
        textAnchor="middle"
        dominantBaseline="central"
        fontFamily="Sora, Inter, sans-serif"
        fontWeight="800"
        fontSize="21"
        fill="#0F172A"
      >
        K
      </text>
    </svg>
  )
}
