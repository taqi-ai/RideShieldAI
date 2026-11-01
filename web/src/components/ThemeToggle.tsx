import { Moon, Sun } from '@phosphor-icons/react'

const KEY = 'rideshield-theme'

type VT = { ready: Promise<void> }

// Day and night switch, same behaviour as Ascora: where the browser supports view transitions the new theme
// grows out of the button as a circle (the old frame stays underneath, so nothing flashes). Elsewhere, and
// for people who prefer reduced motion, colours cross-fade instead. The theme lives on <html data-theme>,
// so the button needs no React state and the icons are swapped in CSS.
export function ThemeToggle({ className }: { className?: string }) {
  function toggle(e: React.MouseEvent<HTMLButtonElement>) {
    const root = document.documentElement
    const next = root.dataset.theme === 'light' ? 'dark' : 'light'
    const apply = () => {
      root.dataset.theme = next
      root.style.colorScheme = next
      try {
        localStorage.setItem(KEY, next)
      } catch {
        /* private mode: the choice just lasts for this visit */
      }
    }
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const start = (document as Document & { startViewTransition?: (cb: () => void) => VT }).startViewTransition?.bind(document)

    if (!start || reduce) {
      root.classList.add('theme-fade')
      apply()
      window.setTimeout(() => root.classList.remove('theme-fade'), 450)
      return
    }
    const r = e.currentTarget.getBoundingClientRect()
    const x = r.left + r.width / 2
    const y = r.top + r.height / 2
    const radius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y))
    const t = start(apply)
    t.ready
      .then(() =>
        root.animate(
          { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`] },
          { duration: 650, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', pseudoElement: '::view-transition-new(root)' },
        ),
      )
      .catch(() => undefined)
  }

  return (
    <button className={`icon-btn${className ? ` ${className}` : ''}`} onClick={toggle} aria-label="Toggle day and night mode" title="Day or night mode">
      <Sun size={20} className="sun-only" />
      <Moon size={20} className="moon-only" />
    </button>
  )
}
