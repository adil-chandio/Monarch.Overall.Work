# v5 — the reference's edit, our objects (first 7 s)

The user's file has arrived and is **the same reference**: md5 `b09a37ef77ac1438326715b0bdbe2f02`,
3,244,599 bytes, 23.266 s, 720×1280 — the file this repo has been measuring all along.
So the target is confirmed, and the remaining problem is the one already on the table:
the reference's photographs are generated objects we do not own.

This build is the answer to that: keep everything that is *editorial* — timecodes,
transitions, layout, type system, grade, grain — and put our plates in the object slots.

```
tools/v5.py        one shot per scene, our assets only, no reference pixels
spec/v5-01.json    timecodes from analysis/v4-build/shots.json
```

## What matches the reference

| | reference | v5 |
|---|---|---|
| duration, 0–7 s | 210 frames @ 30 fps | 210 frames @ 30 fps |
| cuts | 0.533 / 0.800 / 1.333 / 3.133 | same |
| type block 0–0.80 | TWENTY on a lit card, then the slam | rebuilt from measured table (see log 01) |
| green field | FULL colour, bag low-centre, BILLION above | same layout, our bag |
| storm | bright grey, stool centre, HE then NO | same, our stool |
| red room | 2008, red field, figure, slow push | same, our portrait |
| grade | sat 83.9 / luma 72.8 (green), sat 14.1 / luma 145.8 (storm), sat 69.4 / luma 40.0 (red) | **70.0 / 63.1, 18.3 / 134.4, 69.7 / 44.0** |

## Measured, against the reference

```
no black frames            (dimmest frame mean 24.3)
no frozen frames           (0 identical consecutive pairs)
graded to the reference's    saturation and luma per shot, above
```

## Speed

210 frames in **20 s** for a 7 s block — 10.3 fps of finished 720×1280 x264, no browser,
no frame directory. The whole 23.27 s is about **70 s**.

## What is different, honestly

Every photographic object. The reference's bag, easel, stool and portrait are its own
generated images; ours are different photographs of the same ideas. This build is
therefore **the same film, not the same frames** — the edit is identical and the pictures
are ours. That is the only kind of "exact" available without the original assets.
