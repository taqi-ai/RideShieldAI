import type { InferenceSession, Tensor } from 'onnxruntime-web'
import type { ModelSpec } from './models'

export type Backend = 'webgpu' | 'wasm'

export interface Detection {
  cls: number
  label: string
  score: number
  // Pixels in the coordinate space of the source frame.
  x1: number
  y1: number
  x2: number
  y2: number
}

export interface EngineInfo {
  backend: Backend
  threads: number
  webgpuAvailable: boolean
  webgpuNote: string
}

export interface Engine {
  spec: ModelSpec
  info: EngineInfo
  detect(source: CanvasImageSource, width: number, height: number, minScore: number): Promise<Detection[]>
  dispose(): Promise<void>
}

type OrtModule = typeof import('onnxruntime-web')

interface Support {
  webgpu: boolean
  jspi: boolean
  note: string
}

async function probeSupport(): Promise<Support> {
  const hasJspi = typeof (WebAssembly as unknown as { Suspending?: unknown }).Suspending === 'function'
  const gpu = (navigator as unknown as { gpu?: { requestAdapter(): Promise<unknown> } }).gpu
  // Troubleshooting switch: open /test-drive?backend=wasm to skip WebGPU on purpose.
  if (new URLSearchParams(location.search).get('backend') === 'wasm')
    return { webgpu: false, jspi: hasJspi, note: 'WebAssembly was selected with ?backend=wasm.' }
  if (!gpu) return { webgpu: false, jspi: hasJspi, note: 'This browser does not expose WebGPU.' }
  try {
    const adapter = await gpu.requestAdapter()
    if (!adapter) return { webgpu: false, jspi: hasJspi, note: 'WebGPU is present but no GPU adapter was granted.' }
  } catch {
    return { webgpu: false, jspi: hasJspi, note: 'WebGPU adapter request failed.' }
  }
  if (!hasJspi) {
    return {
      webgpu: false,
      jspi: false,
      note: 'WebGPU exists, but this browser lacks WebAssembly JSPI, which the free-hosting build of ONNX Runtime needs.',
    }
  }
  return { webgpu: true, jspi: true, note: 'WebGPU and JSPI are available.' }
}

export interface LoadProgress {
  phase: 'runtime' | 'model' | 'session'
  loaded: number
  total: number
}

async function fetchModel(url: string, expected: number, onProgress: (p: LoadProgress) => void): Promise<Uint8Array> {
  const res = await fetch(url, { cache: 'force-cache' })
  if (!res.ok) throw new Error(`Model file could not be downloaded (${res.status} ${res.statusText}) from ${url}.`)
  const total = Number(res.headers.get('content-length')) || expected
  if (!res.body) {
    const buf = new Uint8Array(await res.arrayBuffer())
    onProgress({ phase: 'model', loaded: buf.length, total: buf.length })
    return buf
  }
  const reader = res.body.getReader()
  const chunks: Uint8Array[] = []
  let loaded = 0
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    chunks.push(value)
    loaded += value.length
    onProgress({ phase: 'model', loaded, total: Math.max(total, loaded) })
  }
  const out = new Uint8Array(loaded)
  let off = 0
  for (const c of chunks) {
    out.set(c, off)
    off += c.length
  }
  return out
}

