import { Link } from 'react-router-dom'
import { ArrowRight } from '@phosphor-icons/react'
import { BRAND } from '../config/brand'
import { PageBand } from '../components/PageBand'
import { StatusRows, type RowItem } from '../components/StatusRows'
import { usePageMeta } from '../hooks/usePageMeta'

const TODAY: RowItem[] = [
  {
    title: 'Website test drive',
    text: 'Runs a helmet model in your browser on a webcam or an uploaded video. Boxes, confidence scores, and counts of riders tracked across frames. Nothing is uploaded.',
    status: 'built',
  },
  {
    title: 'Desktop app',
    text: 'A PyQt6 dashboard styled like a motorcycle cluster. It reads a local camera, speaks a warning when no helmet is seen, saves a snapshot of each alert and keeps a local event log.',
    status: 'built',
  },
  {
    title: 'Three models',
    text: 'YOLO26n, YOLOv8s and YOLO11m, trained on the same two classes: helmet and nohelmet. The website can switch between them.',
    status: 'built',
  },
  {
    title: 'Engine lock',
    text: 'The desktop app has a Smart Lock mode that records "engine lock simulated" and shows the lock on screen. It is not connected to any engine.',
    status: 'simulated',
  },
]

export default function Project() {
  usePageMeta(`The project | ${BRAND.name}`, 'What RideShield AI is, why it exists, what works today and what has not been measured yet.')
  return (
    <>
      <PageBand title="The project">
        RideShield AI checks whether a rider is wearing a helmet, using a camera and a model that runs on the device itself.
      </PageBand>

      <section className="section">
        <div className="container"><div className="prose reveal">
          <h2>Why it exists</h2>
          <p>
            A helmet only protects the rider who is wearing it. Helmet rules are usually enforced by a person at the roadside, or by someone reviewing footage after the ride. By then the decision has already been made.
          </p>
          <p>
            RideShield asks the question earlier and without a person in the loop: is the helmet on? The idea behind it is a detector that sits on the motorcycle itself. You can read that on the{' '}
            <Link to="/on-bike" className="textlink">on-bike page</Link>. What you can try today is the detection half of that idea, running in a browser or on a laptop.
          </p>
        </div></div>
      </section>

      <section className="section alt">
        <div className="container">
          <div className="section-head reveal">
            <h2>What exists today</h2>
            <p>Each item is labelled with what it really is.</p>
          </div>
          <div className="reveal">
            <StatusRows items={TODAY} />
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container two">
          <div className="prose reveal">
            <h2>How a detection works</h2>
            <p>
              A frame from the camera or video is resized to fit the model, with grey padding so nothing is stretched. The model returns boxes, each with a class (helmet or nohelmet) and a confidence score. Boxes that overlap from one frame to the next are matched, so a rider who stays in view is counted once.
            </p>
            <p>
              The website runs this with ONNX Runtime Web, on the graphics chip through WebGPU when the browser allows it and on the processor through WebAssembly when it does not. The desktop app runs the same kind of model through Ultralytics.
            </p>
          </div>
          <div className="prose reveal">
            <h2>What has not been measured</h2>
            <p>
              No accuracy figures are published for these models. We checked that the browser version gives the same detections as the original weights on test photos, but we have not run a formal test with a held-out set, so there is no precision or recall number to quote.
            </p>
            <p>
              The models know two classes only. They do not detect a second rider, a loose strap or a helmet worn on the arm. Night, rain, visors and scarves are likely weak spots and are listed on the roadmap. This is a demonstration, not a certified safety device.
            </p>
          </div>
        </div>
      </section>

      <section className="section alt">
        <div className="container cta-band reveal">
          <h2>See it work.</h2>
          <p>Try the detector on your camera or a clip, or read where the project is going.</p>
          <div className="band-actions">
            <Link to="/test-drive" className="btn btn-primary">
              Experience RideShield <ArrowRight size={18} className="arrow" />
            </Link>
            <Link to="/roadmap" className="btn">Future scope</Link>
          </div>
        </div>
      </section>
    </>
  )
}
