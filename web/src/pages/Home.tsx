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
import { MarkNight } from '../components/Logo'
import { usePageMeta } from '../hooks/usePageMeta'

export default function Home() {
  usePageMeta(`${BRAND.name} | Helmet detection that runs in your browser`, BRAND.description)
  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <h1>Spot every rider without a helmet.</h1>
            <p className="lead">
              RideShield AI finds riders without helmets in traffic footage. The model runs in your browser, so nothing is uploaded.
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

      <section className="facts" aria-label="Facts about the shipped build">
        <div className="container facts-grid">
          <div className="fact"><b>2</b><span>classes: helmet and nohelmet</span></div>
          <div className="fact"><b>9.6 MiB</b><span>model, downloaded once then cached</span></div>
          <div className="fact"><b>0</b><span>frames uploaded, everything runs on your device</span></div>
          <div className="fact"><b>WebGPU</b><span>with a WebAssembly fallback for other browsers</span></div>
        </div>
      </section>

      <section className="section" id="product">
        <div className="container">
          <div className="section-head reveal">
            <h2>Try it on your own footage.</h2>
            <p>Open the test drive, use your camera or upload a clip, and watch boxes and counts update as the model runs.</p>
          </div>
          <Link to="/test-drive" className="preview reveal" aria-label="Open the interactive test drive">
            <div className="preview-bar">
              <span className="chip accent">Test drive</span>
              <span className="chip">Camera</span>
              <span className="chip">Upload video</span>
            </div>
            <div className="preview-body">
              <div className="preview-view">
                <svg className="bg" viewBox="0 0 800 450" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
                  <defs>
                    <linearGradient id="pv-road" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0" stopColor="#0b0b12" />
                      <stop offset="1" stopColor="#1d1936" />
                    </linearGradient>
                  </defs>
                  <rect width="800" height="450" fill="url(#pv-road)" />
                  <g stroke="rgba(196,184,255,0.3)" strokeWidth="2">
                    <path d="M400 190 L40 450" />
                    <path d="M400 190 L760 450" />
                  </g>
                  <path d="M400 190 L400 450" stroke="rgba(238,237,245,0.35)" strokeWidth="3" strokeDasharray="14 18" />
                  <rect y="188" width="800" height="1" fill="rgba(255,255,255,0.1)" />
                </svg>
                <span className="bracket tl" /><span className="bracket tr" /><span className="bracket bl" /><span className="bracket br" />
                <img src="/img/bike.png" alt="" width={600} height={411} loading="lazy" />
                <span className="btn btn-primary btn-sm preview-cta">
                  Start the test <Play size={16} weight="fill" />
                </span>
              </div>
              <div className="preview-side">
                <div className="preview-gauge">
                  <Gauge value={0} max={30} label="Inference FPS" size={200} idle />
                </div>
                <ul className="preview-list">
                  <li>Classes <b>helmet, nohelmet</b></li>
                  <li>Engine <b>WebGPU or WASM</b></li>
                  <li>Upload to a server <b>none</b></li>
                </ul>
              </div>
            </div>
          </Link>
        </div>
      </section>

      <section className="section alt" id="how">
        <div className="container">
          <div className="section-head reveal">
            <h2>From footage to findings in four steps.</h2>
          </div>
          <ol className="steps reveal">
            <li className="step">
              <span className="step-icon"><VideoCamera size={28} /></span>
              <div>
                <h3>Bring footage</h3>
                <p>Use your webcam or choose a traffic video from your device.</p>
              </div>
            </li>
            <li className="step">
              <span className="step-icon"><Scan size={28} /></span>
              <div>
                <h3>Detect</h3>
                <p>A YOLO model finds helmets and riders without them, frame by frame.</p>
              </div>
            </li>
            <li className="step">
              <span className="step-icon"><Crosshair size={28} /></span>
              <div>
                <h3>See the overlay</h3>
                <p>Boxes and confidence scores are drawn right on the footage.</p>
              </div>
            </li>
            <li className="step">
              <span className="step-icon"><ListChecks size={28} /></span>
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
            <article className="cell a reveal">
              <MarkNight />
              <HardHat className="cell-icon" size={32} />
              <h3>Helmet detection</h3>
              <p>The trained model recognises two classes: helmet and nohelmet. Each detection carries its own confidence score.</p>
            </article>
            <article className="cell warn reveal">
              <WarningOctagon className="cell-icon" size={30} />
              <h3>No-helmet flags</h3>
              <p>The one violation supported today, shown in coral.</p>
            </article>
            <article className="cell grid-bg reveal">
              <Crosshair className="cell-icon" size={30} />
              <h3>Live overlays</h3>
              <p>Bounding boxes on every processed frame.</p>
            </article>
            <article className="cell wide tint reveal">
              <ChartLineUp className="cell-icon" size={30} />
              <h3>Statistics and event history</h3>
              <p>Counts come from real detections. Riders are tracked across frames so one person is not counted twice.</p>
            </article>
            <article className="cell wide reveal">
              <Cpu className="cell-icon" size={30} />
              <h3>AI in the browser</h3>
              <p>ONNX Runtime Web uses WebGPU when your browser supports it and falls back to WebAssembly when it does not.</p>
            </article>
            <article className="cell wide grid-bg reveal">
              <LockKey className="cell-icon" size={30} />
              <h3>Private by design</h3>
              <p>Frames are processed on your device. There is no upload and no inference server.</p>
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
    </>
  )
}
