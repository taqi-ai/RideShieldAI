import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, ArrowsOut, Play, SpeakerHigh, SpeakerSlash, Pause, FilmSlate } from '@phosphor-icons/react'
import { BRAND } from '../config/brand'
import { Photo } from '../hooks/useAsset'
import { usePageMeta } from '../hooks/usePageMeta'

type Availability = 'checking' | 'available' | 'missing'

function useTrailerAvailability(): Availability {
  const [state, setState] = useState<Availability>('checking')
  useEffect(() => {
    let alive = true
    // The SPA fallback answers missing files with HTML, so the content type decides.
    fetch(BRAND.trailer.src, { method: 'HEAD' })
      .then((r) => alive && setState(r.ok && (r.headers.get('content-type') ?? '').startsWith('video') ? 'available' : 'missing'))
      .catch(() => alive && setState('missing'))
    return () => {
      alive = false
    }
  }, [])
  return state
}

function useAsset(url: string, kind: 'text' | 'image') {
  const [ok, setOk] = useState(false)
  useEffect(() => {
    let alive = true
    fetch(url, { method: 'HEAD' })
      .then((r) => {
        const type = r.headers.get('content-type') ?? ''
        if (alive) setOk(r.ok && (kind === 'image' ? type.startsWith('image') : type.includes('vtt') || type.startsWith('text/plain')))
      })
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [url, kind])
  return ok
}

export default function Trailer() {
  usePageMeta(`Trailer | ${BRAND.name}`, `Watch the ${BRAND.name} trailer. The 30-second film is in production.`)
  const availability = useTrailerAvailability()
  const hasCaptions = useAsset(BRAND.trailer.captions, 'text')
  const hasPoster = useAsset(BRAND.trailer.poster, 'image')
  const frameRef = useRef<HTMLDivElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const [playing, setPlaying] = useState(false)
  const [muted, setMuted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fsSupported] = useState(() => typeof document !== 'undefined' && !!document.fullscreenEnabled)
  const live = availability === 'available' && !error

  const toggle = () => {
    const v = videoRef.current
    if (!v) return
    if (v.paused) void v.play().catch(() => setError('Playback was blocked. Press play again.'))
    else v.pause()
  }
  const fullscreen = async () => {
    const el = frameRef.current
    if (!el) return
    try {
      if (document.fullscreenElement) await document.exitFullscreen()
      else await el.requestFullscreen()
    } catch {
      setError('Fullscreen is not available in this browser.')
    }
  }

  return (
    <div className="container">
      <div className="page-title">
        <h1>See RideShield in action.</h1>
        <p>
          {live
            ? 'The 30-second trailer.'
            : 'The 30-second film is still in production. This page is ready for it.'}
        </p>
      </div>

      <div className="trailer-frame" ref={frameRef}>
        {live && (
          <video
            ref={videoRef}
            src={BRAND.trailer.src}
            poster={hasPoster ? BRAND.trailer.poster : undefined}
            controls
            playsInline
            preload="metadata"
            onPlay={() => setPlaying(true)}
            onPause={() => setPlaying(false)}
            onWaiting={() => setLoading(true)}
            onCanPlay={() => setLoading(false)}
            onPlaying={() => setLoading(false)}
            onLoadedData={() => setLoading(false)}
            onError={() => setError('The trailer file could not be played in this browser.')}
            onVolumeChange={(e) => setMuted(e.currentTarget.muted)}
          >
            {hasCaptions && <track kind="captions" src={BRAND.trailer.captions} srcLang="en" label="English" default />}
          </video>
        )}
        {live && loading && (
          <div className="poster" style={{ background: 'rgba(0,0,0,0.5)', pointerEvents: 'none' }} role="status">
            <span className="chip">Loading video</span>
          </div>
        )}
        {!live && (
          <div className="poster">
            <Photo src="/media/rideshield-trailer-poster.jpg" className="poster-photo" />
            <div className="poster-inner">
              {availability === 'checking' ? (
                <span className="chip" role="status">Checking for the trailer</span>
              ) : (
                <>
                  <h3>Trailer Coming Soon</h3>
                  <p>{error ?? 'The 30-second film is in production. When it is added, it plays right here.'}</p>
                </>
              )}
              <span className="play-ring" aria-hidden="true">
                <Play size={32} weight="fill" />
              </span>
            </div>
          </div>
        )}
      </div>

      <div className="player-bar">
        <Link to="/" className="btn btn-sm">
          <ArrowLeft size={16} /> Back to home
        </Link>
        <button className="btn btn-sm" onClick={toggle} disabled={!live} aria-label={playing ? 'Pause trailer' : 'Play trailer'}>
          {playing ? <Pause size={16} weight="fill" /> : <Play size={16} weight="fill" />} {playing ? 'Pause' : 'Play'}
        </button>
        <button
          className="btn btn-sm"
          disabled={!live}
          onClick={() => {
            const v = videoRef.current
            if (v) v.muted = !v.muted
          }}
          aria-label={muted ? 'Unmute' : 'Mute'}
        >
          {muted ? <SpeakerSlash size={16} /> : <SpeakerHigh size={16} />} {muted ? 'Unmute' : 'Mute'}
        </button>
        <span className="spacer" />
        <button className="btn btn-sm" onClick={fullscreen} disabled={!fsSupported || !live} aria-label="Toggle fullscreen">
          <ArrowsOut size={16} /> Fullscreen
        </button>
        <Link to="/test-drive" className="btn btn-primary btn-sm">
          <FilmSlate size={16} /> Try the test drive
        </Link>
      </div>
      <div style={{ height: 96 }} />
    </div>
  )
}
