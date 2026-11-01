import { Link } from 'react-router-dom'
import { ArrowRight, Check, FilmSlate } from '@phosphor-icons/react'
import { BRAND } from '../config/brand'
import { HeroDemo } from '../components/HeroDemo'
import { Photo } from '../hooks/useAsset'
import { usePageMeta } from '../hooks/usePageMeta'
import { MODELS } from '../inference/models'

const delay = (ms: number) => ({ '--d': `${ms}ms` }) as React.CSSProperties

// Writes the pointer position straight to CSS so the tile glow follows the cursor without re-rendering.
function glow(e: React.PointerEvent<HTMLElement>) {
  const r = e.currentTarget.getBoundingClientRect()
  e.currentTarget.style.setProperty('--mx', `${e.clientX - r.left}px`)
  e.currentTarget.style.setProperty('--my', `${e.clientY - r.top}px`)
}

export default function Home() {
  usePageMeta(`${BRAND.name} | Helmet detection that runs in your browser`, BRAND.description)
  return (
    <>
      <section className="hero2" id="product" aria-labelledby="hero-title">
        <div aria-hidden className="slab" />
        <div className="container hero2-grid">
          <div>
            <h1 id="hero-title">
              <span className="hero-line">
                <span style={delay(80)}>Spot every rider</span>
              </span>
              <span className="hero-line">
                <span style={delay(180)}>without a helmet.</span>
              </span>
            </h1>
            <p className="lead hero-fade" style={delay(380)}>
              RideShield AI finds riders without helmets in traffic footage. The model runs in your browser, so nothing is uploaded.
            </p>
            <div className="actions hero-fade" style={delay(500)}>
              <Link to="/test-drive" className="btn btn-primary">
                Experience RideShield <ArrowRight size={18} className="arrow" />
              </Link>
              <Link to="/#how" className="btn">
                Explore the Technology
              </Link>
            </div>
          </div>
          <div className="hero-fade" style={delay(300)}>
            <HeroDemo />
          </div>
        </div>
      </section>

      <section className="section" id="how">
        <div className="container">
          <div className="section-head reveal">
            <h2>From footage to findings.</h2>
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

      <section className="section alt" id="capabilities">
        <div className="container">
          <div className="section-head reveal">
            <h2>What the model does.</h2>
          </div>
          <div className="tiles">
            <article className="tile s4 dark reveal" onPointerMove={glow}>
              <Photo src="/img/detection.jpg" className="tile-photo" />
              <h3>Helmet detection</h3>
              <p>The trained model recognises two classes. Each detection carries its own confidence score, and no-helmet is the one violation it flags.</p>
              <div className="legend-boxes">
                <span className="legend-box" style={{ color: 'var(--dev-ok)' }}><i />helmet</span>
                <span className="legend-box" style={{ color: 'var(--dev-bad)' }}><i />nohelmet</span>
              </div>
            </article>
            <article className="tile s2 reveal" onPointerMove={glow}>
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
              <h3>One rider, one count</h3>
              <p>Riders are tracked across frames, so a person who stays in view is counted once, not once per frame. Counts come from real detections only.</p>
            </article>
            <article className="tile s3 reveal" onPointerMove={glow}>
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

      <section className="section">
        <div className="container idea">
          <div className="reveal">
            <h2>Built for the bike.</h2>
            <p>
              RideShield was designed to ride on the motorcycle: a camera at the dashboard that checks the helmet before the ride starts. What you can try here is the detection half of that idea.
            </p>
            <Link to="/on-bike" className="btn btn-primary">
              Read the idea <ArrowRight size={18} className="arrow" />
            </Link>
          </div>
          <figure className="figure reveal">
            <img src="/img/on-bike-concept.jpg" alt="Concept render of a motorcycle dashboard screen with green detection boxes on two riders" width={1774} height={887} loading="lazy" />
            <small>Concept render. The on-bike hardware has not been built.</small>
          </figure>
        </div>
      </section>

      <section className="section alt">
        <div className="container teaser">
          <div className="reveal">
            <h2>See RideShield in action.</h2>
            <p>Watch the 10-second trailer.</p>
            <Link to="/trailer" className="btn btn-primary">
              Open the Trailer Page <FilmSlate size={18} />
            </Link>
          </div>
          <div className="trailer-frame reveal">
            <video src="/media/rideshield-trailer.mp4" poster="/media/rideshield-trailer-poster.jpg" controls playsInline preload="metadata" />
          </div>
        </div>
      </section>

      <section className="section alt cta-section">
        <Photo src="/img/cta-road.jpg" className="cta-photo" />
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
