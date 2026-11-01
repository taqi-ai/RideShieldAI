import { Link } from 'react-router-dom'
import {
  ArrowRight,
  ChartLineUp,
  Cpu,
  Crosshair,
  FilmSlate,
  HardHat,
  ListChecks,
  LockKey,
  Play,
  Scan,
  VideoCamera,
  WarningOctagon,
} from '@phosphor-icons/react'
import { BRAND } from '../config/brand'
import { ClusterArt } from '../components/ClusterArt'
import { Gauge } from '../components/Gauge'
import { usePageMeta } from '../hooks/usePageMeta'

export default function Home() {
  usePageMeta(`${BRAND.name} | Helmet detection that runs in your browser`, BRAND.description)
  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <h1>
              Road safety that <em>sees</em> the helmet.
            </h1>
            <p className="lead">
              RideShield AI spots riders without helmets in traffic footage. The YOLO model runs in your browser, so nothing is uploaded.
            </p>
            <div className="actions">
              <Link to="/test-drive" className="btn btn-primary">
                Experience RideShield <ArrowRight size={18} />
              </Link>
              <Link to="/#how" className="btn">
                Explore the Technology
              </Link>
            </div>
          </div>
          <ClusterArt />
        </div>
      </section>

      <section className="section" id="product">
        <div className="container">
          <div className="section-head reveal">
            <span className="eyebrow">The test drive</span>
            <h2>A cockpit for computer vision.</h2>
            <p>Point your webcam or drop in a traffic clip. Boxes, confidence and counts update as the model runs.</p>
          </div>
          <Link to="/test-drive" className="preview reveal" aria-label="Open the interactive test drive">
            <div className="preview-bar">
              <span className="chip violet">TEST DRIVE</span>
              <span className="chip">Camera</span>
              <span className="chip">Upload video</span>
              <span className="chip spacer">Opens the live experience</span>
            </div>
            <div className="preview-body">
              <div className="preview-view">
                <div className="road" />
                <img src="/img/bike.png" alt="" loading="lazy" />
                <span className="btn btn-primary btn-sm preview-cta">
                  Start the test <Play size={16} weight="fill" />
                </span>
              </div>
              <div className="preview-side">
                <div className="preview-gauge">
                  <Gauge value={0} max={30} label="Inference FPS" size={190} idle />
                </div>
                <ul className="preview-list">
                  <li>
                    Classes <b>helmet, nohelmet</b>
                  </li>
                  <li>
                    Engine <b>WebGPU or WASM</b>
                  </li>
                  <li>
                    Upload to server <b>none</b>
                  </li>
                </ul>
              </div>
            </div>
          </Link>
        </div>
      </section>

      <section className="section" id="how" style={{ background: 'var(--bg-2)' }}>
        <div className="container">
          <div className="section-head reveal">
            <h2>From footage to findings in four steps.</h2>
          </div>
          <ol className="steps reveal">
            <li className="step">
              <span className="step-icon"><VideoCamera size={26} /></span>
              <div>
                <h3>Bring footage</h3>
                <p>Use your webcam or choose a traffic video from your device.</p>
              </div>
            </li>
            <li className="step">
              <span className="step-icon"><Scan size={26} /></span>
              <div>
                <h3>Detect</h3>
                <p>A YOLO model finds helmets and riders without them, frame by frame.</p>
              </div>
            </li>
            <li className="step">
              <span className="step-icon"><Crosshair size={26} /></span>
              <div>
                <h3>See the overlay</h3>
                <p>Boxes and confidence scores are drawn right on the footage.</p>
              </div>
            </li>
            <li className="step">
              <span className="step-icon"><ListChecks size={26} /></span>
              <div>
                <h3>Review</h3>
                <p>Counters and an event list summarise what the model found in this session.</p>
              </div>
            </li>
          </ol>
        </div>
      </section>

      <section className="section" id="capabilities">
        <div className="container">
          <div className="section-head reveal">
            <h2>What the model does, and nothing it doesn't.</h2>
          </div>
          <div className="bento">
            <article className="cell a hero-cell reveal">
              <img src="/img/helmet.png" alt="" loading="lazy" />
              <HardHat className="cell-icon" size={30} />
              <h3>Helmet detection</h3>
              <p>The trained model recognises two classes: helmet and nohelmet. Each detection carries its own confidence score.</p>
            </article>
            <article className="cell warn reveal">
              <WarningOctagon className="cell-icon" size={28} />
              <h3>No-helmet flags</h3>
              <p>The one violation supported today. Shown in coral.</p>
            </article>
            <article className="cell grid-bg reveal">
              <Crosshair className="cell-icon" size={28} />
              <h3>Live overlays</h3>
              <p>Bounding boxes on every processed frame.</p>
            </article>
            <article className="cell wide violet reveal">
              <ChartLineUp className="cell-icon" size={28} />
              <h3>Statistics and event history</h3>
              <p>Counts come from real detections. Riders are tracked across frames so one person is not counted twice.</p>
            </article>
            <article className="cell wide reveal">
              <Cpu className="cell-icon" size={28} />
              <h3>AI in the browser</h3>
              <p>ONNX Runtime Web uses WebGPU when your browser supports it and falls back to WebAssembly when it does not.</p>
            </article>
            <article className="cell wide grid-bg reveal">
              <LockKey className="cell-icon" size={28} />
              <h3>Private by design</h3>
              <p>Frames are processed on your device. There is no upload and no inference server.</p>
            </article>
          </div>
        </div>
      </section>

      <section className="section" style={{ background: 'var(--bg-2)' }}>
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
                <span className="chip violet">30-SECOND FILM IN PRODUCTION</span>
                <h3>Trailer Coming Soon</h3>
              </div>
            </div>
          </Link>
        </div>
      </section>
    </>
  )
}
