// Hero illustration: an instrument-cluster ring around a road view with the RideShield helmet and a
// detection box. It is a composition, not a measurement: it is tagged "Illustration" and shows no
// scores or counts. It is a dark device surface in both themes, like a real dash.
export function ClusterArt() {
  const ticks = Array.from({ length: 41 }, (_, i) => i)
  const pt = (r: number, deg: number) => {
    const a = ((deg - 90) * Math.PI) / 180
    return [280 + r * Math.cos(a), 280 + r * Math.sin(a)]
  }
  return (
    <svg className="cluster-art" viewBox="0 0 560 560" role="img" aria-label="Illustration: an instrument cluster with a helmet detection box over a road view">
      <defs>
        <clipPath id="view">
          <circle cx="280" cy="280" r="188" />
        </clipPath>
        <linearGradient id="road" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#0d0d15" />
          <stop offset="1" stopColor="#1f1b36" />
        </linearGradient>
        <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#c4b8ff" />
          <stop offset="1" stopColor="#8b6cff" stopOpacity="0.25" />
        </linearGradient>
        <linearGradient id="scanfill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#8b6cff" stopOpacity="0" />
          <stop offset="1" stopColor="#8b6cff" stopOpacity="0.3" />
        </linearGradient>
      </defs>

      <circle cx="280" cy="280" r="270" fill="#0b0b12" stroke="rgba(255,255,255,0.14)" strokeWidth="1.5" />
      <path d={`M ${pt(240, 135)} A 240 240 0 1 1 ${pt(240, 405)}`} fill="none" stroke="rgba(255,255,255,0.09)" strokeWidth="14" strokeLinecap="round" />
      <g className="arc-live">
        <path d={`M ${pt(240, 135)} A 240 240 0 0 1 ${pt(240, 300)}`} fill="none" stroke="url(#ring)" strokeWidth="14" strokeLinecap="round" />
      </g>
      {ticks.map((i) => {
        const deg = 135 + (270 * i) / 40
        const major = i % 5 === 0
        const [x1, y1] = pt(214, deg)
        const [x2, y2] = pt(major ? 196 : 205, deg)
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={major ? 'rgba(238,237,245,0.65)' : 'rgba(238,237,245,0.22)'} strokeWidth={major ? 2 : 1} />
      })}

      <g clipPath="url(#view)">
        <rect x="80" y="80" width="400" height="400" fill="url(#road)" />
        <g stroke="rgba(196,184,255,0.34)" strokeWidth="2" fill="none">
          <path d="M280 190 L100 480" />
          <path d="M280 190 L460 480" />
        </g>
        <path className="road-line" d="M280 190 L280 480" stroke="rgba(238,237,245,0.5)" strokeWidth="3" fill="none" />
        <rect x="80" y="258" width="400" height="1" fill="rgba(255,255,255,0.1)" />
        <image href="/brand/mark-night.png" x="204" y="248" width="156" height="154" preserveAspectRatio="xMidYMid meet" />
        <g>
          <rect x="196" y="246" width="172" height="162" fill="none" stroke="#3ddc97" strokeWidth="3" />
          <rect x="196" y="218" width="82" height="28" fill="#3ddc97" />
          <text x="206" y="238" fontFamily="var(--mono)" fontSize="16" fontWeight="600" fill="#07070c">helmet</text>
          <g stroke="#3ddc97" strokeWidth="6" fill="none">
            <path d="M196 268v-22h22M368 268v-22h-22M196 386v22h22M368 386v22h-22" />
          </g>
        </g>
        <g className="scan">
          <rect x="80" y="130" width="400" height="60" fill="url(#scanfill)" />
          <rect x="80" y="188" width="400" height="2" fill="#8b6cff" />
        </g>
      </g>
      <circle cx="280" cy="280" r="188" fill="none" stroke="rgba(255,255,255,0.16)" strokeWidth="1.5" />

      <text x="280" y="522" textAnchor="middle" fontFamily="var(--font)" fontSize="13" fontWeight="600" fill="#c4b8ff">
        Illustration
      </text>
    </svg>
  )
}