export async function createEngine(spec: ModelSpec, onProgress: (p: LoadProgress) => void): Promise<Engine> {
  onProgress({ phase: 'runtime', loaded: 0, total: 1 })
  const support = await probeSupport()

  // The WebGPU wasm shipped in the default ORT bundle is >25 MiB, over the Cloudflare Pages
  // per-file limit. The JSPI build (17 MiB) and the plain CPU build (14 MiB) both fit.
  const ort: OrtModule = support.webgpu
    ? ((await import('onnxruntime-web/jspi')) as unknown as OrtModule)
    : await import('onnxruntime-web/wasm')
  const threads = self.crossOriginIsolated ? Math.max(1, Math.min(4, navigator.hardwareConcurrency || 2)) : 1
  ort.env.wasm.numThreads = threads
  onProgress({ phase: 'runtime', loaded: 1, total: 1 })

  const bytes = await fetchModel(spec.url, spec.sizeBytes, onProgress)
  onProgress({ phase: 'session', loaded: 0, total: 1 })

  let session: InferenceSession
  let backend: Backend = support.webgpu ? 'webgpu' : 'wasm'
  let note = support.note
  try {
    session = await ort.InferenceSession.create(bytes, {
      executionProviders: [backend],
      graphOptimizationLevel: 'all',
    })
  } catch (err) {
    if (backend === 'webgpu') {
      // Do not hide this: the UI shows why the GPU path was not used.
      note = `WebGPU session failed (${err instanceof Error ? err.message : String(err)}); using WebAssembly.`
      backend = 'wasm'
      const wasmOrt = await import('onnxruntime-web/wasm')
      wasmOrt.env.wasm.numThreads = threads
      session = await wasmOrt.InferenceSession.create(bytes, { executionProviders: ['wasm'] })
      return finish(wasmOrt, session)
    }
    throw err
  }
  return finish(ort, session)

  function finish(rt: OrtModule, s: InferenceSession): Engine {
    onProgress({ phase: 'session', loaded: 1, total: 1 })
    const size = spec.inputSize
    const canvas = typeof OffscreenCanvas !== 'undefined' ? new OffscreenCanvas(size, size) : document.createElement('canvas')
    const ctx = canvas.getContext('2d', { willReadFrequently: true }) as
      | CanvasRenderingContext2D
      | OffscreenCanvasRenderingContext2D
      | null
    if (!ctx) throw new Error('Could not create a 2D canvas for preprocessing.')
    let input = new Float32Array(0)
    const inputName = s.inputNames[0]
    const outputName = s.outputNames[0]

    return {
      spec,
      info: { backend, threads, webgpuAvailable: support.webgpu, webgpuNote: note },
      async detect(source, width, height, minScore) {
        // Letterbox like Ultralytics: scale to fit `size`, then pad with grey 114. A dynamic-shape
        // model only needs padding up to the next multiple of 32 (the "rect" mode the desktop app
        // used), which keeps confidences identical to the PyTorch weights. A fixed-shape model is
        // padded to a full square.
        const scale = Math.min(size / width, size / height)
        const nw = Math.round(width * scale)
        const nh = Math.round(height * scale)
        const dw = spec.dynamic ? (size - nw) % 32 : size - nw
        const dh = spec.dynamic ? (size - nh) % 32 : size - nh
        const W = nw + dw
        const H = nh + dh
        const padX = Math.round(dw / 2 - 0.1)
        const padY = Math.round(dh / 2 - 0.1)
        if (canvas.width !== W || canvas.height !== H) {
          canvas.width = W
          canvas.height = H
          input = new Float32Array(3 * W * H)
        }
        ctx.fillStyle = 'rgb(114,114,114)'
        ctx.fillRect(0, 0, W, H)
        ctx.drawImage(source, padX, padY, nw, nh)
        const rgba = ctx.getImageData(0, 0, W, H).data
        const plane = W * H
        // RGBA bytes -> planar CHW float32 RGB in 0..1.
        for (let i = 0, p = 0; i < plane; i++, p += 4) {
          input[i] = rgba[p] / 255
          input[plane + i] = rgba[p + 1] / 255
          input[2 * plane + i] = rgba[p + 2] / 255
        }
        const tensor = new rt.Tensor('float32', input, [1, 3, H, W])
        const out = await s.run({ [inputName]: tensor })
        const result = out[outputName] as Tensor
        const data = result.data as Float32Array
        const dims = result.dims
        const raw =
          spec.output === 'end2end'
            ? decodeEnd2End(data, dims, spec.classes.length, minScore)
            : decodeRaw(data, dims, spec.classes.length, minScore)
        return raw.map((r) => {
          const x1 = clamp((r.x1 - padX) / scale, 0, width)
          const y1 = clamp((r.y1 - padY) / scale, 0, height)
          const x2 = clamp((r.x2 - padX) / scale, 0, width)
          const y2 = clamp((r.y2 - padY) / scale, 0, height)
          return { cls: r.cls, label: spec.classes[r.cls] ?? `class ${r.cls}`, score: r.score, x1, y1, x2, y2 }
        })
      },
      async dispose() {
        await s.release()
      },
    }
  }
}

interface RawBox {
  x1: number
  y1: number
  x2: number
  y2: number
  score: number
  cls: number
}

const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v))

// Output [1, N, 6]: x1, y1, x2, y2, score, class (letterboxed pixels). NMS already applied in-graph.
function decodeEnd2End(data: Float32Array, dims: readonly number[], nc: number, minScore: number): RawBox[] {
  const n = dims[1]
  const stride = dims[2]
  if (stride !== 6) throw new Error(`Unexpected end-to-end output shape [${dims.join(', ')}]; expected [1, N, 6].`)
  const out: RawBox[] = []
  for (let i = 0; i < n; i++) {
    const o = i * stride
    const score = data[o + 4]
    if (score < minScore) continue
    const cls = Math.round(data[o + 5])
    if (cls < 0 || cls >= nc) continue
    out.push({ x1: data[o], y1: data[o + 1], x2: data[o + 2], y2: data[o + 3], score, cls })
  }
  return out
}

// Output [1, 4+nc, A]: cx, cy, w, h then nc class scores per anchor. Needs per-class NMS.
function decodeRaw(data: Float32Array, dims: readonly number[], nc: number, minScore: number): RawBox[] {
  const rows = dims[1]
  const anchors = dims[2]
  if (rows !== 4 + nc) throw new Error(`Unexpected raw output shape [${dims.join(', ')}]; expected [1, ${4 + nc}, A].`)
  const cands: RawBox[] = []
  for (let a = 0; a < anchors; a++) {
    let best = -1
    let bestScore = minScore
    for (let c = 0; c < nc; c++) {
      const s = data[(4 + c) * anchors + a]
      if (s >= bestScore) {
        bestScore = s
        best = c
      }
    }
    if (best < 0) continue
    const cx = data[a]
    const cy = data[anchors + a]
    const w = data[2 * anchors + a]
    const h = data[3 * anchors + a]
    cands.push({ x1: cx - w / 2, y1: cy - h / 2, x2: cx + w / 2, y2: cy + h / 2, score: bestScore, cls: best })
  }
  cands.sort((p, q) => q.score - p.score)
  const kept: RawBox[] = []
  for (const c of cands) {
    if (kept.every((k) => k.cls !== c.cls || iou(k, c) < 0.45)) kept.push(c)
    if (kept.length >= 100) break
  }
  return kept
}

export function iou(a: { x1: number; y1: number; x2: number; y2: number }, b: { x1: number; y1: number; x2: number; y2: number }) {
  const ix = Math.max(0, Math.min(a.x2, b.x2) - Math.max(a.x1, b.x1))
  const iy = Math.max(0, Math.min(a.y2, b.y2) - Math.max(a.y1, b.y1))
  const inter = ix * iy
  const ua = (a.x2 - a.x1) * (a.y2 - a.y1) + (b.x2 - b.x1) * (b.y2 - b.y1) - inter
  return ua > 0 ? inter / ua : 0
}
