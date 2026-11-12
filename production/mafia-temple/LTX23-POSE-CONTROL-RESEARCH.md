# LTX 2.3 motion and environment research — not a final film

Budget: zero. Nothing here is an approved final film.

## Pose motion

- The official LTX-2.3 Union Control ref0.5 adapter was checked against SHA-256 `a1b888a87f661d27f08b394ae559e8e1050be33900bcc36a5cdf659e48f88d18`. Model and adapter remain subject to the LTX Community License and other terms.
- First guide comprised low-resolution JPEG pose thumbnails from earlier Pexels preflight, potentially incomplete/misaligned and not cleared for final use. Only previously public pose-only images and generated keyframes were used; neither original photograph nor stock footage/audio was uploaded.
- Actions `42541505158`, `42542831615`, and `42544343216` failed during integration or GPU memory allocation. Diagnostic `42547501065` located the OOM in the video VAE encoder on GPU 1. Enabling 128-pixel spatial and 32-frame temporal VAE tiles fixed that bottleneck.
- Action `42547620845` completed a 49-frame/24 fps pose test at 448×768 (SHA-256 `ad4dd316efe7c1525cc00e717aa5739196aaa9b8515b0117ee7aa342255a5bc0`; public output blob `3b11f40c997013dc5d34daa3ecc3d81946da21fb`). Diagnostic `42549357914` confirms the Union LoRA was loaded. All frames were reviewed: camera tracking is visible, but curved/hooked shoes, smears and unreliable ground contact remain. Not usable as a final shot.
- Action `42549566624` tested 25 lossless poses projected from CMU 35_17 (source terms and limitations in `motion-control/README.md`), 448×768 at 24 fps (SHA-256 `634ccc73f4b44bf9258daab4c05730d203b130086187b771234dec5e896c6b4b`; blob `ad80bcebc85a91bc07492ba89a16aee19465255a`). All 25 frames and foot crops reviewed. The clip tracks sideways but repeats unnatural gait with hooked shoes and ambiguous foot contact, and does not establish identity fidelity. Rejected as final.

## Environment candidates

- Action `42551080332` completed `ltx23-gate.mp4` (121 frames, 24 fps, 832×480, SHA-256 `2670cf232981fd2d4fcfb5df5cd861215eb56dff480b57f174690a10995833c2`, blob `ed19b515a11aa81514744ac4baf656dfbcc0ddf3`) and `ltx23-aerial.mp4` (97 frames, 24 fps, 832×480, SHA-256 `b65465afc78b53491b8332c9f25ccce6cc7f4983e8e9503bd3cdd4452dbe1f84`, blob `dcc88f6fb53234613ccdced666253e2e0090ad64`). All frames inspected in contact sheets; selected frames examined at full resolution.
- Gate has plausible atmospheric mist, but visibly pulls back despite the locked-off prompt; architecture changes slightly and native output is only 832×480. Aerial moves toward the courtyard, one small figure persists, but scene geometry and detail fluctuate and its motion cannot be certified as real 3D. Both are provisional candidates, not final approval. Generated audio remains unauditioned; project audio needs separate creative review.

No compliant 20-second film exists yet. Do not present rejected pilots as completed work or suggest motion, identity, audio, license or final edit is verified.
