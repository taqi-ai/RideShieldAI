import { useRef } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowLeft,
  Camera,
  FilmStrip,
  FolderOpen,
  Pause,
  Play,
  ShieldCheck,
  Stop,
  X,
} from '@phosphor-icons/react'
import { Gauge } from '../components/Gauge'
import { Logo } from '../components/Logo'
import { ThemeToggle } from '../components/ThemeToggle'
import { BRAND } from '../config/brand'
import { useDetectionSession } from '../hooks/useDetectionSession'
import { MODELS } from '../inference/models'
import { usePageMeta } from '../hooks/usePageMeta'

const fmtTime = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`
const mb = (bytes: number) => (bytes / 1048576).toFixed(1)

export default function TestDrive() {
  usePageMeta(`Test Drive | ${BRAND.name}`, 'Run the RideShield helmet-detection model on your webcam or a local video, entirely in your browser.')
  const s = useDetectionSession()
  const { videoRef, canvasRef } = s
  const fileRef = useRef<HTMLInputElement>(null)
  const { engineState: eng, stats, run } = s
  const ready = eng.status === 'ready'
  const active = run === 'running' || run === 'paused'
  const idle = run === 'idle'

  const uniqueTotal = stats.helmetTracks + stats.noHelmetTracks
  const compliance = uniqueTotal > 0 ? (stats.helmetTracks / uniqueTotal) * 100 : null
  const alerting = stats.live > 0 && s.stats.noHelmetTracks > 0

  const loadPct =
    eng.status === 'loading'
      ? eng.progress.phase === 'runtime'
        ? 5
        : eng.progress.phase === 'model'
          ? 5 + 85 * (eng.progress.loaded / Math.max(1, eng.progress.total))
          : 95
      : 100
  const loadText =
    eng.status === 'loading'
      ? eng.progress.phase === 'runtime'
        ? 'Preparing runtime'
        : eng.progress.phase === 'model'
          ? `Downloading model ${mb(eng.progress.loaded)} / ${mb(eng.progress.total)} MB`
          : 'Compiling model'
      : ''

  return (
    <div className="cockpit">
      <header className="cockpit-bar">
        <h1 className="sr-only">RideShield AI test drive: helmet detection in your browser</h1>
        <Link to="/" className="back-link" aria-label="Back to the RideShield home page">
          <ArrowLeft size={18} /> Home
        </Link>
        <Logo />
        <span className="spacer" />
        {eng.status === 'loading' && <span className="chip accent" role="status">Loading model</span>}
        {eng.status === 'error' && <span className="chip bad">Model failed</span>}
        {ready && (
          <>
            <span className="chip ok" role="status">System ready</span>
            <span className="chip">Engine <b>{eng.info.backend === 'webgpu' ? 'WebGPU' : `WASM x${eng.info.threads}`}</b></span>
          </>
        )}
        <span className="chip">Model <b>{s.spec.label}</b></span>
        <ThemeToggle />
      </header>

      <main className="cockpit-grid" id="main">
        {/* Left: model, instruments */}
        <div className="col-left">
          <section className="panel" aria-labelledby="mdl">
            <h2 id="mdl">Model</h2>
            <div className="model-list" role="radiogroup" aria-label="Detection model">
              {MODELS.map((m) => (
                <label key={m.id} className="model-opt">
                  <input
                    type="radio"
                    name="model"
                    value={m.id}
                    checked={m.id === s.spec.id}
                    onChange={() => s.selectModel(m.id)}
                  />
                  <span className="m-name">
                    {m.label}
                    <small>{mb(m.sizeBytes)} MiB</small>
                  </span>
                  <span className="m-blurb">{m.blurb}</span>
                </label>
              ))}
            </div>
            <p className="note-small">
              Switching downloads the model once and stops the current source. Larger models can be more accurate but run slower.
            </p>
          </section>

          <section className="panel" aria-labelledby="inst">
            <h2 id="inst">Instruments</h2>
            <div className="gauge-wrap">
              <Gauge value={stats.fps} max={30} label="Inference FPS" decimals={1} size={250} idle={stats.frames === 0} />
            </div>
            <div className="gauge-row" style={{ marginTop: 8 }}>
              <Gauge value={stats.latencyMs} max={500} label="Latency" unit="ms" size={130} idle={stats.frames === 0} />
              <Gauge
                value={(stats.lastScore ?? 0) * 100}
                max={100}
                label="Top conf."
                unit="%"
                size={130}
                idle={stats.lastScore === null}
                tone="ok"
              />
            </div>
            <p className="note-small">The dial shows model throughput, not vehicle speed. Values are measured on this device.</p>
          </section>

          <section className="panel" aria-labelledby="eng">
            <h2 id="eng">Inference engine</h2>
            <div className="kv">
              <div>Model <b>{s.spec.label}</b></div>
              <div>Classes <b>{s.spec.classes.join(', ')}</b></div>
              <div>Input <b>{s.spec.dynamic ? `up to ${s.spec.inputSize}, step 32` : `${s.spec.inputSize} x ${s.spec.inputSize}`}</b></div>
              <div>File size <b>{mb(s.spec.sizeBytes)} MiB</b></div>
              <div>Backend <b>{ready ? (eng.info.backend === 'webgpu' ? 'WebGPU' : 'WebAssembly') : '...'}</b></div>
            </div>
            {ready && eng.info.backend === 'wasm' && (
              <p className="note-small">{eng.info.webgpuNote}</p>
            )}
          </section>
        </div>

        {/* Center: viewport and controls */}
        <div className="stage">
          <div className={`viewport${idle ? ' idle' : ''}`}>
            <div className="frame">
              <video ref={videoRef} muted playsInline aria-label="Video being analysed" />
              <canvas ref={canvasRef} aria-hidden="true" />
              {idle && (
                <div className="viewport-empty">
                  <h3>{eng.status === 'error' ? 'The model could not start' : 'Pick a source to begin'}</h3>
                  <p>
                    {eng.status === 'error'
                      ? eng.message
                      : 'Use your camera or upload a traffic video. Everything is analysed on this device.'}
                  </p>
                  {eng.status === 'error' && (
                    <button className="btn btn-sm" onClick={() => window.location.reload()}>Reload and retry</button>
                  )}
                </div>
              )}
              {active && (
                <div className="hud">
                  <span className="chip"><b>{s.sourceLabel}</b></span>
                  <span className={`chip ${run === 'paused' ? '' : 'ok'}`}>{run === 'paused' ? 'Paused' : 'Analysing'}</span>
                  <span className="chip">In frame <b>{stats.live}</b></span>
                </div>
              )}
              {run === 'starting' && (
                <div className="viewport-empty" role="status" style={{ position: 'absolute' }}>
                  <p>Starting the source...</p>
                </div>
              )}
            </div>
          </div>

          {eng.status === 'loading' && (
            <div role="status" aria-live="polite">
              <div className="load-bar" aria-hidden="true"><i style={{ width: `${loadPct}%` }} /></div>
              <p style={{ color: 'var(--muted)', fontSize: 13, marginTop: 6, fontFamily: 'var(--mono)' }}>{loadText}</p>
            </div>
          )}

          {s.notice && (
            <div className={`notice ${s.notice.tone === 'error' ? 'error' : ''}`} role={s.notice.tone === 'error' ? 'alert' : 'status'}>
              <span>{s.notice.text}</span>
              <button onClick={s.dismissNotice} aria-label="Dismiss message"><X size={16} /></button>
            </div>
          )}

          <div className="controls">
            <button className="btn btn-primary" disabled={!ready || run === 'starting'} onClick={() => void s.startCamera()}>
              <Camera size={18} /> Camera
            </button>
            <button className="btn" disabled={!ready || run === 'starting'} onClick={() => fileRef.current?.click()}>
              <FolderOpen size={18} /> Upload video
            </button>
            <button
              className="btn"
              disabled={!ready || !s.sampleAvailable || run === 'starting'}
              onClick={() => void s.startSample()}
              title={s.sampleAvailable ? undefined : 'No sample footage has been added to this build yet.'}
            >
              <FilmStrip size={18} /> Sample
            </button>
            <input
              ref={fileRef}
              type="file"
              accept="video/*"
              hidden
              onChange={(e) => {
                const f = e.target.files?.[0]
                e.target.value = ''
                if (f) void s.startFile(f)
              }}
            />
            <span className="spacer" />
            <button className="btn" disabled={!active} onClick={s.togglePause}>
              {run === 'paused' ? <Play size={18} weight="fill" /> : <Pause size={18} weight="fill" />}
              {run === 'paused' ? 'Resume' : 'Pause'}
            </button>
            <button className="btn btn-danger" disabled={idle} onClick={s.stop}>
              <Stop size={18} weight="fill" /> Stop
            </button>
          </div>

          {(s.source === 'file' || s.source === 'sample') && active && s.position.d > 0 && (
            <div className="seek">
              <span>{fmtTime(s.position.t)}</span>
              <input
                type="range"
                min={0}
                max={s.position.d}
                step={0.1}
                value={s.position.t}
                onChange={(e) => s.seek(Number(e.target.value))}
                aria-label="Seek video"
              />
              <span>{fmtTime(s.position.d)}</span>
            </div>
          )}

          <div className="legend">
            <span><i style={{ background: 'var(--ok)' }} />helmet</span>
            <span><i style={{ background: 'var(--bad)' }} />nohelmet (violation)</span>
            <span>Dashed box: still being confirmed</span>
          </div>
          <p className="privacy">
            <ShieldCheck size={18} />
            <span>Camera and video never leave this device. Inference runs locally in your browser; nothing is uploaded. Stopping releases the camera.</span>
          </p>
        </div>

        {/* Right: telemetry */}
        <div className="col-right">
          <section className="panel" aria-labelledby="status">
            <h2 id="status">Detection status</h2>
            <div
              className={`status-line ${stats.frames === 0 ? '' : alerting ? 'bad' : 'ok'}`}
              role="status"
              aria-live="polite"
            >
              <span className="state">
                {stats.frames === 0
                  ? 'Waiting for footage'
                  : alerting
                    ? 'No-helmet rider detected'
                    : stats.live > 0
                      ? 'Helmets in view'
                      : 'Nothing detected in view'}
              </span>
            </div>
            <div className="counters" style={{ marginTop: 10 }}>
              <div className="counter">
                <div className="k">Objects detected</div>
                <div className="v">{stats.detections}</div>
                <small>Boxes summed over all processed frames</small>
              </div>
              <div className="counter">
                <div className="k">Frames processed</div>
                <div className="v">{stats.frames}</div>
                <small>Some video frames are skipped</small>
              </div>
              <div className="counter">
                <div className="k">Tracked with helmet</div>
                <div className="v ok">{stats.helmetTracks}</div>
                <small>Unique, confirmed</small>
              </div>
              <div className="counter">
                <div className="k">No-helmet violations</div>
                <div className="v bad">{stats.noHelmetTracks}</div>
                <small>Unique, confirmed</small>
              </div>
            </div>
            <div className="kv" style={{ marginTop: 12 }}>
              <div>
                Helmet share of tracked riders
                <b>{compliance === null ? '--' : `${compliance.toFixed(0)}% (${uniqueTotal})`}</b>
              </div>
            </div>
          </section>

          <section className="panel" aria-labelledby="ev">
            <h2 id="ev">Recent events</h2>
            {s.events.length === 0 ? (
              <p className="empty">
                {active ? 'No object has been confirmed yet.' : 'Events appear here once an object is confirmed across several frames.'}
              </p>
            ) : (
              <ul className="events" aria-live="polite">
                {s.events.map((e) => (
                  <li key={e.id}>
                    <span className="t">{e.clock}</span>
                    <span className={`l ${e.label}`}>{e.label === 'nohelmet' ? 'No helmet' : 'Helmet'} #{e.trackId}</span>
                    <span className="s">{(e.score * 100).toFixed(0)}%</span>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="panel" aria-labelledby="set">
            <h2 id="set">Settings</h2>
            <div className="field">
              <label htmlFor="thr">
                Confidence threshold <b>{Math.round(s.threshold * 100)}%</b>
              </label>
              <input id="thr" type="range" min={0.2} max={0.9} step={0.05} value={s.threshold} onChange={(e) => s.setThreshold(Number(e.target.value))} />
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}
