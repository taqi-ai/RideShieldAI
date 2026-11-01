// Describes the ONNX assets that ship with the site. Every file was exported with
// web/scripts/export_model.py: dynamic height and width, input float32 RGB 0..1, classes from the
// trained weights. Output layouts differ by architecture, so each spec says how to decode it.
export interface ModelSpec {
  id: string
  label: string
  family: string
  blurb: string
  url: string
  sizeBytes: number
  inputSize: number
  // true when exported with dynamic height/width (input is padded only to a multiple of 32).
  dynamic: boolean
  // 'end2end': output [1,300,6] rows of x1,y1,x2,y2,score,class (already NMS-free).
  // 'raw': output [1,4+nc,A] with cx,cy,w,h then class scores; needs NMS.
  output: 'end2end' | 'raw'
  classes: readonly string[]
  source: string
}

const CLASSES = ['helmet', 'nohelmet'] as const

export const MODELS: readonly ModelSpec[] = [
  {
    id: 'yolo26n',
    label: 'YOLO26n',
    family: 'YOLO26',
    blurb: 'Smallest and fastest. Best default for phones and older laptops.',
    url: '/models/helmet_yolo26n.dynamic.onnx',
    sizeBytes: 10_057_613,
    inputSize: 640,
    dynamic: true,
    output: 'end2end',
    classes: CLASSES,
    source: 'models/helmet_yolo26n.pt',
  },
  {
    id: 'yolov8s',
    label: 'YOLOv8s',
    family: 'YOLOv8',
    blurb: 'Mid-size model trained from YOLOv8s. Balanced speed and size.',
    url: '/models/helmet_yolov8s.dynamic.onnx',
    sizeBytes: 44_772_395,
    inputSize: 640,
    dynamic: true,
    output: 'raw',
    classes: CLASSES,
    source: 'models/best.pt',
  },
  {
    id: 'yolo11m',
    label: 'YOLO11m',
    family: 'YOLO11',
    blurb: 'Largest model, the desktop app default. Slowest to download and run.',
    url: '/models/helmet_yolo11m.dynamic.onnx',
    sizeBytes: 80_589_368,
    inputSize: 640,
    dynamic: true,
    output: 'raw',
    classes: CLASSES,
    source: 'models/yolo11m.pt',
  },
]

export const DEFAULT_MODEL = MODELS[0]

export function getModel(id: string | null | undefined): ModelSpec {
  return MODELS.find((m) => m.id === id) ?? DEFAULT_MODEL
}

const KEY = 'rideshield-model'

// ?model=yolov8s wins, then the visitor's last choice, then the default.
export function initialModelId(): string {
  try {
    const fromUrl = new URLSearchParams(location.search).get('model')
    if (fromUrl && MODELS.some((m) => m.id === fromUrl)) return fromUrl
    const saved = localStorage.getItem(KEY)
    if (saved && MODELS.some((m) => m.id === saved)) return saved
  } catch {
    /* storage blocked: use the default */
  }
  return DEFAULT_MODEL.id
}

export function rememberModelId(id: string) {
  try {
    localStorage.setItem(KEY, id)
  } catch {
    /* private mode: the choice just lasts for this visit */
  }
}
