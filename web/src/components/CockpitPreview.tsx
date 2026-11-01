import { Gauge } from './Gauge'
import { MarkNight } from './Logo'
import { MODELS } from '../inference/models'

// A non-interactive render of the real cockpit UI in its idle state, used as the landing-page product plane.
// It uses the same classes and components as /test-drive and shows no measurements: every value is empty.
export function CockpitPreview() {
  return (
    <div className="cp" aria-hidden inert>
      <div className="cp-bar">
        <span className="chip accent">Test drive</span>
        <span className="chip">Camera</span>
        <span className="chip">Upload video</span>
        <span className="spacer" />
        <span className="chip">Engine <b>WebGPU or WASM</b></span>
        <span className="chip">Classes <b>helmet, nohelmet</b></span>
      </div>
      <div className="cp-body">
        <div className="cp-col">
          <section className="panel">
            <h2>Model</h2>
            <div className="model-list">
              {MODELS.map((m, i) => (
                <div key={m.id} className="model-opt" style={i === 0 ? { borderColor: 'var(--accent)', background: 'var(--accent-soft)' } : undefined}>
                  <span className="m-name">
                    {m.label}
                    <small>{(m.sizeBytes / 1048576).toFixed(1)} MiB</small>
                  </span>
                </div>
              ))}
            </div>
          </section>
          <section className="panel">
            <h2>Instruments</h2>
            <div className="gauge-wrap">
              <Gauge value={0} max={30} label="Inference FPS" size={170} idle />
            </div>
          </section>
        </div>
        <div className="viewport">
          <div className="frame">
            <div className="viewport-empty">
              <MarkNight />
              <h3>Pick a source to begin</h3>
              <p>Use your camera or upload a traffic video. Everything is analysed on this device.</p>
            </div>
          </div>
        </div>
        <div className="cp-col">
          <section className="panel">
            <h2>Detection status</h2>
            <div className="status-line">Waiting for footage</div>
            <div className="cp-counters" style={{ marginTop: '0.6rem' }}>
              <div className="counter"><div className="k">Objects detected</div><div className="v">0</div></div>
              <div className="counter"><div className="k">Frames processed</div><div className="v">0</div></div>
              <div className="counter"><div className="k">Tracked with helmet</div><div className="v ok">0</div></div>
              <div className="counter"><div className="k">No-helmet violations</div><div className="v bad">0</div></div>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
