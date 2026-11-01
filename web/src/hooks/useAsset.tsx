import { useEffect, useState } from 'react'

// True when `url` is a real image file. The SPA fallback answers missing files with HTML, so the content
// type decides, not the status. Lets the page pick up photos the moment they are dropped into public/.
export function useImageAvailable(url: string): boolean {
  const [ok, setOk] = useState(false)
  useEffect(() => {
    let alive = true
    fetch(url, { method: 'HEAD' })
      .then((r) => {
        if (alive) setOk(r.ok && (r.headers.get('content-type') ?? '').startsWith('image'))
      })
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [url])
  return ok
}

// Renders the photo when the file exists, nothing otherwise (so no broken-image icons, ever).
export function Photo({ src, alt = '', className, width, height }: { src: string; alt?: string; className?: string; width?: number; height?: number }) {
  const ok = useImageAvailable(src)
  if (!ok) return null
  return <img src={src} alt={alt} className={className} width={width} height={height} loading="lazy" decoding="async" />
}
