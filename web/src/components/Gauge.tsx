import { useId } from 'react'

interface GaugeProps {
  value: number
  max: number
  label: string
  unit?: string
  size?: number
  decimals?: number
  tone?: 'accent' | 'ok' | 'bad'
  idle?: boolean
}

const START = 135 // degrees clockwise from 12 o'clock; the 90 degree gap sits at the bottom
const SWEEP = 270

const polar = (cx: number, cy: number, r: number, deg: number) => {
  const a = ((deg - 90) * Math.PI) / 180
  return [cx + r * Math.cos(a), cy + r * Math.sin(a)] as const
}

const arc = (cx: number, cy: number, r: number, from: number, to: number) => {
  const [x1, y1] = polar(cx, cy, r, from)
  const [x2, y2] = polar(cx, cy, r, to)
  const large = to - from > 180 ? 1 : 0
  return `M ${x1.toFixed(2)} ${y1.toFixed(2)} A ${r} ${r} 0 ${large} 1 ${x2.toFixed(2)} ${y2.toFixed(2)}`
}

// Circular instrument. It only ever shows a measured value passed in by the caller.
// Colours come from theme variables so it reads in day and night mode.
export function Gauge({ value, max, label, unit, size = 220, decimals = 0, tone = 'accent', idle }: GaugeProps) {
  const id = useId()
  const ratio = Math.max(0, Math.min(1, value / max))
  const c = 100
  const R = 84
  const color = tone === 'ok' ? 'var(--ok)' : tone === 'bad' ? 'var(--bad)' : 'var(--accent)'
  const ticks = Array.from({ length: 28 }, (_, i) => i)
  const needleDeg = START + SWEEP * ratio
  const [nx, ny] = polar(c, c, R - 20, needleDeg)

  return (
    <figure className="gauge" style={{ width: size }}>
    <svg
      width={size}
      height={size}
      viewBox="0 0 200 200"
      role="img"
      aria-label={idle ? `${label}: no data yet` : `${label}: ${value.toFixed(decimals)} ${unit ?? ''}`}
    >
      <defs>
        <linearGradient id={`${id}-g`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor={color} stopOpacity="0.4" />
          <stop offset="1" stopColor={color} />
        </linearGradient>
      </defs>
      <circle cx={c} cy={c} r={96} fill="var(--surface-2)" stroke="var(--line)" />
      <path d={arc(c, c, R, START, START + SWEEP)} stroke="var(--line-2)" strokeWidth="8" strokeLinecap="round" fill="none" />
      {ratio > 0.002 && (
        <path d={arc(c, c, R, START, START + SWEEP * ratio)} stroke={`url(#${id}-g)`} strokeWidth="8" strokeLinecap="round" fill="none" />
      )}
      {ticks.map((i) => {
        const deg = START + (SWEEP * i) / (ticks.length - 1)
        const major = i % 3 === 0
        const [x1, y1] = polar(c, c, R - 12, deg)
        const [x2, y2] = polar(c, c, R - (major ? 23 : 18), deg)
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={major ? 'var(--muted)' : 'var(--faint)'} strokeOpacity={major ? 0.9 : 0.5} strokeWidth={major ? 1.6 : 1} />
      })}
      <line
        x1={c}
        y1={c}
        x2={nx}
        y2={ny}
        stroke="var(--text)"
        strokeWidth="2.4"
        strokeLinecap="round"
        style={{ transition: 'all 0.35s cubic-bezier(0.16,1,0.3,1)' }}
      />
      <circle cx={c} cy={c} r="5.5" fill="var(--surface)" stroke="var(--text)" strokeWidth="2" />
      <text x={c} y={c + 52} textAnchor="middle" fontFamily="var(--display)" fontSize="42" fontWeight="800" fill="var(--text)">
        {idle ? '--' : value.toFixed(decimals)}
      </text>
    </svg>
    <figcaption>{unit ? `${label} (${unit})` : label}</figcaption>
    </figure>
  )
}
