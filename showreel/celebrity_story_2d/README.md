# Celebrity morning — painted 2D cut (v2)

A 60-second portrait film, 1080×1920 at 24 fps, animated **frame by frame**
from painted cels. Same script, same narration takes, same cue timings as the
3D v6 cut; every image is new.

**Deliverable:** `deliverables/monarch-celebrity-story-2d-60s.mp4`
(60.00 s, 1080×1920, 24 fps, H.264 High + AAC, 47 MB, −16.3 LUFS, −0.8 dBTP)
**Preview:** `deliverables/monarch-celebrity-story-2d-60s-preview.mp4` (608×1080, 4.3 MB)

## What changed from v1

v1 pasted painted sprites onto painted plates: one rigid cut-out per shot,
sliding across a background. It was rejected, and correctly — that is not
animation, it is a slideshow with a camera on it.

v2 is built the way a 2D production is built:

| Production step | Where it lives |
| --- | --- |
| Cel library — a painted pose per drawing, keyed off flat green | `anim2d.py` (`cut_green`, `normalise`) |
| Model sheet locked pose to pose | `assets/frames/`, generated against `assets/hero_*.png` |
| Head-anchored placement, so a swinging arm never shifts the body | `anim2d.Cel.pivot` |
| Pose changes as **cuts**, not dissolves | `scene2d.pose_frame` |
| Lip sync from the recorded narration | `voice2d.py` → `anim2d.speak_mix` |
| Virtual camera over overscan plates | `scene2d.view_of` |
| Per-act light, grade, bloom, halation, grain | `scene2d.apply_grade` |
| One cue table for picture, captions and sound | `script.json`, `film_a.shots`, `mix2d.py` |

Every one of the 1440 frames is rendered individually; nothing is a still with
a filter over it.

## Two decisions worth recording

**Pose hand-offs cut.** Two separately drawn poses share no pixel
correspondence — the arms and legs are in different places. Cross-fading them
pastes a second, half-transparent figure on screen (a "double exposure" ghost).
Drawn animation flips the drawing instead. Only the sub-pixel idle motion —
breathing and sway, applied as a displacement of the cel's own shape field —
runs continuously.

**Lip sync swaps a drawn lip chart.** Three approaches were tried and two
failed:

- *Drawing a synthetic mouth onto the cel* — reads as a dark blob pasted over
  the beard. Rejected.
- *Warping the jaw open from the envelope* — shears the chin and leaves a
  ghosted double smile. Rejected.
- *Registering the open-mouth drawing onto the base cel and swapping it in
  inside a feathered patch* — this is what drawn animation actually does. The
  patch reaches the lip corners and stops below the nose, so the eyes, nose,
  hair and jaw of the base drawing are untouched. Used.

The swap is driven by the narration audio, not a timer: each take is analysed
into a per-frame envelope at 24 fps (`voice2d.build_track`), and that envelope
decides when the mouth is open.

## Shot list — 14 shots, 1440 frames

| # | Time | Shot |
| --- | --- | --- |
| 1 | 0.00–5.40 | Bedroom dawn, lying awake, push in |
| 2 | 5.40–8.60 | Phone insert — screen is the light source |
| 3 | 8.60–11.91 | Close on him, the calls |
| 4 | 11.91–14.60 | Kitchen — coffee first |
| 5 | 14.60–17.24 | Mug insert |
| 6 | 17.24–20.20 | The window, in the suit |
| 6b | 20.20–22.95 | The empty street — the pause before the door |
| 7 | 22.95–29.81 | The street, walking into the noise, press flashes |
| 8 | 29.81–34.79 | The press line |
| 9 | 34.79–40.12 | The girl at the barrier |
| 10 | 40.12–46.31 | The reach |
| 11 | 46.31–50.54 | The car, the door closes |
| 12 | 50.54–55.60 | Night, at the glass |
| 13 | 55.60–60.00 | The empty room, slow push in |

## Rebuild

```sh
/PATH/.venv2d/bin/python showreel/celebrity_story_2d/film_a.py --out /tmp/silent.mp4
/PATH/.venv2d/bin/python showreel/celebrity_story_2d/mix2d.py /tmp/silent.mp4 out.mp4
```

One beat while iterating:

```sh
film_a.py --t0 40.1 --t1 46.3 --scale 0.5 --out /tmp/reach.mp4
```

Runtime: ~13 minutes for the full 1440 frames at 1080×1920 on this box
(~0.55 s/frame), plus ~3 minutes for the mix and delivery encode.

Dependencies are Pillow, numpy and imageio-ffmpeg only — no scipy, no GPU.

## Verified, not assumed

- **Frame count**: 1440 frames, 60.00 s exactly (`ffmpeg -f null -`).
- **Every shot** reviewed as a frame probe at full resolution; the contact
  sheet in this repo's history is the record.
- **Audio measured**: −16.3 LUFS integrated, −0.8 dBTP true peak, LRA 3.0.
- **Lip sync** checked frame by frame against the narration envelope across a
  spoken line.
- **Character consistency** checked across all 9 cels (head width, eye line,
  mouth line) after each drawing was added.

## What is still short of a studio film

- **Nine cels per character.** This is true limited animation — a drawing held
  and cut, plus continuous idle motion — not full animation at 24 unique
  drawings per second. A broadcast production would have a walk cycle and a
  lip chart of a dozen shapes per character.
- **The walk is a two-drawing cycle.** Readable, but it does not have the
  weight shift of a real cycle with breakdowns.
- **No eye blinks, no eyelid acting.** The painted cels carry a fixed gaze.
- **The camera does the acting in the static beats.** Where a full production
  would animate a hand or a shoulder, this holds the cel and moves the camera.

These are stated plainly rather than claimed away: the film is a real animated
short made frame by frame, and it is not a studio production.
