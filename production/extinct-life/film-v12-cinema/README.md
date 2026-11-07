# V12 — authorized enhancement of the enjoyed POV opening

Owner said “Bhai Maza Aya” about V11 and requested a more cinematic, lively, realistic, engaging next iteration. **V11 remains intact**, along with V9/V10. This is the same sentence-complete **61-second opening experiment**, not a replacement full seven-minute master. Original English voice-02, script hash and sample/chapter timing preserved. 1920×1080, 30fps, 1,830 native frames.

## Concrete enhancements, not engagement promises

- Atmospheric procedural sky, environment illumination, contact AO and final antialiasing; no new picture plates.
- Original black-suit slim investigator/POV retained; less blocky cuff treatment, finger/knuckle/nail detail and tool-to-pouch posing revised.
- Sample grains have an analytic gravity → impact → bounded bounce → rest sequence. Tests cover continuity, limits and deterministic seeking, not validated granular physics.
- A hinged/flexible report page changes the reading action; a hand-held lens adds a different interpretation action.
- Per-instance foliage wind, stream channel with gravel margins, leaf litter/ripples, airborne indoor motes and environment material reflections/contact shading.
- Conceptual reindeer/goose behaviours and a short bird flyby add living-world/scale beats. A tiny leaf beetle is illustrative detail, not a claimed identified ancient species. These are new staged actions, not copied reference choreography.
- Revised soft grain, paper, wing/water foley and subtle procedural stereo air beneath the unchanged narration and licensed Hiraeth excerpt. No loudness-density or ASMR effectiveness guarantee.

The look remains stylized 3D, not photoreal footage, an exact portrait, recovered appearance/co-occurrence or a physically validated simulation. No claim that every frame guarantees retention, hypnosis, virality, audience geography/RPM, algorithm ownership or reference parity. Those aspirations are not measurable production guarantees.

## Files / verification

`scene.mjs` retains the multi-space POV foundation. `cinema.mjs` is the original rendering/action enhancement layer; `kinematics.mjs` and `kinematics.test.mjs` define/test analytic grain motion. `animals.mjs` loads earlier original production mastodon/reindeer/goose meshes; old source files and all old rendered movies remain untouched. `ASSET-PROVENANCE.json` records hashes and keeps the owner's original portrait sheet private. Two old clay material maps are used on real 3D surfaces (not scene/image plates); the albedo was originally AI-generated, and the derived bump map is not measured displacement. See `CREDITS.md` for attribution/science/review limitations.

`render.mjs` checks native visibility/limb lengths, deterministic absolute seek and actual hand/object movement with a frozen camera. Twelve exact contiguous frame ranges are rendered in parallel. `finish.py` checks range coverage, full output decode/frame count and final delivered audio levels. Workflow `.github/workflows/extinct-cinema-minute.yml` publishes an actual MP4, original captions, credits and technical reports as a GitHub prerelease for owner creative review, not YouTube. Large movies/source music are not committed to Git.

```sh
# At repository root with workflow-pinned dependencies installed:
.venv/bin/python production/extinct-life/film-v12-cinema/finish.py
node production/extinct-life/film-v12-cinema/kinematics.test.mjs
node production/extinct-life/film-v12-cinema/render.mjs --stills
.venv/bin/python -m unittest discover -s tests -p 'test_extinct_cinema_minute.py' -v
node production/extinct-life/film-v12-cinema/render.mjs --serve --port=4192
# Part i in [0,11]: --from=floor(1830*i/12) --to=floor(1830*(i+1)/12)
.venv/bin/python production/extinct-life/film-v12-cinema/finish.py --assemble
```

Official score download runs on GitHub Actions; `--voice-only` is a local development fallback, not the release soundtrack. `DELIVERY.json`, `QC.json`, `AUDIO-QC.json`, `seek-QC.json` and `inspection/` are generated from actual jobs. Sample/native/technical inspection is not uninterrupted human audiovisual review or owner creative acceptance.
