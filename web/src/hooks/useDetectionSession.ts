import { useCallback, useEffect, useRef, useState } from 'react'
import { createEngine, type Engine, type EngineInfo, type LoadProgress } from '../inference/engine'
import { DEFAULT_MODEL, getModel, initialModelId, rememberModelId, type ModelSpec } from '../inference/models'
import { Tracker, type TrackedDetection } from '../inference/tracker'

export type EngineState =
  | { status: 'idle' }
  | { status: 'loading'; progress: LoadProgress }
  | { status: 'ready'; info: EngineInfo }
  | { status: 'error'; message: string }

export type SourceKind = 'camera' | 'file' | 'sample'
export type RunState = 'idle' | 'starting' | 'running' | 'paused'

export interface DetectionEvent {
  id: number
  trackId: number
  label: string
  score: number
  clock: string
}

export interface SessionStats {
  frames: number
  detections: number // box count summed over processed frames
  helmetTracks: number
  noHelmetTracks: number
  live: number // boxes in the latest processed frame
  lastScore: number | null
  fps: number // inference frames per second
  latencyMs: number // rolling mean
}

const EMPTY: SessionStats = {
  frames: 0,
  detections: 0,
  helmetTracks: 0,
  noHelmetTracks: 0,
  live: 0,
  lastScore: null,
  fps: 0,
  latencyMs: 0,
}

// The loaded engine outlives route changes so a model is downloaded and compiled once per page load.
// Only one engine is kept: loading another model releases the previous one (frees GPU memory).
const enginePromises = new Map<string, Promise<Engine>>()
const progressListeners = new Set<(p: LoadProgress) => void>()
let lastProgress: LoadProgress = { phase: 'runtime', loaded: 0, total: 1 }

function loadEngine(spec: ModelSpec): Promise<Engine> {
  for (const [id, pending] of enginePromises) {
    if (id === spec.id) continue
    enginePromises.delete(id)
    pending.then((e) => e.dispose()).catch(() => {})
  }
  let p = enginePromises.get(spec.id)
  if (!p) {
    lastProgress = { phase: 'runtime', loaded: 0, total: 1 }
    p = createEngine(spec, (prog) => {
      lastProgress = prog
      progressListeners.forEach((l) => l(prog))
    }).catch((e) => {
      enginePromises.delete(spec.id)
      throw e
    })
    enginePromises.set(spec.id, p)
  }
  return p
}

// Box colours match the legend in the cockpit (safety green, coral, lavender for unknown classes).
const COLORS = { helmet: '#3ddc97', nohelmet: '#ff5d6c', other: '#b9a7ff' }

// Resolves on the next presented video frame, or after 120 ms if the browser does not report one
// (background tabs, hidden panes), so the loop never stalls. Only one inference is ever in flight.
function nextFrame(v: HTMLVideoElement): Promise<void> {
  return new Promise((resolve) => {
    let done = false
    const finish = () => {
      if (done) return
      done = true
      resolve()
    }
    if ('requestVideoFrameCallback' in v) v.requestVideoFrameCallback(finish)
    else requestAnimationFrame(finish)
    window.setTimeout(finish, 120)
  })
}

function describeCameraError(err: unknown): string {
  const name = err instanceof DOMException ? err.name : ''
  switch (name) {
    case 'NotAllowedError':
    case 'SecurityError':
      return 'Camera permission was denied. Allow camera access for this site in the address bar, then press Camera again.'
    case 'NotFoundError':
    case 'OverconstrainedError':
      return 'No camera was found on this device. Plug one in, or upload a video instead.'
    case 'NotReadableError':
    case 'AbortError':
      return 'The camera is busy or blocked by another application. Close it there and try again.'
    default:
      return `The camera could not be started${err instanceof Error ? `: ${err.message}` : '.'}`
  }
}

