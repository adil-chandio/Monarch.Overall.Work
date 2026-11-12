# Celebrity 3D preview — reconstruction

This is a **new reconstruction**, not the missing earlier Blender preview. It
retells the same 60-second celebrity story, using the exact ten takes and
script timings from `../celebrity_story_3d_v6/`. All visible backgrounds,
characters, furniture and props are 3D geometry rendered by PyBullet's software
TinyRenderer. The articulated characters walk, reach, wave and move props. A
small synthesized score, foley and estimated clause-level captions accompany
the original narration.

The rebuild is a basic, low-resolution (320×568, 24 fps) **preview**, not a
polished replacement or a match for the lost film. It has simplified joints,
fingers, facial acting, materials and lighting. Caption transitions are pause
estimates. Selected frames and automated tests were checked; continuous
playback and listening still need human review.

## Reproduce

```sh
python3 -m venv ~/.venv/celebrity-recovery
~/.venv/celebrity-recovery/bin/pip install pybullet==3.2.7 'numpy>=2,<3' Pillow imageio-ffmpeg
~/.venv/celebrity-recovery/bin/python -m unittest discover -s showreel/celebrity_recovery_3d/tests -v
~/.venv/celebrity-recovery/bin/python showreel/celebrity_recovery_3d/render.py \
  --out deliverables/celebrity-rebuilt-3d-preview.mp4
```

The render streams raw video directly into ffmpeg, so it does not create a large
PNG sequence. Intermediate media is temporary; the finished MP4 is gitignored
and should be published as a GitHub release asset. `--stills 3,14,26,42,48,56`
renders selected review frames under `/home/user/celebrity-recovery-stills/`.
