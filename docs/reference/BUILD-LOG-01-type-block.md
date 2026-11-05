# Build log — 0.00–0.80 s rebuilt from nothing but numbers

This block does not contain a single reference pixel. It is a polynomial surface, one
font and 24 rows of measured parameters:

```
tools/build_typo_table.py   measures the reference once   -> spec/typo-block.json
tools/typo_core.py          draws from that table only
tools/block_typo.py         streams frames to x264        -> public/demo/block-typo.mp4
```

## Result

| | value |
|---|---|
| block | 0.00–0.80 s, 24 frames, 720×1280 |
| build time | **12 s** (whole block, including the measurement pass) |
| whole-frame mean abs diff vs REF | **5.49 / 255** (2.2 %) |
| background-only mean abs diff | **3.41 / 255** (1.3 %) |
| frames that are black or frozen | 0 |

## What is measured, not styled

- **Plate** — 15-term polynomial fitted to the reference's own plate, *per frame*, so
  the light band's position and its dimming are numbers. rms 2.5/255.
  A sampled grid was tried first and showed its own cells; a formula was tried before
  that and put the hot spot in the wrong place.
- **Word** — box (x, y, w, h) read off the reference's green-excess channel each frame:
  x 178→132→60, y 290→628, w 361→567, i.e. it descends and grows.
- **Font** — Archivo Black, chosen by IoU on the settled frame (**0.747**) against 58
  candidate faces; Montserrat 900 was 0.663, Anton 0.700. That IoU is the block's
  honest ceiling: 25 % of the letterform area differs from whatever face the reference
  used, and no amount of rendering closes it.
- **Travel** — a number that the reference gives: the box is ~1.5× taller than the font
  at those widths while it moves, so the shutter is open during the travel. The frame is
  the word averaged along its path, not a stretched glyph (stretching inked the whole
  span at full weight, which the reference never does).
- **Dimmer** — the plate's own centre luma per frame, applied to the plate and not to
  the lettering: the reference dims the room, the word keeps its colour.

## Things this block cannot contain, by construction

- **"BILLION" from 0.44 s** — it enters skewed along an envelope's edge, cut by that
  object. Without the object there is no honest place to put the letters.
- **The photographic shots** (entrance, envelope, bag on easel, stool, hands, portrait).
  These are the reference's generated images; see `REF-01-WHY-COPY.md`.

So: 0 → 0.80 s is rebuilt. 0.80 → 23.35 s needs the object assets, or a decision to put
different objects in those slots.
