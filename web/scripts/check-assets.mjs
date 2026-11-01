// Fails the build if any file in dist/ is at or over the Cloudflare Pages 25 MiB per-file limit,
// or if a model/entry file the app needs is missing.
import { existsSync, readdirSync, statSync } from 'node:fs'
import { dirname, join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

const dist = join(dirname(fileURLToPath(import.meta.url)), '..', 'dist')
const LIMIT = 25 * 1024 * 1024
const required = ['index.html', 'models/helmet_yolo26n.dynamic.onnx', 'favicon.svg', '_headers']

const walk = (dir) =>
  readdirSync(dir, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(join(dir, e.name)) : [join(dir, e.name)]))

let failed = false
const files = walk(dist)
for (const f of files) {
  const size = statSync(f).size
  if (size >= LIMIT) {
    console.error(`TOO LARGE: ${relative(dist, f)} is ${(size / 1048576).toFixed(2)} MiB (limit 25 MiB)`)
    failed = true
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
console.log('asset check passed: every file is under 25 MiB')
