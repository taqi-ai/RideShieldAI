import { Link } from 'react-router-dom'
import { BRAND } from '../config/brand'

// Placeholder mark (shield + gauge arc). Replace this file's SVG when the final logo is ready.
export function LogoMark({ size = 30 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <path d="M16 2.5 4.5 6.6v8.2c0 7 4.6 11.9 11.5 14.7 6.9-2.8 11.5-7.7 11.5-14.7V6.6L16 2.5Z" stroke="#c4b8ff" strokeWidth="1.6" strokeLinejoin="round" />
      <path d="M9.6 17.6a6.4 6.4 0 1 1 12.8 0" stroke="#8f73ff" strokeWidth="2.2" strokeLinecap="round" />
      <path d="m16 17.6 3.6-4.4" stroke="#ecebf4" strokeWidth="1.8" strokeLinecap="round" />
      <circle cx="16" cy="17.6" r="1.5" fill="#ecebf4" />
    </svg>
  )
}

export function Logo({ to = '/' }: { to?: string }) {
  return (
    <Link to={to} className="logo" aria-label={`${BRAND.name} home`}>
      <LogoMark />
      <span>{BRAND.short}</span>
      <span className="ai">AI</span>
    </Link>
  )
}
