import { iou, type Detection } from './engine'

export interface Track {
  id: number
  box: { x1: number; y1: number; x2: number; y2: number }
  hits: number
  missed: number
  votes: number[] // summed confidence per class
  lastScore: number
  firstSeen: number
  lastSeen: number
}

export interface TrackedDetection extends Detection {
  trackId: number
  confirmed: boolean
}

const MIN_HITS = 3 // frames a box must persist before it counts as a real object
const MAX_MISSED = 12 // processed frames without a match before a track is retired
const MATCH_IOU = 0.3

// Small IoU tracker. It exists so counters can say "unique objects" without counting the same
// rider once per frame. It is deliberately simple: no motion model, greedy matching.
export class Tracker {
  private nextId = 1
  private tracks: Track[] = []
  readonly classCount: number

  constructor(classCount: number) {
    this.classCount = classCount
  }

  reset() {
    this.tracks = []
    this.nextId = 1
  }

  update(dets: Detection[], now: number): TrackedDetection[] {
    const used = new Set<number>()
    const pairs: { t: number; d: number; v: number }[] = []
    this.tracks.forEach((t, ti) =>
      dets.forEach((d, di) => {
        const v = iou(t.box, d)
        if (v >= MATCH_IOU) pairs.push({ t: ti, d: di, v })
      }),
    )
    pairs.sort((a, b) => b.v - a.v)
    const trackUsed = new Set<number>()
    const assigned = new Map<number, Track>()
    for (const p of pairs) {
      if (trackUsed.has(p.t) || used.has(p.d)) continue
      trackUsed.add(p.t)
      used.add(p.d)
      const t = this.tracks[p.t]
      const d = dets[p.d]
      t.box = { x1: d.x1, y1: d.y1, x2: d.x2, y2: d.y2 }
      t.hits++
      t.missed = 0
      t.votes[d.cls] += d.score
      t.lastScore = d.score
      t.lastSeen = now
      assigned.set(p.d, t)
    }
    this.tracks.forEach((t, ti) => {
      if (!trackUsed.has(ti)) t.missed++
    })
    dets.forEach((d, di) => {
      if (used.has(di)) return
      const votes = new Array<number>(this.classCount).fill(0)
      votes[d.cls] = d.score
      const t: Track = {
        id: this.nextId++,
        box: { x1: d.x1, y1: d.y1, x2: d.x2, y2: d.y2 },
        hits: 1,
        missed: 0,
        votes,
        lastScore: d.score,
        firstSeen: now,
        lastSeen: now,
      }
      this.tracks.push(t)
      assigned.set(di, t)
    })
    this.tracks = this.tracks.filter((t) => t.missed <= MAX_MISSED)
    return dets.map((d, di) => {
      const t = assigned.get(di)!
      return { ...d, trackId: t.id, confirmed: t.hits >= MIN_HITS }
    })
  }

  // Class with the most accumulated confidence for a track (stabilises flicker between classes).
  static majority(t: Track): number {
    let best = 0
    for (let c = 1; c < t.votes.length; c++) if (t.votes[c] > t.votes[best]) best = c
    return best
  }

  get active(): readonly Track[] {
    return this.tracks
  }

  static readonly MIN_HITS = MIN_HITS
}
