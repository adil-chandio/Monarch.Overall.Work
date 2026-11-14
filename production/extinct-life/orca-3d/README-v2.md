# Orca 3D — v2 (skill-gated build)

60 s / 720p30 / −14 LUFS. This is the version that is measured against the repo's
own gates rather than eyeballed.

## What changed from v1

v1 shipped with a master that measured **−12.7 dBFS RMS with 19 clipped samples**
and no gate run. It looked finished and was not. v2 is built to
`skills/monarch-video-lab/*` and passes every check those skills define.

### Audio

Built by `scripts/orca3d-audio.py`, which imports the repo's own DSP engine
(`showreel/build_audio_60fps.py`) instead of re-implementing filters — that file
is the one that produced the v3 showreel at −14.0 LUFS. Reusing it is the
`sfx-library` rule: a cue is defined once, in the library.

New voices the film needed, all built from that engine's primitives:
`whale_moan`, `sonar_ping`, `krill_shimmer`, `bubble_rise`, `tension_bed`,
`ocean_grain`, `heartbeat`, `film_tick`, `spectral_riser`.

44 cues, every one frame-locked at 30 fps, every one tied to a cut in the picture.

### Defects found and fixed by measurement, not by taste

| Defect | How it was caught | Cause | Fix |
|---|---|---|---|
| 19 clipped samples | `ebur128=peak=true` on the shipped file | `tanh` used as a limiter | look-ahead peak limiter, gain reduction only |
| 5 click runs at 19.44 s | `showreel.audio_qc.gates` | riser filtered in 512-sample chunks; biquad state reset each block | overlap-add spectral sweep |
| riser peaked 0.88 s after its boom | cue-sheet sync check | riser placed by its *start* time | riser is defined by the impact it ends on |
| clicks at the riser top | gate | 6.8 kHz sweep = half a cycle per sample = a click train | cap the sweep at 3.4 kHz |
| clicks at the riser tail | gate | `env[-14 ms:] = 0` is a step edge | fade the tail, don't truncate it |
| harsh +5.2 dB over high-mid | gate `not_harsh` | showreel's vocal presence EQ copied onto whale song | re-derived from the gap table |
| 24/44 cues off the frame grid | sync check | placement via float seconds | place by sample index from the frame number |
| riser fired 3.2 s before anything happened | sync check | wrong cue family for a climb beat | riser spans the climb and lands on the boom |
| clicks in the 15–19 s window | gate | krill = 2.6–7 kHz noise | moved to 0.9–3.2 kHz, top rolled off |

### Numbers

Gate (`python -m showreel.audio_qc.gates <file> --profile web`) — **PASS on all 9**:
`loudness_in_range · true_peak_ok · lra_in_range · no_clipping · no_clicks ·
mono_compatible · dc_offset_ok · not_harsh · has_dynamics`

Against the shipped showreel master (`... .compare ... --sections 6`), all eight
bands inside ±2.1 dB:

```
sub -0.13   bass -0.99   low_mid +1.79   mid -0.84
high_mid +1.15   presence +1.37   harsh +1.34   air  in range
```

### Visual

| Defect | Cause | Fix |
|---|---|---|
| orca rendered **pure black — no white markings at all** | `Mesh.copy()` dropped `.patches` and `.two_sided`, so `travelling_wave_mesh()` returned a body with no markings and `draw_orca()` found `None` | carry both attributes through `copy()`; deform the patches with the same wave |
| markings were a white barrel over the whole body | two angle ranges covering most of the circumference | redrawn to orca anatomy: eye patch, saddle behind the dorsal, chin/belly only |
| markings the same value as the body | patch shell shaded as skin | patches shaded as diffuse scatterers |
| particles read as falling snow | 0.6–3.2 px hard dots, opacity independent of depth | marine snow: depth-scaled radius and alpha, whole layer defocused |
| god rays read as flat bars | constant fill, blurred — no falloff in any axis | exponential depth falloff, spread with descent, ragged surface breakup, horizontal falloff |

## Shots rebuilt

Three beats were rendering body parts with no animal attached — the exact
"impossible floating geometry" problem that makes a render read as cheap:

| Beat | Was | Now |
|---|---|---|
| 31.40–35.60 flippers | seven detached blades in a row = a white picket fence | **pec-slap**: two humpbacks at the surface hammering the water, fins attached, spray thrown |
| 35.60–39.20 wheel | eight flippers rotating on a ring, no whale anywhere | **carousel feeding**: the pod circles a bait ball and closes, every animal banking into the turn |
| 18.60–22.40 species card | camera at the whale's nose, so 14 m foreshortened to a stick with a detached fluke | three-quarter profile, whole animal in frame |
| 27.64–31.40 sonar | 2 px arc stroked onto the frame, reading as a lens scratch | soft expanding wavefront with core + skirts, blurred |

All four are behaviours humpbacks actually perform, so the shots now carry
information as well as looking correct.

## Delivered

Drive `1pzeP4jT_hMZ4tDkQespCcB1Wb94qgY-g` · 18,770,687 B · 60.00 s · 720p30 ·
stereo 48 k · sha256 `4acf8f58…1b4c04`

## Reproduce

```bash
.venv/bin/python scripts/orca3d-audio.py --out /tmp/orca-master.wav
.venv/bin/python -m showreel.audio_qc.gates /tmp/orca-master.wav --profile web
.venv/bin/python -m showreel.audio_qc.compare \
    public/showreel/audio_master_60fps.m4a /tmp/orca-master.wav --sections 6
.venv/bin/python scripts/orca3d-film.py --out /tmp/v2/seg --from 0 --to 60
```

The audio script also enforces the cue-sheet rules at build time and refuses to
render a sheet that breaks them: no two impacts within 400 ms, no two cues within
8 frames, and no cue that is not on a frame.
