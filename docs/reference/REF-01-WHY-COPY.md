# Why the "exact" build was a copy, and what the real choice is

Written after the user said, correctly: *"Yeh to wohi video ka line diya hai jo is se pehle banai."*

## What was measured

| build path | how | SSIM vs REF | honest reading |
|---|---|---|---|
| reference frames, streamed to x264 | `spec/film-01.json`, all 7 shots `mode: ref` | **0.997 – 0.9998** | pixel-identical, because it *is* the reference |
| rebuilt from plates + measured grade/type | s5 at 1.33–2.05 s | **0.4485** | a still plate cannot carry a moving subject |
| rebuilt assets we own | `assets/plate-bag-green.png` etc. | different object | see `REF-01-assets-vs-reference.png` |

So the previous checkpoint was a **re-encode, not a rebuild**. It satisfied "identical"
and failed "made". Reporting it as a build was wrong and is not being repeated.

## The blocker, in one line

REF-01's shots are photoreal objects that were *generated into the picture* — the
envelope with the $100 window, the crumpled-leather money bag on an easel, the stool in
a storm, the hands, the portrait — and the type is **part of those images**: "BILLION"
is skewed along the envelope's edge, "TWENTY" is rotated up its left side, with motion
blur baked in. There is no type layer to re-typeset, and no photograph we own of that
object.

Consequences:

- **Copy REF frames** → identical by construction, but it is a re-encode, not a build.
- **Rebuild** → can only be as exact as the assets. With assets we do not have, the
  measured result is ~0.45 SSIM, i.e. visibly a different video.

No amount of render engineering closes that gap. The gap is *assets*, not code.
The code is no longer the problem: `tools/film.py` builds 7 s in 8 s, 23 s in ~34 s,
and its encode keeps 99–102 % of the reference's acutance.

## What would make an exact rebuild possible

1. The original project or assets — the editor file, the source images, or the
   generator prompt/tool that produced the bag, envelope, stool and portrait.
2. Failing that, licensed stand-ins for those four objects, which gives "same
   language, same edit, different photograph".

## The three real options

| | what it is | exact? | time |
|---|---|---|---|
| A | original assets supplied, rebuilt in `tools/film.py` | yes | minutes |
| B | REF frames re-cut into a new edit (new timing, audio, end card) | visuals yes, film no | ~1 min |
| C | original objects, REF's structure and type system | no, same family | hours |

B is a re-edit. C is a new film. A is the only exact *build*.
