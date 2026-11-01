import { Link } from 'react-router-dom'
import { BRAND } from '../config/brand'

// Logo art lives in public/brand (built from "ai assets/logo full.png" by
// web/scripts/build_brand_assets.py). Night art shows on dark, day art on light; the swap is pure CSS
// keyed on the theme attribute, so there is no flash on load.
type Variant = 'lockup' | 'full'

const ART: Record<Variant, { night: string; day: string; w: number; h: number }> = {
  lockup: { night: '/brand/lockup-night.png', day: '/brand/lockup-day.png', w: 1280, h: 376 },
  full: { night: '/brand/logo-night.png', day: '/brand/logo-day.png', w: 1068, h: 376 },
}

export function Logo({ variant = 'lockup', to = '/' }: { variant?: Variant; to?: string }) {
  const a = ART[variant]
  return (
    <Link to={to} className="logo" aria-label={`${BRAND.name} home`}>
      <img className="theme-art-night" src={a.night} width={a.w} height={a.h} alt="" />
      <img className="theme-art-day" src={a.day} width={a.w} height={a.h} alt="" />
    </Link>
  )
}

// Helmet mark on dark instrument surfaces (always the night art).
export function MarkNight({ className }: { className?: string }) {
  return <img className={className} src="/brand/mark-night.png" width={381} height={376} alt="" />
}
