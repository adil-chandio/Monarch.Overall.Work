# V11 — approved POV / life-scale world experiment

**Owner authorization:** after reviewing the one-minute structure, “Isko or bhi next level lejake or enhance improve Karke banao.” No additional approval gate was introduced. V9 and V10 remain unchanged.

## Scope and creative change

61 seconds to finish the original approved English sentence, not retime the narration. 1920×1080, 30fps, 1,830 native frames. The new film leaves the single display-platform setup: an observer approaches a sediment bank, handles sample/tools, enters an explicitly enlarged DNA explanation, walks/looks across a polar landscape and conceptual past, handles a research report and leaf at a full-room workbench, compares evidence, then observes living wildlife and a falling/caught leaf in woodland. Returns have different purposes (published source → plant/sample inspection → interpretation), not an orbit of the same cube.

The black-suit, open-collar, dark-haired slim investigator is owner-sheet-inspired and stylized, not a photographic replica. A short over-shoulder establishment transitions to predominantly first-person camera/hand staging. There are five distinct 3D worlds and eight timed narrative sections; scientific visualization is not falsely labeled literal human eyesight.

## Implementation and reproduction

- `scene.mjs`: deterministic absolute-time terrain/room/hand/prop/environment animation; fixed-length two-bone arms; original procedural investigator; native movement and spatial camera travel. Distinct microscope-scale explanatory set. Camera pose is independently freezeable for motion QC.
- `animals.mjs`: V9 original mesh loader/deformation adapted to the mastodon only; per-frame foot-state calculations cached rather than redundantly evaluated per vertex. The original V9 files are not modified.
- `render.mjs`: native capture, visible-picture/limb guards, deterministic seek and camera-frozen motion checks; six exact 305-frame shards. Uses existing original mastodon geometry and two existing material maps, not previous rendered movie frames or scene images.
- `finish.py`: verified original voice assets/slot padding, licensed Hiraeth, synthesized action-specific low-level foley/air, mix normalization, full native frame-count decode and delivered audio statistics.
- `schedule.json`, `English.srt`: original script hash/voice-02/timing retained; only the opening is excerpted. Caption 18 completes at 60.743s; the next sentence is outside this experiment.
- `CREDITS.md`, `ASSET-PROVENANCE.json`: references/licensing and honest conceptual/realism/review limits. The owner's original portrait sheet is not published.
- Delivery workflow: `.github/workflows/extinct-pov-minute.yml`; large movie/music remain outside Git. Publishes a GitHub prerelease, not YouTube. `DELIVERY.json`, `QC.json`, `AUDIO-QC.json`, `seek-QC.json`, `inspection/` are created by actual production jobs, not fabricated beforehand.

From repository root, with workflow-pinned dependencies installed:

```sh
.venv/bin/python production/extinct-life/film-v11-pov/finish.py
node production/extinct-life/film-v11-pov/render.mjs --stills
.venv/bin/python -m unittest discover -s tests -p 'test_extinct_pov_minute.py' -v
node production/extinct-life/film-v11-pov/render.mjs --serve --port=4191
# Render ranges [0,305), [305,610), [610,915), [915,1220), [1220,1525), [1525,1830).
.venv/bin/python production/extinct-life/film-v11-pov/finish.py --assemble
```

The official music download is reachable on GitHub Actions; local network restrictions may require `--voice-only` for development preview. Such a preview is not the final scored release. A native render/decode and sampled image inspection are not uninterrupted human audiovisual review or creative acceptance.
