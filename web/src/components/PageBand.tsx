// The violet header band shared by the project pages: same ground and slab as the home hero.
export function PageBand({ title, children }: { title: string; children?: React.ReactNode }) {
  return (
    <section className="band" aria-labelledby="band-title">
      <div aria-hidden className="slab" />
      <div className="container">
        <h1 id="band-title">{title}</h1>
        {children && <p className="lead">{children}</p>}
      </div>
    </section>
  )
}

export type Status = 'built' | 'simulated' | 'planned' | 'exploring'

const LABEL: Record<Status, string> = {
  built: 'Built',
  simulated: 'Simulated',
  planned: 'Planned',
  exploring: 'Exploring',
}

export function StatusTag({ status }: { status: Status }) {
  return <span className={`status status-${status}`}>{LABEL[status]}</span>
}
