# Genetics recut — experimental work, not a finished documentary

This recuts the earlier 29.77-second evidence test in response to the feedback that the DNA shot remained on screen too long. The 2017 comparison is introduced with several shorter lab framings; the previous almost-ten-second DNA shot is replaced with a three-second helix view, a conceptual fragment-removal animation with a second camera angle, and a simplified translation/stop-signal image. The example mRNA triplet UAA is a stop codon; the letters are invented and are **not** the mammoth's actual sequence. A deletion is illustrated by removing a fragment; this is not a literal molecular simulation of how a deletion occurs. The lab equipment and labels are illustrative reconstructions, not records of the actual laboratory or containers.

This is still a **stylized test**. Shorter shots do not by themselves make the visual storytelling premium or ensure audience retention. Much of the first 20 seconds is still the same simple laboratory and props from different angles; the simplified molecular visuals are not photorealistic. No believable mammoth performance is included. The full documentary, quality art, cinematography, physics, score, sound design, human listening/review, and the majority of the film's scenes remain unfinished. The automatic captions and voice have not had full human review. There is no music or SFX in this test; the earlier rejected mechanical-sounding background has not been reused.

`deliverables/Last-Mammoths-Genetics-3D-Recut-Test.mp4` preserves the previous test separately and uses the same first 29.77 seconds of the draft `03-genome.mp3`, at its generated speed. The narration is an adapted science-qualified script, not a verbatim reading of the original research draft. The complete narration is not rendered here. No YouTube publication was authorised.

## Reproduce / verify

From the repository root, with Three.js, Playwright, Sparticuz Chromium, Python and imageio-ffmpeg installed:

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/genetics-recut/render.mjs --verify
node production/extinct-life/longform-mammoth/cinematic-rebuild/genetics-recut/render.mjs --stills
node production/extinct-life/longform-mammoth/cinematic-rebuild/genetics-recut/render.mjs
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/genetics-recut/finish.py
```

The renderer makes 893 individually rendered frames at 1280×720/30 fps and writes scratch files in `.cache/mammoth-genetics-recut`. `--verify` checks deterministic seeking, scan-carriage movement, molecular shot changes, and movement of the removed fragment. The finishing script refuses a plate when the scene or stage hash changed after rendering, and checks decoding and peak level. These checks do not verify quality, retention, listening experience, or scientific accuracy; visual and expert review remain necessary.
