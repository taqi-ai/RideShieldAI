// Checks dist/ before deploying.
//  - Fails if a file is 100 MB or more (the Vercel and GitHub per-file limit) or if a file the app needs is missing.
//  - Warns for files over 25 MiB: they work on Vercel but would not upload to Cloudflare Pages Free.
import { existsSync, readdirSync, statSync } from 'node:fs'
import { dirname, join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

const dist = join(dirname(fileURLToPath(import.meta.url)), '..', 'dist')
const HARD_LIMIT = 100 * 1000 * 1000
const CLOUDFLARE_LIMIT = 25 * 1024 * 1024
const required = [
  'index.html',
  'models/helmet_yolo26n.dynamic.onnx',
  'models/helmet_yolov8s.dynamic.onnx',
  'models/helmet_yolo11m.dynamic.onnx',
  'brand/logo-night.png',
  'brand/logo-day.png',
  'brand/favicon-32.png',
  '_headers',
]

const walk = (dir) =>
  readdirSync(dir, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(join(dir, e.name)) : [join(dir, e.name)]))

let failed = false
const files = walk(dist)
for (const f of files) {
  const size = statSync(f).size
  const name = relative(dist, f)
  if (size >= HARD_LIMIT) {
    console.error(`TOO LARGE: ${name} is ${(size / 1048576).toFixed(2)} MiB (limit 100 MB)`)
    failed = true
  } else if (size >= CLOUDFLARE_LIMIT) {
    console.warn(`note: ${name} is ${(size / 1048576).toFixed(1)} MiB, over Cloudflare Pages' 25 MiB file limit (fine on Vercel)`)
  }
}
for (const r of required) {
  if (!existsSync(join(dist, r))) {
    console.error(`MISSING: dist/${r}`)
    failed = true
  }
}
const largest = files.map((f) => [relative(dist, f), statSync(f).size]).sort((a, b) => b[1] - a[1])[0]
console.log(`${files.length} files in dist. Largest: ${largest[0]} (${(largest[1] / 1048576).toFixed(2)} MiB)`)
if (failed) process.exit(1)
console.log('asset check passed: every file is under 100 MB')
