# Viral short — `youtube automation`

**42 s · 1920×1080 · 30 fps · Urdu-English voiceover · every number measured**

## The idea, chosen from data

Of 30 videos on `youtube automation` (7.8M views combined):

| | |
|---|---|
| #1 video | **25% of every view in the topic** (1,922,751 views) |
| 29 others | split the remaining 75% |
| median | 51,654 views — **37× below** #1 |
| top 5 titles | **3 of 5** are literally "how to start" |
| 100 comments | **11% want to pay for teaching**, 1% asked for a sequel |

So the topic is not saturated. It is **concentrated** — one winner and twenty-nine copies of it.
That is the video, and it ends on SHARPEN, not GO.

## The script

| time | scene | line |
|---|---|---|
| 0.0 | 25% counter | "Ek video is topic ki har view ka pachees percent le rahi hai." |
| 4.9 | 29 counters fill | "Baqi untees videos, aapas mein baant rahe hain. Pachehattar percent, un sab ka mila kar." |
| 11.3 | two numbers diverge | "Number one: unnees lakh views. Typical video: ikyavan hazaar. Same topic. Chhattees guna ka farq." |
| 18.5 | top-5 list staggers in | "Top five mein se teen sirf shuruaat sikhate hain. Koi nahi batata ke kaun shuru kar ke chhod gaya." |
| 25.1 | SATURATED struck out | "Yeh topic saturated nahi hai. Concentrated hai. Ek jeetne wala, untees uski copy." |
| 31.7 | 11 of 100 squares fill | "Sau comments padhe. Gyarah log teaching ke paise dena chahte hain. Aur tutorial nahi." |
| 37.3 | stillness, then the mark | "Next video: woh hissa jo koi film nahi karta." |

## How it is built (and what the skills demanded)

`showreel/viral_short.py` renders with PIL frames piped straight to ffmpeg. It follows
`skills/hyperframes/motion-doctrine`:

- **Narration is the clock.** Beat boundaries are the measured VO timestamps from
  `public/demo/vo/timing.json` — not invented numbers. A VO regen re-times the film.
- **A camera, not a slideshow.** The world is 4.4 screens wide; the camera holds on each
  anchor and whips between them. No scene is ever composed next to another.
- **Every seam is mid-motion.** The whip is at full speed on both sides; inside every beat the
  content itself is animating (counters tick, bars grow, rows stagger). There is no dead beat.
- **No idle wobble.** Nothing breathes or floats. Each held beat has an owner.
- **Carrier.** The red rule runs under every scene and the progress rule never leaves.
- **Stillness before climax.** 0.45 s of camera drift only, before the last line.

## Checks that run before a render is accepted

- `showreel/qc_framing.py` — composes every scene alone and fails if its own bounding box
  touches the frame edge. It exists because two renders shipped with the first letter of every
  headline sliced off. Its *first* version was also wrong: it flagged a scene leaving the frame
  during a whip, which is the transition working correctly.
- `showreel/ctr/hook.py` — the repo's own hook scorer: motion at frame 0, a specific claim in
  words inside ~1.5 s, no ramp-up.
- `python -m yt_intel style` on the finished file — cut agreement, pacing, motion profile.

## Measured output

```
duration   42.23 s        loudness  -14.7 LUFS (YouTube target)
voice      -14.5 dBFS     bed       -24 dBFS (ducked under the voice)
```

## Rebuild

```bash
python showreel/qc_framing.py            # fails fast on composition errors
python showreel/viral_short.py           # ~70 s render
```

Fresh narration: write the seven lines to `public/demo/vo/*.mp3`, recompute
`public/demo/vo/timing.json`, re-render.
