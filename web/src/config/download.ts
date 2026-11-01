// The Windows desktop app is too large for the website host (100 MB per file), so it is published as a
// GitHub Release asset. Update these values whenever a new build is uploaded (packaging/build_windows.ps1
// prints them).
interface DownloadInfo {
  version: string
  file: string
  url: string
  releasesPage: string
  sizeMiB: number
  unpackedGiB: number
  sha256: string
}

export const DOWNLOAD: DownloadInfo = {
  version: '0.1.0',
  file: 'RideShield-Windows.zip',
  // Always points at the newest release's asset with this exact name.
  url: 'https://github.com/taqi-ai/RideShieldAI/releases/latest/download/RideShield-Windows.zip',
  releasesPage: 'https://github.com/taqi-ai/RideShieldAI/releases',
  sizeMiB: 288,
  unpackedGiB: 0.71,
  sha256: '2045071742b17992ab457f2b49f7912d58d118c5c966274bf4041b01eaaacf98',
}
