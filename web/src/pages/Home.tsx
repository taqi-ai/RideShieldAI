import { useRef } from 'react'
import { Link } from 'react-router-dom'
import { motion, useReducedMotion, useScroll, useSpring, useTransform } from 'motion/react'
import { ArrowRight, ChartLineUp, Check, Cpu, FilmSlate, HardHat, Stack } from '@phosphor-icons/react'
import { BRAND } from '../config/brand'
import { CockpitPreview } from '../components/CockpitPreview'
import { Intro } from '../components/Intro'
import { MarkNight } from '../components/Logo'
import { usePageMeta } from '../hooks/usePageMeta'
import { MODELS } from '../inference/models'

const delay = (ms: number) => ({ '--d': `${ms}ms` }) as React.CSSProperties

// Writes the pointer position straight to CSS so the tile glow follows the cursor without re-rendering.
function glow(e: React.PointerEvent<HTMLElement>) {
  const r = e.currentTarget.getBoundingClientRect()
  e.currentTarget.style.setProperty('--mx', `${e.clientX - r.left}px`)
  e.currentTarget.style.setProperty('--my', `${e.clientY - r.top}px`)
}

function Hero() {
  const reduce = useReducedMotion()
  const stage = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({ target: stage, offset: ['start 0.8', 'start 0.15'] })
  const p = useSpring(scrollYProgress, { stiffness: 120, damping: 26, mass: 0.4 })
  const rotateX = useTransform(p, [0, 1], reduce ? [0, 0] : [20, 0])
  const scale = useTransform(p, [0, 1], reduce ? [1, 1] : [0.92, 1])

  return (
    <section aria-labelledby="hero-title" className="hero" id="product">
      <div aria-hidden className="hero-glow" />
      <div aria-hidden className="hero-grid-bg" />
      <div className="container">
        <div className="hero-cols">
          <div>
            <p className="hero-note hero-fade" style={delay(60)}>
              Browser-based helmet detection for road safety
            </p>
            <h1 id="hero-title">
              <span className="hero-line">
                <span style={delay(120)}>Spot every rider</span>
              </span>
              <span className="hero-line">
                <span style={delay(220)}>without a helmet.</span>
              </span>
            </h1>
            <p className="lead hero-fade" style={delay(420)}>
              RideShield AI finds riders without helmets in traffic footage. The model runs in your browser, so nothing is uploaded.
            </p>
            <div className="actions hero-fade" style={delay(540)}>
              <Link to="/test-drive" className="btn btn-primary">
                Experience RideShield <ArrowRight size={18} className="arrow" />
              </Link>
              <Link to="/#how" className="btn">
                Explore the Technology
              </Link>
            </div>
          </div>
          <ul className="hero-facts hero-fade" style={delay(650)} aria-label="Facts about the shipped build">
            <li><b>2</b><span>classes: helmet and nohelmet</span></li>
            <li><b>3</b><span>models you can switch between</span></li>
            <li><b>0</b><span>frames uploaded, everything runs on your device</span></li>
            <li><b>WebGPU</b><span>with a WebAssembly fallback for other browsers</span></li>
          </ul>
        </div>

        <div ref={stage} className="plane-wrap">
          <div className="hero-plane" style={delay(380)}>
            <motion.div style={{ rotateX, scale, transformOrigin: '50% 0%' }}>
              <Link to="/test-drive" className="plane edge" aria-label="Open the live test drive">
                <CockpitPreview />
              </Link>
            </motion.div>
          </div>
          <div aria-hidden className="plane-fade" />
          {/* Decorative: clicks pass through to the plane link underneath. */}
          <span aria-hidden className="btn btn-primary btn-sm plane-open">
            Open the live test <ArrowRight size={16} className="arrow" />
          </span>
        </div>
      </div>
    </section>
  )
}

