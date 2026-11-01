import { Link } from 'react-router-dom'
import { ArrowRight } from '@phosphor-icons/react'
import { BRAND } from '../config/brand'
import { PageBand } from '../components/PageBand'
import { StatusRows, type RowItem } from '../components/StatusRows'
import { usePageMeta } from '../hooks/usePageMeta'

const STATE: RowItem[] = [
  { title: 'Helmet detection', text: 'Working in the browser and in the desktop app, on a laptop camera or a video.', status: 'built' },
  { title: 'Cluster-style dashboard and voice prompts', text: 'Built in the desktop app: helmet status, engine control card, spoken warnings.', status: 'built' },
  { title: 'Engine lock', text: 'Shown on the dashboard and written to the event log. Nothing is connected to an engine.', status: 'simulated' },
  { title: 'In-bike hardware unit', text: 'A camera and a small computer mounted on the dashboard. Not built.', status: 'planned' },
  { title: 'Real ignition interlock', text: 'Holding the start until the helmet is confirmed. Needs a safety design first. Not built.', status: 'planned' },
  { title: 'Pillion detection', text: 'Checking the second rider as well. Needs a new class and training footage. Not built.', status: 'planned' },
]

export default function OnBike() {
  usePageMeta(`Built for the bike | ${BRAND.name}`, 'RideShield was designed as a helmet detector that rides on the motorcycle. What the idea is and where it stands.')
  return (
    <>
      <PageBand title="Built for the bike">
        RideShield was designed as a detector that rides on the motorcycle, not a camera that watches it from the roadside.
      </PageBand>

      <section className="section">
        <div className="container">
          <figure className="figure reveal">
            <img src="/img/on-bike-concept.jpg" alt="Concept render of a motorcycle dashboard screen showing two riders with green detection boxes and a Helmet Compliant message" width={1774} height={887} loading="lazy" />
            <figcaption>
              Concept render of the on-bike idea. The scores, the clock and the frame rate on the screen are illustrative. This hardware has not been built.
            </figcaption>
          </figure>
        </div>
      </section>

      <section className="section alt">
        <div className="container">
          <div className="section-head reveal">
            <h2>How it is meant to work.</h2>
          </div>
          <ol className="steps reveal">
            <li className="step">
              <span className="step-n">1</span>
              <h3>Look</h3>
              <p>A camera on the dashboard faces the rider.</p>
            </li>
            <li className="step">
              <span className="step-n">2</span>
              <h3>Check</h3>
              <p>The model decides helmet or no helmet, on the bike, with no network.</p>
            </li>
            <li className="step">
              <span className="step-n">3</span>
              <h3>Tell</h3>
              <p>The dashboard shows the state and speaks: "Please wear helmet", or "Helmet detected. Now you can ride the bike."</p>
            </li>
            <li className="step">
              <span className="step-n">4</span>
              <h3>Decide</h3>
              <p>The ignition starts only when the helmet is on. This last step is the part that is still to be built.</p>
            </li>
          </ol>
        </div>
      </section>

      <section className="section">
        <div className="container two">
          <div className="prose reveal">
            <h2>Why on the bike is different.</h2>
            <p>
              A roadside camera sees a rider after the ride has begun, and only where the camera happens to be. A detector on the bike checks every ride, before it starts, wherever the bike is.
            </p>
          </div>
          <ul className="points reveal">
            <li>
              <h3>It acts early</h3>
              <p>The check happens at the moment of the decision, not in a report later.</p>
            </li>
            <li>
              <h3>It works anywhere</h3>
              <p>The model runs on the device, so a signal is not needed.</p>
            </li>
            <li>
              <h3>It stays private</h3>
              <p>The video never has to leave the bike. The website demo already works this way.</p>
            </li>
          </ul>
        </div>
      </section>

      <section className="section alt">
        <div className="container">
          <div className="section-head reveal">
            <h2>Where it stands.</h2>
          </div>
          <div className="reveal">
            <StatusRows items={STATE} />
          </div>
          <p className="callout reveal">
            No part of RideShield is connected to a real engine today. The website and the desktop app show the detection and the interface of the on-bike idea on a laptop.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container cta-band reveal">
          <h2>Next steps.</h2>
          <p>The roadmap lists what has to be built to get from the laptop to the bike.</p>
          <div className="band-actions">
            <Link to="/roadmap" className="btn btn-primary">
              Future scope <ArrowRight size={18} className="arrow" />
            </Link>
            <Link to="/test-drive" className="btn">Try the detector</Link>
          </div>
        </div>
      </section>
    </>
  )
}
