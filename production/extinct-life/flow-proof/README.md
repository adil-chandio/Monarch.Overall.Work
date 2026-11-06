# Extinct Life — 24-second sediment continuity proof

**Status: owner review pending. This is a new short visual-direction proof, not an approved full-film rebuild.** The earlier films remain unchanged. No YouTube upload is authorized or performed.

## Review deliverable

`deliverables/Extinct_Life_24s_Continuity_Proof_1080p.mp4`

1920×1080, 30 fps, 24 seconds. Eight three-second shots share one persistent 3D scene, one identifiable short DNA fragment, one mineral aggregate, the same lighting direction and the same side of the action axis. The fragment moves from the left towards the aggregate and approaches its surface during the binding explanation; it remains there for the protection/limitations explanation. The camera continues moving after the fragment settles. No full-frame generated image plate, reused old-film footage, pan-only slideshow, chapter reset, or cut-triggered whoosh sequence is used.

This is **stylised conceptual 3D**, not photoreal sample footage or a physically/chemically simulated reconstruction. The mineral forms, molecular colours, fragment geometry, distances, binding trajectory and particle motion are illustrative. A short ball-and-stick fragment is a readability device, not an atomically validated ancient sequence or recovered full genome. Apparent object sizes are not a calibrated soil-to-nanometre scale transition. The generated clay image supplies surface colour; the action, geometry, lighting, shadows and camera are rendered in 3D.

## Narration and cueing

The selected temporary Urdu-English review voice (`voice-01`, auditioned earlier in this conversation) is preserved losslessly in `voice.flac`. Duration: **23.36 s**. It is not stretched or compressed. The film is 24 s, including the narration's own pauses and a short final tail. This proof uses a compact explanatory passage; it is **not** another translation of the entire flagship script. Eventual channel narration remains English for the Tier-1 audience.

The original synthesis tool prompt is not reconstructed verbatim here: the preserved audio is authoritative. The following is an **English semantic cue sheet**, not a verbatim transcript or word-level forced alignment. Boundaries are the measured silences in the selected WAV, with the nine utterances assigned to their intended script cues; those assignments have not been independently verified by ASR or a human listener.

| Voice window (seconds) | Intended meaning | Visual action |
|---|---|---|
| 0.270–3.559 | Soil may contain small DNA fragments | Establish the material environment and a single short fragment |
| 4.144–5.935 | How could these survive? | Move closer without changing environment or fragment |
| 6.621–8.889 | Look more closely at the mechanism | Persistent fragment, closer camera, ongoing lateral drift |
| 9.662–11.564 | Cold can help | Continue the microscopic illustration; do not invent an ice-encapsulation event |
| 12.058–14.513 | Some fragments may bind to a mineral surface | The same fragment approaches the aggregate and settles |
| 14.970–16.549 | Binding can offer some protection | Reduced motion, sustained contact; no indestructible shield effect |
| 17.138–18.712 | This is not actual sample footage | Explicit reconstruction disclaimer remains visible |
| 19.024–20.154 | Not a complete genome | Short ends remain visible; do not grow a whole genome |
| 20.610–23.008 | An incomplete trace of ancient life | Pull back slightly on the same bound fragment |

The first and final captions are deliberately sparse. A small “Mineral surface” label accompanies the binding explanation (12.05–16.60 s). The finishing pass applies a restrained lift/desaturation grade, not a new scene or a transition effect. The continuous small disclaimer reads “Conceptual magnification · not actual sample imagery”.

## Sound

`finish.py` creates an original quiet three-note sustained bed, deterministic filtered air and one restrained settlement texture. The bed bridges cuts and ducks beneath speech. The contact sound is editorial sonification, not the sound of molecular adsorption. There is no stock-music licensing dependency. The selected narration is kept at its natural speed. The final AAC stream is measured after encoding; see `QC.json`.

## Science boundary

Kjær et al. (2022), *A 2-million-year-old ecosystem in Greenland uncovered by environmental DNA*, Nature, DOI **10.1038/s41586-022-05453-y**, https://www.nature.com/articles/s41586-022-05453-y . Also see the previously researched source ledger in `../feature-25d/SOURCES.md`.

Cold conditions and adsorption to mineral surfaces can contribute to preservation; this sequence does not claim all sediment DNA survives, establish a specific molecular reaction for an actual sample, recover complete genomes, show animal behaviour or promise cloning. No “oldest DNA as of 2026” claim is made.

## Reproduce

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install -r production/extinct-life/flow-proof/requirements.txt
npm install --no-save --package-lock=false --ignore-scripts playwright@1.64.1 @sparticuz/chromium@153.0.0 three@0.187.0
# Optional frame-only inspection first:
node production/extinct-life/flow-proof/render.mjs --stills
node production/extinct-life/flow-proof/render.mjs
.venv/bin/python production/extinct-life/flow-proof/finish.py
.venv/bin/python production/extinct-life/flow-proof/test_contract.py
```

The capture harness serves local Three.js modules, extracts bundled NSS libraries when needed and renders in Chromium/SwiftShader. No external runtime asset fetch is required. For software-rendering efficiency, direct camera/action frames remain 30 fps while the directional shadow map refreshes every third consecutive capture frame; direct out-of-order seeks force a fresh shadow render. Working images, renderer libraries, picture-only encode, WAVs and mix stems stay in `.cache/extinct-flow/`, excluded from Git. The durable `voice.flac` restores the narration after cache loss; no fresh voice selection is silently substituted. Source material textures are tracked. Albedo is AI-generated; the bump texture is a deterministic grayscale/autocontrast derivative, not a measured physical height field.

## Review limitations

Native shot samples and final encoded samples are inspected. The harness checks an out-of-order A/B/A seek for deterministic output. Contract tests check frame count, technical delivery and encoded-frame variation; these **do not establish cinematic quality, smooth storytelling, audience retention, or owner approval**. This environment has no verified full real-time audiovisual watch/listen. The owner should judge whether the action reads clearly and whether the edit now maintains flow **before** this direction is extended to the six-to-eight-minute film.

### Partial-render recovery used for this review

The unchanged first nine seconds of this new proof were retained from its initial coverage render. Only camera shots 4, 6 and 8 were revised; the last 15 seconds were recaptured with `render.mjs --from=270`. `resume.py head` and `resume.py join` preserve decoded pixels through lossless intermediate encodes. These helpers need their cache inputs and are not required for a fresh full render. This is not reuse of either rejected full-film master.

## Delivered verification

Final master: 24.00 s, 720 decoded video frames, 1920×1080/30 fps, 19,500,940 bytes. Encoded audio measured −16.02 LUFS / −2.06 dBTP. All five delivery-contract tests passed. Eight final encoded shot samples (1.2, 4.5, 7.5, 10.5, 13.5, 16.5, 19.5, 22.5 s) were inspected, including the native-resolution binding/contact frames. This is not a claim of a full real-time watch/listen or creative approval.
