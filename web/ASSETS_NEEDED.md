# Assets the site is waiting for

The page already has a slot for each file below. Drop a file at the exact path and it appears automatically
(no code change); until then the slot shows nothing, never a broken image. Commit and push the files and
Vercel redeploys.

Rules for every image: no text, no logos, no watermarks, no readable number plates, no recognisable real
people. JPG, sRGB, under 400 KB each (squoosh.app or similar). Keep the violet and near-black palette of the
brand in mind: cool night tones, one violet accent, nothing orange or beige.

| File | Where it shows | Size | Notes |
|---|---|---|---|
| `web/public/img/hero-rider.jpg` | Behind the "Drop in a traffic clip" text in the hero detector, dimmed to 40% | 1600 x 1000, landscape | A night road scene. Dark, so white text stays readable. |
| `web/public/img/detection.jpg` | Right side of the "Helmet detection" tile | 1200 x 900, landscape | A rider in a helmet, close and sharp. |
| `web/public/img/cta-road.jpg` | Behind the closing "Try it on your own footage" band, at 35% | 2000 x 900, wide | Empty road, lots of calm space. |
| `web/public/media/rideshield-trailer-poster.jpg` | Trailer card on the home page, and the trailer page | 1920 x 1080 | A cinematic still. Also used as the video poster. |
| `web/public/samples/sample.mp4` | Turns on the "Sample" button in the hero and test drive | 10 to 20 s, 720p or 1080p, H.264, under 20 MB | Real footage of riders with and without helmets that you have the rights to. |
| `web/public/media/rideshield-trailer.mp4` | The trailer player | 30 s, H.264, under 90 MB | See `DEPLOYMENT.md`. Optional `.vtt` captions. |
| Logo as SVG | Replaces the cropped PNG logos | vector | Day (dark ink) and night (light ink) versions, or one file with `currentColor`. |

## Prompts for ChatGPT (image generation)

Paste each as is. If the first result has any text, a logo or a face, say "regenerate with no text, no logos,
no visible faces" and try again.

**hero-rider.jpg**
> Photorealistic cinematic night photograph of a motorcycle rider in a full-face helmet riding along a wet
> city road, seen from behind and slightly to the left, tail lights and streetlights reflected on the
> asphalt, shallow depth of field, soft motion blur on the background, deep indigo and violet colour grade
> with cool blue shadows, very dark overall so white text on top stays readable. Wide landscape, 16:10. No
> text, no logos, no readable number plate, no visible face.

**detection.jpg**
> Photorealistic daylight photograph, sharp close-up of a motorcyclist's head and shoulders from the side
> while riding, wearing a modern full-face helmet with a dark visor, blurred traffic and buildings behind in
> cool grey tones, crisp focus on the helmet, natural light, slight violet tint in the shadows. Landscape,
> 4:3. No text, no logos, no brand marks, no visible face.

**cta-road.jpg**
> Photorealistic wide panoramic photograph of an empty highway at dusk disappearing toward the horizon,
> long soft light trails from passing traffic, sky in deep violet and indigo, lots of calm empty space in the
> upper half, cinematic, very dark and moody. Ultra wide, 21:9. No text, no logos, no vehicles in sharp
> detail, no number plates.

**rideshield-trailer-poster.jpg**
> Cinematic still frame for a road-safety film: a motorcycle rider's silhouette riding through a tunnel lit
> by rhythmic overhead lights, strong leading lines, deep violet and near-black palette, one bright white
> highlight on the helmet, subtle film grain, anamorphic feel. 16:9. No text, no logos, no number plates, no
> visible face.

**sample.mp4**: please use real footage you own or have a licence for (a phone clip of a road works well:
film from a bridge or a roadside for 15 seconds, riders passing, daylight, steady camera). Generated video
tends to warp riders and helmets, which makes a poor test for a detector.

**Logo SVG** (if you have the original vector, use it; otherwise ask the designer or tool that made the PNG):
> Export the RideShield helmet mark and the "rideshield" wordmark as clean SVG with flat fills, no raster
> images, no effects. Provide a dark-ink version for light backgrounds and a white version for dark
> backgrounds, violet accent kept as #6a43f0.

## After you add files

1. Put them at the paths above (create the folders if needed).
2. `git add web/public && git commit -m "Add photos" && git push`.
3. Vercel rebuilds; the slots fill in.