function describeMediaError(v: HTMLVideoElement): string {
  const code = v.error?.code
  if (code === 3 || code === 4)
    return 'This browser cannot decode that video. Try an MP4 (H.264) or WebM file.'
  if (code === 2) return 'A network or file-read error interrupted the video.'
  return 'The video could not be loaded. Choose another file.'
}

type PendingStart = { kind: 'camera' } | { kind: 'sample' } | { kind: 'file'; file: File }

// lazy: do not download the model until a source is started (used by the landing-page demo, so a visit to
// the home page costs nothing until the visitor asks for detection).
export function useDetectionSession({ lazy = false }: { lazy?: boolean } = {}) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const [modelId, setModelId] = useState(initialModelId)
  const spec = getModel(modelId)
  const [wanted, setWanted] = useState(!lazy)
  const [engineState, setEngineState] = useState<EngineState>(
    lazy ? { status: 'idle' } : { status: 'loading', progress: lastProgress },
  )
  const [run, setRun] = useState<RunState>('idle')
  const [source, setSource] = useState<SourceKind | null>(null)
  const [sourceLabel, setSourceLabel] = useState('')
  const [notice, setNotice] = useState<{ tone: 'info' | 'error'; text: string } | null>(null)
  const [stats, setStats] = useState<SessionStats>(EMPTY)
  const [events, setEvents] = useState<DetectionEvent[]>([])
  const [threshold, setThreshold] = useState(0.45)
  const [position, setPosition] = useState({ t: 0, d: 0 })
  const [sampleAvailable, setSampleAvailable] = useState(false)

  const engineRef = useRef<Engine | null>(null)
  const trackerRef = useRef(new Tracker(DEFAULT_MODEL.classes.length))
  const loopRef = useRef(0) // incremented to cancel the running loop
  const streamRef = useRef<MediaStream | null>(null)
  const objectUrlRef = useRef<string | null>(null)
  const statsRef = useRef<SessionStats>({ ...EMPTY })
  const classOfTrack = useRef(new Map<number, number>())
  const latencies = useRef<number[]>([])
  const frameTimes = useRef<number[]>([])
  const eventSeq = useRef(0)
  const confirmedSeen = useRef(new Set<number>())
  const thresholdRef = useRef(threshold)
  const lastDets = useRef<TrackedDetection[]>([])

  useEffect(() => {
    thresholdRef.current = threshold
  }, [threshold])

  // Engine loading for the selected model, with progress shared across mounts.
  useEffect(() => {
    if (!wanted) return
    let alive = true
    engineRef.current = null
    const onProgress = (p: LoadProgress) => alive && setEngineState({ status: 'loading', progress: p })
    progressListeners.add(onProgress)
    loadEngine(spec).then(
      (e) => {
        if (!alive) return
        engineRef.current = e
        setEngineState({ status: 'ready', info: e.info })
      },
      (err) => alive && setEngineState({ status: 'error', message: err instanceof Error ? err.message : String(err) }),
    )
    return () => {
      alive = false
      progressListeners.delete(onProgress)
    }
  }, [spec, wanted])

  // Is optional sample footage present? (The SPA fallback returns HTML for missing files, so check the type.)
  useEffect(() => {
    let alive = true
    fetch('/samples/sample.mp4', { method: 'HEAD' })
      .then((r) => alive && setSampleAvailable(r.ok && (r.headers.get('content-type') ?? '').startsWith('video')))
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [])

  const releaseMedia = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    const v = videoRef.current
    if (v) {
      v.pause()
      v.srcObject = null
      v.removeAttribute('src')
      v.load()
    }
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current)
      objectUrlRef.current = null
    }
  }, [])

  const clearOverlay = useCallback(() => {
    const c = canvasRef.current
    c?.getContext('2d')?.clearRect(0, 0, c.width, c.height)
    lastDets.current = []
  }, [])

  const resetStats = useCallback(() => {
    statsRef.current = { ...EMPTY }
    trackerRef.current.reset()
    classOfTrack.current.clear()
    confirmedSeen.current.clear()
    latencies.current = []
    frameTimes.current = []
    setStats(EMPTY)
    setEvents([])
  }, [])

  const stop = useCallback(() => {
    loopRef.current++
    releaseMedia()
    clearOverlay()
    setRun('idle')
    setSource(null)
    setSourceLabel('')
    setPosition({ t: 0, d: 0 })
  }, [releaseMedia, clearOverlay])

  // Always release camera tracks and object URLs when leaving the page.
  useEffect(
    () => () => {
      loopRef.current++
      streamRef.current?.getTracks().forEach((t) => t.stop())
      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current)
    },
    [],
  )

  // Flush stats to React ~4x per second instead of every frame.
  useEffect(() => {
    if (run !== 'running') return
    const id = window.setInterval(() => {
      setStats({ ...statsRef.current })
      const v = videoRef.current
      if (v && Number.isFinite(v.duration)) setPosition({ t: v.currentTime, d: v.duration })
    }, 250)
    return () => window.clearInterval(id)
  }, [run])

  const draw = useCallback((dets: TrackedDetection[], w: number, h: number) => {
    const c = canvasRef.current
    if (!c) return
    if (c.width !== w || c.height !== h) {
      c.width = w
      c.height = h
    }
    const ctx = c.getContext('2d')
    if (!ctx) return
    ctx.clearRect(0, 0, w, h)
    const lw = Math.max(2, Math.round(w / 480))
    const fs = Math.max(12, Math.round(w / 56))
    ctx.font = `600 ${fs}px "Geist Variable", system-ui, sans-serif`
    ctx.textBaseline = 'top'
    for (const d of dets) {
      const color = d.label === 'helmet' ? COLORS.helmet : d.label === 'nohelmet' ? COLORS.nohelmet : COLORS.other
      ctx.lineWidth = lw
      ctx.strokeStyle = color
      ctx.setLineDash(d.confirmed ? [] : [lw * 3, lw * 2])
      ctx.strokeRect(d.x1, d.y1, d.x2 - d.x1, d.y2 - d.y1)
      ctx.setLineDash([])
      const text = `${d.label} ${(d.score * 100).toFixed(0)}%`
      const tw = ctx.measureText(text).width + fs * 0.8
      const ty = d.y1 - fs * 1.5 < 0 ? d.y1 : d.y1 - fs * 1.5
      ctx.fillStyle = color
      ctx.fillRect(d.x1 - lw / 2, ty, tw, fs * 1.5)
      ctx.fillStyle = '#0b0b0f'
      ctx.fillText(text, d.x1 + fs * 0.3, ty + fs * 0.25)
    }
  }, [])

  const startLoop = useCallback(() => {
    const engine = engineRef.current
    const v = videoRef.current
    if (!engine || !v) return
    const myLoop = ++loopRef.current
    const tracker = trackerRef.current
    const clock = (t: number) => {
      const s = Math.floor(t)
      return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`
    }

    let lastTime = -1
    const tick = async () => {
      if (myLoop !== loopRef.current) return
      if (v.readyState >= 2 && !v.paused && !v.ended && v.videoWidth > 0 && v.currentTime !== lastTime) {
        lastTime = v.currentTime
        const t0 = performance.now()
        try {
          const dets = await engine.detect(v, v.videoWidth, v.videoHeight, thresholdRef.current)
          if (myLoop !== loopRef.current) return
          const tracked = tracker.update(dets, performance.now())
          const latency = performance.now() - t0
          latencies.current.push(latency)
          if (latencies.current.length > 30) latencies.current.shift()
          frameTimes.current.push(performance.now())
          if (frameTimes.current.length > 20) frameTimes.current.shift()

          const st = statsRef.current
          st.frames++
          st.detections += tracked.length
          st.live = tracked.length
          if (tracked.length) st.lastScore = Math.max(...tracked.map((d) => d.score))
          st.latencyMs = latencies.current.reduce((a, b) => a + b, 0) / latencies.current.length
          const ft = frameTimes.current
          st.fps = ft.length > 1 ? ((ft.length - 1) * 1000) / (ft[ft.length - 1] - ft[0]) : 0

          // Unique objects: confirmed tracks, classified by accumulated confidence.
          const newEvents: DetectionEvent[] = []
          for (const t of tracker.active) {
            if (t.hits < Tracker.MIN_HITS) continue
            const cls = Tracker.majority(t)
            classOfTrack.current.set(t.id, cls)
            if (!confirmedSeen.current.has(t.id)) {
              confirmedSeen.current.add(t.id)
              newEvents.push({
                id: ++eventSeq.current,
                trackId: t.id,
                label: engine.spec.classes[cls],
                score: t.lastScore,
                clock: clock(v.currentTime),
              })
            }
          }
          let helmet = 0
          let none = 0
          classOfTrack.current.forEach((cls) => (engine.spec.classes[cls] === 'helmet' ? helmet++ : none++))
          st.helmetTracks = helmet
          st.noHelmetTracks = none
          if (newEvents.length) setEvents((prev) => [...newEvents.reverse(), ...prev].slice(0, 40))

          lastDets.current = tracked
          draw(tracked, v.videoWidth, v.videoHeight)
        } catch (err) {
          loopRef.current++
          setNotice({
            tone: 'error',
            text: `Inference failed: ${err instanceof Error ? err.message : String(err)}. Reload the page; if it keeps happening, switch to a smaller input or another browser.`,
          })
          setRun('paused')
          return
        }
      }
      if (myLoop !== loopRef.current) return
      await nextFrame(v)
      void tick()
    }
    void tick()
  }, [draw])

  const attachAndPlay = useCallback(
    async (kind: SourceKind, label: string) => {
      const v = videoRef.current
      if (!v) return
      resetStats()
      clearOverlay()
      setSource(kind)
      setSourceLabel(label)
      try {
        await v.play()
      } catch (err) {
        if (!(err instanceof DOMException && err.name === 'AbortError')) {
          releaseMedia()
          setRun('idle')
          setSource(null)
          const unplayable = err instanceof DOMException && err.name === 'NotSupportedError'
          setNotice({
            tone: 'error',
            text: v.error
              ? describeMediaError(v)
              : unplayable
                ? 'This file could not be read as a video. Try an MP4 (H.264) or WebM file.'
                : 'The browser blocked playback. Press the source button again.',
          })
          return
        }
      }
      setRun('running')
      startLoop()
    },
    [resetStats, clearOverlay, releaseMedia, startLoop],
  )

  const startCamera = useCallback(async () => {
    setNotice(null)
    if (engineState.status !== 'ready') return
    if (!navigator.mediaDevices?.getUserMedia) {
      setNotice({ tone: 'error', text: 'This browser or connection does not allow camera access. Camera needs HTTPS (or localhost).' })
      return
    }
    stop()
    setRun('starting')
    setNotice({ tone: 'info', text: 'Your browser will ask for camera permission. Video stays on this device and is never uploaded.' })
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      })
      streamRef.current = stream
      const v = videoRef.current!
      v.srcObject = stream
      v.loop = false
      setNotice(null)
      await attachAndPlay('camera', 'Webcam')
    } catch (err) {
      setRun('idle')
      setNotice({ tone: 'error', text: describeCameraError(err) })
    }
  }, [engineState.status, stop, attachAndPlay])

  const startFile = useCallback(
    async (file: File) => {
      setNotice(null)
      if (engineState.status !== 'ready') return
      if (!file.type.startsWith('video/') && !/\.(mp4|webm|mov|m4v|ogv)$/i.test(file.name)) {
        setNotice({ tone: 'error', text: `"${file.name}" is not a video file. Choose an MP4, WebM or MOV file.` })
        return
      }
      stop()
      setRun('starting')
      const url = URL.createObjectURL(file)
      objectUrlRef.current = url
      const v = videoRef.current!
      v.srcObject = null
      v.loop = true
      v.src = url
      v.onerror = () => {
        setNotice({ tone: 'error', text: describeMediaError(v) })
        stop()
      }
      await attachAndPlay('file', file.name)
    },
    [engineState.status, stop, attachAndPlay],
  )

  const startSample = useCallback(async () => {
    setNotice(null)
    if (engineState.status !== 'ready') return
    stop()
    setRun('starting')
    const v = videoRef.current!
    v.srcObject = null
    v.loop = true
    v.src = '/samples/sample.mp4'
    v.onerror = () => {
      setNotice({ tone: 'error', text: describeMediaError(v) })
      stop()
    }
    await attachAndPlay('sample', 'Sample footage')
  }, [engineState.status, stop, attachAndPlay])

  const togglePause = useCallback(() => {
    const v = videoRef.current
    if (!v || run === 'idle' || run === 'starting') return
    if (run === 'running') {
      v.pause()
      setRun('paused')
    } else {
      void v.play().then(() => {
        setRun('running')
        startLoop()
      })
    }
  }, [run, startLoop])

  const seek = useCallback((t: number) => {
    const v = videoRef.current
    if (v && Number.isFinite(v.duration)) {
      v.currentTime = t
      setPosition({ t, d: v.duration })
    }
  }, [])

  // Switching models stops the current source (the old model's results would no longer apply),
  // clears the counters and loads the new engine; the effect above does the loading.
  const selectModel = useCallback(
    (id: string) => {
      if (id === modelId) return
      stop()
      resetStats()
      setNotice({ tone: 'info', text: `Switching to ${getModel(id).label}. Counters were reset.` })
      rememberModelId(id)
      setEngineState({ status: 'loading', progress: { phase: 'runtime', loaded: 0, total: 1 } })
      setModelId(id)
    },
    [modelId, stop, resetStats],
  )

  // begin*: start a source, waking the engine first if it was left asleep (lazy mode). The action runs as
  // soon as the model is ready, so one click both loads the model and starts the camera or video.
  const pendingRef = useRef<PendingStart | null>(null)
  const startersRef = useRef({ startCamera, startFile, startSample })
  useEffect(() => {
    startersRef.current = { startCamera, startFile, startSample }
  })
  useEffect(() => {
    if (engineState.status !== 'ready' || !pendingRef.current) return
    const p = pendingRef.current
    pendingRef.current = null
    const s = startersRef.current
    if (p.kind === 'camera') void s.startCamera()
    else if (p.kind === 'sample') void s.startSample()
    else void s.startFile(p.file)
  }, [engineState.status])
  const begin = useCallback(
    (p: PendingStart) => {
      if (engineState.status === 'error') return
      pendingRef.current = p
      if (!wanted) {
        setEngineState({ status: 'loading', progress: { phase: 'runtime', loaded: 0, total: 1 } })
        setWanted(true)
      } else if (engineState.status === 'ready') {
        // Already loaded: the effect above will not fire again, so run it now.
        pendingRef.current = null
        const s = startersRef.current
        if (p.kind === 'camera') void s.startCamera()
        else if (p.kind === 'sample') void s.startSample()
        else void s.startFile(p.file)
      }
    },
    [engineState.status, wanted],
  )
  const beginCamera = useCallback(() => begin({ kind: 'camera' }), [begin])
  const beginSample = useCallback(() => begin({ kind: 'sample' }), [begin])
  const beginFile = useCallback((file: File) => begin({ kind: 'file', file }), [begin])

  return {
    videoRef,
    canvasRef,
    spec,
    selectModel,
    beginCamera,
    beginSample,
    beginFile,
    engineState,
    run,
    source,
    sourceLabel,
    notice,
    dismissNotice: () => setNotice(null),
    stats,
    events,
    threshold,
    setThreshold,
    position,
    sampleAvailable,
    startCamera,
    startFile,
    startSample,
    togglePause,
    stop,
    seek,
  }
}
