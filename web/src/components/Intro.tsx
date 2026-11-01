import { useEffect, useState } from 'react'

// Full-screen logo curtain on the first landing-page visit of a session (never with reduced motion).
// The animation is CSS (.intro-overlay), so it lifts on time even if JavaScript is slow; React only adds
// the Skip control and removes the layer once it is done. The inline script in index.html decides whether
// to play it, by putting "intro" or "no-intro" on <html> before first paint.
export function Intro() {
  const [gone, setGone] = useState(false)
  useEffect(() => {
    const t = window.setTimeout(() => setGone(true), 2600)
    return () => window.clearTimeout(t)
  }, [])
  if (gone) return null
  const skip = () => {
    document.documentElement.classList.remove('intro')
    document.documentElement.classList.add('no-intro')
    setGone(true)
  }
  return (
    <div aria-hidden className="intro-overlay">
      <img src="/brand/logo-night.png" width={1068} height={376} alt="" />
      <button type="button" tabIndex={-1} className="intro-skip" onClick={skip}>
        Skip
      </button>
    </div>
  )
}
