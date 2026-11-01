import { StatusTag, type Status } from './PageBand'

export interface RowItem {
  title: string
  text: string
  status: Status
}

// One filled row per item: name on the left, what it is in the middle, its honest status on the right.
export function StatusRows({ items }: { items: RowItem[] }) {
  return (
    <ul className="rows">
      {items.map((i) => (
        <li key={i.title} className="row">
          <h3>{i.title}</h3>
          <p>{i.text}</p>
          <StatusTag status={i.status} />
        </li>
      ))}
    </ul>
  )
}
