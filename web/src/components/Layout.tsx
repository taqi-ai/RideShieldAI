import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { motion, useMotionValueEvent, useScroll } from 'motion/react'
import { GithubLogo, List, X } from '@phosphor-icons/react'
import { BRAND } from '../config/brand'
import { useReveal } from '../hooks/useReveal'
import { Logo } from './Logo'
import { ThemeToggle } from './ThemeToggle'

const LINKS = [
  { to: '/#product', label: 'Product' },
  { to: '/project', label: 'Project' },
  { to: '/on-bike', label: 'On-Bike' },
  { to: '/roadmap', label: 'Roadmap' },
  { to: '/test-drive', label: 'Test It Out' },
  { to: '/trailer', label: 'Trailer' },
] as const

// Pages that open on the violet band, so the nav is white over them until you scroll.
const BAND_PAGES = ['/', '/project', '/on-bike', '/roadmap']

function ScrollManager() {
  const { pathname, hash } = useLocation()
  useEffect(() => {
    if (hash) {
      // Wait a frame so the target exists after a route change.
      const id = requestAnimationFrame(() => document.getElementById(hash.slice(1))?.scrollIntoView())
      return () => cancelAnimationFrame(id)
    }
    window.scrollTo(0, 0)
  }, [pathname, hash])
  return null
}

function Nav() {
  const [open, setOpen] = useState(false)
  const [solid, setSolid] = useState(false)
  const { pathname } = useLocation()
  const { scrollY } = useScroll()
  useMotionValueEvent(scrollY, 'change', (v) => setSolid(v > 24))
  const close = () => setOpen(false)
  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false)
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open])

  return (
    <header className={`nav${solid ? ' solid' : ''}${open ? ' open' : ''}${BAND_PAGES.includes(pathname) ? ' on-hero' : ''}`}>
      <div className="container nav-inner">
        <Logo />
        <nav className="nav-links" aria-label="Primary">
          {LINKS.map((l) =>
            l.to.includes('#') ? (
              <Link key={l.to} to={l.to}>
                {l.label}
              </Link>
            ) : (
              <NavLink key={l.to} to={l.to}>
                {l.label}
              </NavLink>
            ),
          )}
        </nav>
        <div className="nav-end">
          <ThemeToggle />
          <Link to="/test-drive" className="btn btn-primary btn-sm nav-cta">
            Experience RideShield
          </Link>
          <button className="icon-btn nav-toggle" aria-expanded={open} aria-controls="mobile-menu" aria-label={open ? 'Close menu' : 'Open menu'} onClick={() => setOpen((o) => !o)}>
            {open ? <X size={22} /> : <List size={22} />}
          </button>
        </div>
      </div>
      {open && (
        <motion.nav
          id="mobile-menu"
          className="nav-menu"
          aria-label="Primary mobile"
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {LINKS.map((l) => (
            <Link key={l.to} to={l.to} onClick={close}>
              {l.label}
            </Link>
          ))}
          <Link to="/test-drive" className="btn btn-primary" onClick={close}>
            Experience RideShield
          </Link>
        </motion.nav>
      )}
    </header>
  )
}

function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div>
            <Logo variant="full" />
            <p className="note">
              The live test processes media in your browser. Webcam frames and uploaded videos stay on your device and are never sent to a server.
            </p>
          </div>
          <div>
            <h4>Product</h4>
            <ul>
              <li><Link to="/#product">Overview</Link></li>
              <li><Link to="/#how">How it works</Link></li>
              <li><Link to="/project">The project</Link></li>
              <li><Link to="/on-bike">Built for the bike</Link></li>
              <li><Link to="/roadmap">Future scope</Link></li>
              <li><Link to="/test-drive">Test drive</Link></li>
              <li><Link to="/trailer">Trailer</Link></li>
            </ul>
          </div>
          <div>
            <h4>Project</h4>
            <ul>
              <li>
                <a href={BRAND.repoUrl} target="_blank" rel="noreferrer noopener" style={{ display: 'inline-flex', gap: 8, alignItems: 'center' }}>
                  <GithubLogo size={18} /> Source on GitHub
                </a>
              </li>
            </ul>
          </div>
        </div>
        <p className="footer-base">{BRAND.name}. Detection runs locally with ONNX Runtime Web.</p>
      </div>
    </footer>
  )
}

export function Layout() {
  useReveal()
  return (
    <>
      <a className="skip-link" href="#main">Skip to content</a>
      <ScrollManager />
      <Nav />
      <main id="main">
        <Outlet />
      </main>
      <Footer />
    </>
  )
}
