# Research-only portrait motion feasibility test

This directory contains two **3.12-second test clips**, not a finished film or a complete character pilot. They animate the previously generated `shot-05a.jpg` and `shot-05b.jpg`; the user's original reference photo was not used in this test or uploaded.

The pipeline used the LivePortrait official repository at `9b294b3d0536135442ea73cb01e6cb3ca7029dd3`, with its supplied `d0.mp4` example motion as a driver. Both clips are 78 frames at 25 fps, 1280×714. This output dimension does not mean the face was generated at that resolution; LivePortrait uses a low-resolution crop and pastes the result back into the source frame.

## Inspection and limitations

- Some expression and gaze animation is visible; the face does not exhibit the abrupt whole-head replacement seen in the earlier WAN close-up over the six sampled frames. This is not a guarantee of identity fidelity or glitch-free playback.
- The side take stays mostly side-on: it **does not perform the required full turn to camera**. The smiles are broader than the intended controlled sinister smile. The front take starts with red eyes already present in the source image, rather than showing the effect appear during the shot. The background and body are essentially static; neither clip is a full moving scene.
- These tests do not validate walk, run, feet, cloth physics, camera tracking, scene consistency, or the complete 20-second sequence. They must not be substituted for the requested video.
- LivePortrait code/weights carry an MIT license, but its standard InsightFace models are licensed for **non-commercial research only**; see the upstream `LICENSE`. These clips are research tests and are **not cleared for commercial use**. Check the licenses/permissions of driver footage, other weights and assets separately before any publication or production usage.
- Neither test is a rigged 3D character. No face reconstruction was performed and no full-scene GPU/CPU render was produced.

The test is reproducible through `make_liveportrait_pilot.py`, `liveportrait_kernel.py`, and `run_liveportrait_pilot.sh`, with a Kaggle GPU environment. Receipts are in `liveportrait-receipts.json`. The original Actions generation run was `42405635576`; a separate Actions recovery copied the resulting test clips to this branch for inspection.
