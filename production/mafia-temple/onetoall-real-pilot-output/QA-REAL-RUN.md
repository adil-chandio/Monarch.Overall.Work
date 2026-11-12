# Real-motion One-to-All pilot — review

**Verdict: research only. Not a finished or production-approved film shot.** This is the one bounded follow-up approved after the first running pilot, not the requested 20-second film.

## What was actually reviewed

All 49 decoded frames were inspected in sequential seven-frame contact sheets, and enlarged foot and upper-body crops were checked at frames 0, 2, 5, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 31, 34, 37, 40, 43, 46 and 48. Input pose controls and reference framing were inspected separately before generation; see `../REAL-DRIVER-PREFLIGHT.md`. This was a frame-by-frame visual inspection, **not a real-time playback review**. The MP4 contains no audio.

The output is 49 frames, 16 fps, 480×832, 3.0625 seconds, H.264. The private GPU kernel completed on Tesla T4 (compute capability 7.5); prompt execution took 402.9 seconds. The graph uses the 1.3B model, 8 sampling steps, FP16 text encoder and VAE, `align_to=none`, and a mirrored, uniformly reframed real runner as pose input. The receipt correctly distinguishes native BF16 (`false`) from emulated support (`true`). No original user photo was uploaded.

## Findings

- **Better preservation of the reference and setting:** the black suited, bearded character and portions of the blue-lit red temple courtyard remain visible throughout. Both shoes are present in the reference audit; the previous test's reference warp had cropped them out. Compared with the earlier One-to-All result, the courtyard architecture is more recognizable and the motion source is a real performance rather than a generated v6 loop.
- **Gait is still not trustworthy:** the rear shoe narrows into a hook or tapered spike at frames such as 2, 8, 12, 25 and 40. The legs and ankles appear to merge or change thickness around frames 5, 10, 20, 37 and 46. There are blurred feet and broad, shifting dark shadows rather than consistently convincing contact. The floor markings and texture smear and appear to slide; the shot does not demonstrate a physically grounded tracked camera.
- **Face, hair and hands change:** compare frames 14, 20, 28, 34, 40 and 46. The face and hair change shape or lose detail across the run. Hands are tiny, often mitten-like and sometimes obscured. The generated character broadly follows the approved generated reference, but a private visual comparison to the original is insufficient to certify the requested likeness.
- **Continuity and cinematic delivery are unproven:** the scene is largely a reference-like courtyard plate, not verified 3D camera motion through the same temple. Floor details and the lamp change or leave the frame. The clip is a 16 fps portrait research output with no sound, not a completed five-shot edit. Upscaling or interpolation would not repair identity, anatomy or contact.

## Provenance and rights

The driver window was drawn from [Eduardo Holanda's Pexels 32740423](https://www.pexels.com/video/man-running-outdoors-on-open-road-32740423/), rendition SHA-256 `fef029f40687ee924f0eaef6e3da932485441db4b9a3c992780121b12507e28d`. The real source video was used only to obtain pose controls inside a verified private Kaggle dataset/kernel; its pixels, face and clothing were not supplied as the appearance reference or included as video footage in the output. Face landmark drawing from the source was disabled. The generated-reference image came from the already-public pinned project commit `4204ebe`.

[Pexels rules](https://help.pexels.com/hc/en-us/articles/360042332714-What-are-the-rules-for-using-Pexels-photos-or-videos) restrict depicting identifiable people as engaged in criminal activities or implying endorsement. The source athlete is not intentionally represented; no blanket legal clearance is claimed. Review performer identifiability, any model-release/privacy requirements, and all auxiliary model licences before production publication. The generated pilot has been made available for the user's review, not labelled final.

## Next gate

Do not assemble this shot into a claimed final film. The remaining problem is not just driver quality: this small 1.3B/FP16/8-step pipeline still invents unstable shoe geometry, struggles with occluded hands and alters the character. Evaluate a stronger identity-and-motion-controlled method and secure sufficient compute/rights before rendering the remaining shots; independently validate a gait/contact and identity test, then review every shot in motion and the full timed audiovisual edit. The prior rejected 20-second review must not be re-delivered as final.
