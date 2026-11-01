import { lazy, Suspense } from 'react'
import { Link, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import Home from './pages/Home'
import { usePageMeta } from './hooks/usePageMeta'

// The cockpit pulls in ONNX Runtime, so it is split out of the landing bundle.
const TestDrive = lazy(() => import('./pages/TestDrive'))
const Trailer = lazy(() => import('./pages/Trailer'))

function NotFound() {
  usePageMeta('Page not found | RideShield AI', 'This page does not exist.')
  return (
    <div className="container notfound">
      <div>
        <h1>That page is off the map.</h1>
        <p style={{ color: 'var(--muted)', margin: '14px 0 24px' }}>The address does not match any RideShield page.</p>
        <Link to="/" className="btn btn-primary">Back to home</Link>
      </div>
    </div>
  )
}

const Loading = () => (
  <div className="container notfound" role="status">
    <p style={{ color: 'var(--muted)' }}>Loading...</p>
  </div>
)

export default function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        {/* Test drive is a full-screen cockpit, so it sits outside the marketing layout. */}
        <Route path="/test-drive" element={<TestDrive />} />
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="/trailer" element={<Trailer />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Suspense>
  )
}
