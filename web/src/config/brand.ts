// Single source of truth for identity. Name, tagline, logo text and links are NOT final:
// change them here (and the mark in components/Logo.tsx) and the whole site follows.
export const BRAND = {
  name: 'RideShield AI',
  short: 'RideShield',
  tagline: 'AI road safety that rides with you.',
  description:
    'RideShield AI detects helmet use in traffic footage with a YOLO model that runs entirely in your browser.',
  repoUrl: 'https://github.com/taqi-ai/RideShieldAI',
  // Drop the finished film at web/public/media/rideshield-trailer.mp4 (see DEPLOYMENT.md).
  trailer: {
    src: '/media/rideshield-trailer.mp4',
    captions: '/media/rideshield-trailer.vtt',
    poster: '/media/rideshield-trailer-poster.jpg',
  },
} as const
