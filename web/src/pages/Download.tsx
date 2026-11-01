import { Link } from 'react-router-dom'
import { ArrowRight, DownloadSimple } from '@phosphor-icons/react'
import { BRAND } from '../config/brand'
import { DOWNLOAD } from '../config/download'
import { PageBand } from '../components/PageBand'
import { StatusRows, type RowItem } from '../components/StatusRows'
import { usePageMeta } from '../hooks/usePageMeta'

const INCLUDED: RowItem[] = [
  {
    title: 'Cluster dashboard',
    text: 'A full-screen motorcycle-style dashboard with helmet status, an engine control card, alerts and a live camera view with detection boxes.',
    status: 'built',
  },
  {
    title: 'Voice prompts',
    text: 'Speaks "Please wear helmet" and "Helmet detected. Now you can ride the bike." through the Windows speech engine.',
    status: 'built',
  },
  {
    title: 'Snapshots and event log',
    text: 'Saves a picture for each alert and keeps a local log with analytics pages. Everything stays in your Windows user folder.',
    status: 'built',
  },
  {
    title: 'Engine lock',
    text: 'Smart Lock mode shows the lock and writes "engine lock simulated" to the log. It is not connected to any engine.',
    status: 'simulated',
  },
]

const mib = (n: number) => (n ? `${n.toFixed(0)} MB` : 'a few hundred MB')

export default function Download() {
  usePageMeta(`Desktop app | ${BRAND.name}`, 'Download the RideShield AI Windows desktop app. It runs offline on your own camera.')
  return (
    <>
      <PageBand title="Desktop app">
        The original RideShield as a Windows program. It reads your own camera and needs no internet once it is installed.
      </PageBand>

      <section className="section">
        <div className="container two">
          <div className="prose reveal">
            <h2>Download for Windows</h2>
            <p>
              Version {DOWNLOAD.version}. Windows 10 or 11, 64-bit, and a camera. The download is {mib(DOWNLOAD.sizeMiB)}
              {DOWNLOAD.unpackedGiB ? ` and unpacks to about ${DOWNLOAD.unpackedGiB.toFixed(1)} GB` : ''}.
            </p>
            <div className="dl-actions">
              <a className="btn btn-primary" href={DOWNLOAD.url}>
                <DownloadSimple size={20} /> Download {DOWNLOAD.file}
              </a>
              <a className="btn" href={DOWNLOAD.releasesPage} target="_blank" rel="noreferrer noopener">
                All releases
              </a>
            </div>
            {DOWNLOAD.sha256 && (
              <p className="note-small">
                SHA-256: <code className="hash">{DOWNLOAD.sha256}</code>
              </p>
            )}
          </div>
          <ol className="how-run reveal">
            <li><b>Unzip</b> the file anywhere you like.</li>
            <li><b>Open</b> the RideShield folder and run <b>RideShield.exe</b>. The first start can take a minute while the model loads.</li>
            <li><b>Allow the camera</b> if Windows asks.</li>
            <li><b>Leave the full-screen view</b> with the Esc key.</li>
          </ol>
        </div>
      </section>

      <section className="section alt">
        <div className="container">
          <div className="section-head reveal">
            <h2>What you get.</h2>
          </div>
          <div className="reveal">
            <StatusRows items={INCLUDED} />
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container two">
          <div className="prose reveal">
            <h2>Before you run it</h2>
            <p>
              The program is not code-signed, so Windows SmartScreen may warn that it does not recognise it. If you trust the download, choose More info, then Run anyway. You can check the file first: in PowerShell run
              {' '}<code className="hash">Get-FileHash {DOWNLOAD.file}</code> and compare it with the SHA-256 above.
            </p>
            <p>
              Your database and alert snapshots are saved in <code className="hash">%APPDATA%\RideShieldAI</code>. Nothing is sent anywhere. Delete that folder to remove them.
            </p>
          </div>
          <div className="prose reveal">
            <h2>About the licence</h2>
            <p>
              The desktop app includes Ultralytics YOLO, which is released under the AGPL-3.0 licence. The source for this program is on{' '}
              <a href={BRAND.repoUrl} target="_blank" rel="noreferrer noopener" className="textlink">GitHub</a>.
            </p>
            <p>
              This is a demonstration, not a certified safety device. See <Link to="/project" className="textlink">what has not been measured</Link>.
            </p>
          </div>
        </div>
      </section>

      <section className="section alt">
        <div className="container cta-band reveal">
          <h2>Prefer the browser?</h2>
          <p>The website runs the same kind of detector with no install.</p>
          <Link to="/test-drive" className="btn btn-primary">
            Experience RideShield <ArrowRight size={18} className="arrow" />
          </Link>
        </div>
      </section>
    </>
  )
}
