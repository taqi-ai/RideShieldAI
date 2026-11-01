import { Link } from 'react-router-dom'
import { ArrowRight } from '@phosphor-icons/react'
import { BRAND } from '../config/brand'
import { PageBand } from '../components/PageBand'
import { StatusRows, type RowItem } from '../components/StatusRows'
import { usePageMeta } from '../hooks/usePageMeta'

const NEXT: RowItem[] = [
  {
    title: 'On-bike unit',
    text: 'A camera and a small computer fixed to the dashboard, running the detector with no network. Needs a smaller model, a mount, power from the bike and a weatherproof case.',
    status: 'planned',
  },
  {
    title: 'Ignition interlock',
    text: 'A relay that holds the start until the helmet is confirmed. It must never cut the engine while the bike is moving, and it must fail safe if the camera is blocked. Needs a safety design and a legal review before any test.',
    status: 'planned',
  },
  {
    title: 'Pillion detection',
    text: 'Check the second rider too. The models today know only helmet and nohelmet, so this needs a new class and training footage.',
    status: 'planned',
  },
  {
    title: 'Ride analytics',
    text: 'A history of each ride: how long the helmet was on, and when it was not. Kept on the device. The desktop app already stores events locally; this extends it per ride.',
    status: 'planned',
  },
  {
    title: 'Measured accuracy',
    text: 'A held-out test set and published precision and recall, split by day, night and rain. Until then no accuracy figure should be quoted.',
    status: 'planned',
  },
  {
    title: 'Night and weather robustness',
    text: 'More training footage in low light, rain, tinted visors, scarves and caps, which are the likely failure cases.',
    status: 'planned',
  },
  {
    title: 'Smaller, faster models',
    text: 'Quantized or pruned versions for low-power hardware. Not tried yet; it has to be checked against accuracy and against the graphics-chip backend.',
    status: 'planned',
  },
]

const LATER: RowItem[] = [
  { title: 'Strap fastened check', text: 'A helmet on the head with the strap open still fails in a crash. Could be a third class.', status: 'exploring' },
  { title: 'Fleet view', text: 'A dashboard for an operator with many bikes, using the same local event log idea.', status: 'exploring' },
  { title: 'More languages for voice prompts', text: 'The spoken warnings are in English only.', status: 'exploring' },
]

export default function Roadmap() {
  usePageMeta(`Future scope | ${BRAND.name}`, 'What RideShield AI has built, what is simulated, and what comes next. No dates are promised.')
  return (
    <>
      <PageBand title="Future scope">
        What comes next, in order. There are no dates here, because none have been committed.
      </PageBand>

      <section className="section">
        <div className="container">
          <div className="section-head reveal">
            <h2>The road to the bike.</h2>
            <p>The detector works. These are the pieces between a laptop demo and a unit on a motorcycle.</p>
          </div>
          <div className="reveal">
            <StatusRows items={NEXT} />
          </div>
        </div>
      </section>

      <section className="section alt">
        <div className="container">
          <div className="section-head reveal">
            <h2>Further out.</h2>
            <p>Ideas worth looking at once the on-bike unit exists.</p>
          </div>
          <div className="reveal">
            <StatusRows items={LATER} />
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container two">
          <div className="prose reveal">
            <h2>Open questions.</h2>
            <p>
              Some of the hard parts are not technical. They need answers before the idea can leave the laptop.
            </p>
          </div>
          <ul className="points reveal">
            <li>
              <h3>When should a bike refuse to start?</h3>
              <p>A wrong block strands a rider. A wrong allow gives false comfort. The right balance has to be decided with riders and regulators.</p>
            </li>
            <li>
              <h3>What happens when the camera cannot see?</h3>
              <p>Dirt, glare, a hand over the lens. The system needs a clear, safe behaviour for each.</p>
            </li>
            <li>
              <h3>Who is it for?</h3>
              <p>A personal safety aid, a fleet tool or a compliance device are three different products with different rules.</p>
            </li>
          </ul>
        </div>
      </section>

      <section className="section alt">
        <div className="container cta-band reveal">
          <h2>Follow the build.</h2>
          <p>The source for the website, the desktop app and the models is on GitHub.</p>
          <div className="band-actions">
            <a href={BRAND.repoUrl} target="_blank" rel="noreferrer noopener" className="btn btn-primary">
              Source on GitHub <ArrowRight size={18} className="arrow" />
            </a>
            <Link to="/on-bike" className="btn">The on-bike idea</Link>
          </div>
        </div>
      </section>
    </>
  )
}
