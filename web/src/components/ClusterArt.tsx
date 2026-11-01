// Original hero illustration: an instrument-cluster ring around a road view with a detection box.
// It is a composition, not a measurement: it carries an "Illustrative" tag and shows no numbers.
export function ClusterArt() {
  const ticks = Array.from({ length: 41 }, (_, i) => i)
  const pt = (r: number, deg: number) => {
    const a = ((deg - 90) * Math.PI) / 180
    return [280 + r * Math.cos(a), 280 + r * Math.sin(a)]
  }
  return (
    <svg className="cluster-art" viewBox="0 0 560 560" role="img" aria-label="Illustration of a motorcycle instrument cluster showing a helmet detection box over a road view">
      <defs>
        <clipPath id="view">
          <circle cx="280" cy="280" r="188" />
        </clipPath>
        <linearGradient id="road" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#12121b" />
          <stop offset="1" stopColor="#1d1b30" />
        </linearGradient>
        <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#c4b8ff" />
          <stop offset="1" stopColor="#8f73ff" stopOpacity="0.2" />
        </linearGradient>
        <linearGradient id="scanfill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#8f73ff" stopOpacity="0" />
          <stop offset="1" stopColor="#8f73ff" stopOpacity="0.28" />
        </linearGradient>
      </defs>

      <circle cx="280" cy="280" r="268" fill="#0e0e15" stroke="rgba(255,255,255,0.08)" />
      <path d={`M ${pt(240, 135)} A 240 240 0 1 1 ${pt(240, 405)}`} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="14" strokeLinecap="round" />
      <path d={`M ${pt(240, 135)} A 240 240 0 0 1 ${pt(240, 300)}`} fill="none" stroke="url(#ring)" strokeWidth="14" strokeLinecap="round" />
      {ticks.map((i) => {
        const deg = 135 + (270 * i) / 40
        const major = i % 5 === 0
        const [x1, y1] = pt(214, deg)
        const [x2, y2] = pt(major ? 196 : 204, deg)
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={major ? 'rgba(236,235,244,0.6)' : 'rgba(236,235,244,0.2)'} strokeWidth={major ? 2 : 1} />
      })}

      <g clipPath="url(#view)">
        <rect x="80" y="80" width="400" height="400" fill="url(#road)" />
        <g stroke="rgba(196,184,255,0.35)" strokeWidth="2" fill="none">
          <path d="M280 200 L120 480" />
          <path d="M280 200 L440 480" />
        </g>
        <path className="road-line" d="M280 200 L280 480" stroke="rgba(236,235,244,0.5)" strokeWidth="3" fill="none" />
        <rect x="80" y="260" width="400" height="1" fill="rgba(255,255,255,0.08)" />
        <image href="/img/helmet.png" x="196" y="236" width="170" height="160" preserveAspectRatio="xMidYMid meet" />
        <g>
          <rect x="204" y="248" width="154" height="132" fill="none" stroke="#3ddc97" strokeWidth="3" />
          <rect x="204" y="222" width="74" height="26" fill="#3ddc97" />
          <text x="212" y="240" fontFamily="var(--mono)" fontSize="15" fontWeight="600" fill="#0a0a0e">helmet</text>
          <g stroke="#3ddc97" strokeWidth="5" fill="none">
            <path d="M204 266v-18h18M358 266v-18h-18M204 362v18h18M358 362v18h-18" />
          </g>
        </g>
        <g className="scan">
          <rect x="80" y="130" width="400" height="60" fill="url(#scanfill)" />
          <rect x="80" y="188" width="400" height="2" fill="#8f73ff" />
        </g>
      </g>
      <circle cx="280" cy="280" r="188" fill="none" stroke="rgba(255,255,255,0.14)" strokeWidth="1.5" />

      <g className="sweep">
        <path d="M280 280 L280 92" stroke="rgba(143,115,255,0.0)" strokeWidth="2" />
      </g>

      <g fontFamily="var(--mono)" fontSize="12" letterSpacing="1.4" fill="#8582a0">
        <text x="280" y="508" textAnchor="middle">YOLO26N  /  HELMET  /  NOHELMET</text>
        <text x="280" y="534" textAnchor="middle" fill="#c4b8ff">ILLUSTRATIVE</text>
      </g>
    </svg>
  )
}
