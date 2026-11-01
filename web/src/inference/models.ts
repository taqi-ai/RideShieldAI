// Describes the ONNX assets that ship with the site. Values come from the real export
// (see DEPLOYMENT.md): input 1x3x640x640 float32 RGB 0..1, classes from the trained weights.
export interface ModelSpec {
  id: string
  label: string
  url: string
  sizeBytes: number
  inputSize: number
  // true when exported with dynamic height/width (input is padded only to a multiple of 32).
  dynamic: boolean
  // 'end2end': output [1,300,6] rows of x1,y1,x2,y2,score,class (already NMS-free).
  // 'raw': output [1,4+nc,8400] with cx,cy,w,h then class scores; needs NMS.
  output: 'end2end' | 'raw'
  classes: readonly string[]
  source: string
}

export const MODELS: readonly ModelSpec[] = [
  {
    id: 'helmet_yolo26n',
    label: 'YOLO26n helmet model',
    url: '/models/helmet_yolo26n.dynamic.onnx',
    sizeBytes: 10_057_613,
    inputSize: 640,
    dynamic: true,
    output: 'end2end',
    classes: ['helmet', 'nohelmet'],
    source: 'models/helmet_yolo26n.pt',
  },
]

export const DEFAULT_MODEL = MODELS[0]
