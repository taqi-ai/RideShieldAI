import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Camera, FilmStrip, FolderOpen, Stop, X } from '@phosphor-icons/react'
import { useDetectionSession } from '../hooks/useDetectionSession'
import { Photo } from '../hooks/useAsset'

const mb = (bytes: number) => (bytes / 1048576).toFixed(1)

// The landing-page hero IS the detector: a live demo framed like a road sign. It stays asleep (no model
// download) until the visitor starts a source, then loads the model and starts in one step.
export function HeroDemo() {
  const s = useDetectionSession({ lazy: true })
  const { videoRef, canvasRef, engineState: eng, stats, run } = s
  const fileRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)
  const active = run === 'running' || run === 'paused'
  const idle = run === 'idle'
  const waking = eng.status === 'loading'

  const loadText =
    eng.status !== 'loading'
      ? ''
      : eng.progress.phase === 'runtime'
        ? 'Preparing the engine'
        : eng.progress.phase === 'model'
          ? `Downloading ${s.spec.label}, ${mb(eng.progress.loaded)} of ${mb(eng.progress.total)} MiB`
          : 'Compiling the model'
  const loadPct =
    eng.status === 'loading'
      ? eng.progress.phase === 'runtime'
        ? 5
        : eng.progress.phase === 'model'
          ? 5 + 85 * (eng.progress.loaded / Math.max(1, eng.progress.total))
          : 95
      : 0

  return (
    <div className="sign">
      <div
        className={`viewport${idle ? ' idle' : ''}${dragging ? ' drag' : ''}`}
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          const f = e.dataTransfer.files?.[0]
          if (f) s.beginFile(f)
        }}
      >
        <div className="frame">
          <video ref={videoRef} muted playsInline aria-label="Video being analysed" />
          <canvas ref={canvasRef} aria-hidden="true" />
          {idle && <Photo src="/img/hero-rider.jpg" className="idle-photo" />}
          {idle && (
            <div className="viewport-empty">
              <h3>{dragging ? 'Drop it here' : 'Drop in a traffic clip'}</h3>
              <p>or use your camera. Nothing is uploaded; the model runs on this device.</p>
            </div>
          )}
          {active && (
            <div className="hud">
              <span className="chip"><b>{s.sourceLabel}</b></span>
              <span className={`chip ${run === 'paused' ? '' : 'ok'}`}>{run === 'paused' ? 'Paused' : 'Analysing'}</span>
              <span className="chip">{s.spec.label}</span>
            </div>
          )}
        </div>
      </div>

      {waking && (
        <div role="status" aria-live="polite" className="sign-load">
          <div className="load-bar" aria-hidden="true"><i style={{ width: `${loadPct}%` }} /></div>
          <p>{loadText}</p>
        </div>
      )}
      {eng.status === 'error' && (
        <div className="notice error" role="alert">
          <span>{eng.message}</span>
        </div>
      )}
      {s.notice && eng.status !== 'error' && (
        <div className={`notice ${s.notice.tone === 'error' ? 'error' : ''}`} role={s.notice.tone === 'error' ? 'alert' : 'status'}>
          <span>{s.notice.text}</span>
          <button onClick={s.dismissNotice} aria-label="Dismiss message"><X size={16} /></button>
        </div>
      )}

      <div className="sign-row">
        <div className="controls">
          <button className="btn btn-primary btn-sm" disabled={run === 'starting'} onClick={s.beginCamera}>
            <Camera size={18} /> Camera
          </button>
          <button className="btn btn-sm" disabled={run === 'starting'} onClick={() => fileRef.current?.click()}>
            <FolderOpen size={18} /> Upload video
          </button>
          {s.sampleAvailable && (
            <button className="btn btn-sm" disabled={run === 'starting'} onClick={s.beginSample}>
              <FilmStrip size={18} /> Sample
            </button>
          )}
          {!idle && (
            <button className="btn btn-sm btn-danger" onClick={s.stop}>
              <Stop size={16} weight="fill" /> Stop
            </button>
          )}
          <input
            ref={fileRef}
            type="file"
            accept="video/*"
            hidden
            onChange={(e) => {
              const f = e.target.files?.[0]
              e.target.value = ''
              if (f) s.beginFile(f)
            }}
          />
        </div>
        <div className="plates" aria-label="Tracked riders this session">
          <span className="plate ok"><b>{stats.helmetTracks}</b> helmet</span>
          <span className="plate bad"><b>{stats.noHelmetTracks}</b> no helmet</span>
        </div>
      </div>
      <Link to="/test-drive" className="sign-link">
        Open the full test drive <ArrowRight size={16} className="arrow" />
      </Link>
    </div>
  )
}