export default function Home() {
  usePageMeta(`${BRAND.name} | Helmet detection that runs in your browser`, BRAND.description)
  return (
    <>
      <Intro />
      <Hero />

      <section className="section alt" id="how">
        <div className="container">
          <div className="section-head reveal">
            <h2>From footage to findings in four steps.</h2>
          </div>
          <ol className="steps reveal">
            <li className="step">
              <span className="step-n">1</span>
              <h3>Bring footage</h3>
              <p>Use your webcam or choose a traffic video from your device.</p>
            </li>
            <li className="step">
              <span className="step-n">2</span>
              <h3>Detect</h3>
              <p>A YOLO model finds helmets and riders without them, frame by frame.</p>
            </li>
            <li className="step">
              <span className="step-n">3</span>
              <h3>See the overlay</h3>
              <p>Boxes and confidence scores are drawn right on the footage.</p>
            </li>
            <li className="step">
              <span className="step-n">4</span>
              <h3>Review</h3>
              <p>Counters and an event list summarise what the model found in this session.</p>
            </li>
          </ol>
        </div>
      </section>

      <section className="section" id="capabilities">
        <div className="container">
          <div className="section-head reveal">
            <h2>What the model does, and nothing it doesn't.</h2>
          </div>
          <div className="tiles">
            <article className="tile s4 dark reveal" onPointerMove={glow}>
              <MarkNight className="tile-mark" />
              <span className="tile-icon" style={{ background: 'oklch(0.26 0.04 290)', color: 'var(--dev-accent)' }}><HardHat size={20} /></span>
              <h3>Helmet detection</h3>
              <p>The trained model recognises two classes. Each detection carries its own confidence score, and no-helmet is the one violation it flags.</p>
              <div className="legend-boxes">
                <span className="legend-box" style={{ color: 'var(--dev-ok)' }}><i />helmet</span>
                <span className="legend-box" style={{ color: 'var(--dev-bad)' }}><i />nohelmet</span>
              </div>
            </article>
            <article className="tile s2 reveal" onPointerMove={glow}>
              <span className="tile-icon"><Cpu size={20} /></span>
              <h3>Fast in the browser</h3>
              <p>WebGPU when your browser has it, WebAssembly when it does not.</p>
              <div className="bars">
                <div className="bar-row">
                  <span><b>WebGPU</b>, about 20 ms a frame</span>
                  <div className="bar-track"><div className="bar-fill" style={{ width: '17%' }} /></div>
                </div>
                <div className="bar-row">
                  <span><b>WebAssembly</b>, about 115 ms a frame</span>
                  <div className="bar-track"><div className="bar-fill" style={{ width: '100%', opacity: 0.55 }} /></div>
                </div>
              </div>
              <small>Measured with YOLO26n on one development laptop. Your speed will differ.</small>
            </article>
            <article className="tile s3 reveal" onPointerMove={glow}>
              <span className="tile-icon"><ChartLineUp size={20} /></span>
              <h3>One rider, one count</h3>
              <p>Riders are tracked across frames, so a person who stays in view is counted once, not once per frame. Counts come from real detections only.</p>
            </article>
            <article className="tile s3 reveal" onPointerMove={glow}>
              <span className="tile-icon"><Check size={20} /></span>
              <h3>Nothing leaves your device</h3>
              <ul className="checklist">
                <li><Check size={16} weight="bold" />Frames stay in your browser</li>
                <li><Check size={16} weight="bold" />No account or sign-in</li>
                <li><Check size={16} weight="bold" />No tracking scripts or analytics</li>
              </ul>
            </article>
            <article className="tile s6 reveal" onPointerMove={glow}>
              <div className="tile-split">
                <div>
                  <span className="tile-icon"><Stack size={20} /></span>
                  <h3>Three models, one switch</h3>
                  <p>All three are trained on the same two classes. Switch between them in the test drive and compare results on your own footage.</p>
                </div>
                <ul className="model-rows">
                  {MODELS.map((m) => (
                    <li key={m.id}>
                      <span className="mr-name">{m.label}</span>
                      <span className="mr-blurb">{m.blurb}</span>
                      <span className="mr-size">{(m.sizeBytes / 1048576).toFixed(1)} MiB</span>
                    </li>
                  ))}
                </ul>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section className="section alt">
        <div className="container teaser">
          <div className="reveal">
            <h2>See RideShield in action.</h2>
            <p>A 30-second film is in production. The trailer page is ready for it.</p>
            <Link to="/trailer" className="btn btn-primary">
              Check Out the Trailer <FilmSlate size={18} />
            </Link>
          </div>
          <Link to="/trailer" className="trailer-frame reveal" aria-label="Open the trailer page">
            <div className="poster">
              <div className="poster-inner">
                <MarkNight />
                <span className="chip">30-second film in production</span>
                <h3>Trailer Coming Soon</h3>
              </div>
            </div>
          </Link>
        </div>
      </section>

      <section className="section">
        <div className="container cta-band reveal">
          <h2>Try it on your own footage.</h2>
          <p>Open the test drive, use your camera or upload a clip, and watch the boxes and counts update.</p>
          <Link to="/test-drive" className="btn btn-primary">
            Experience RideShield <ArrowRight size={18} className="arrow" />
          </Link>
        </div>
      </section>
    </>
  )
}
