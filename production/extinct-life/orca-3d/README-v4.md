# v4 — rebuilt animal, fixed optics

Delivered: https://drive.google.com/file/d/1IqiBAO2k3z0DmO8I8g5XzsGFEc3-TcBn/view

| | |
| --- | --- |
| file | `Why-Orcas-Fear-Humpbacks-3D-v4-60s-720p.mp4` |
| size | 17,906,026 B |
| duration | 60.00 s |
| video | 1280x720, 30 fps, h264 High, yuv420p |
| audio | AAC LC, 48 kHz, stereo, 192 kb/s |
| sha256 | `d8f7499bd5e9b6341b761b181b960b1d11b509fc6e5edfb8b5f7a9488f8d351f` |
| audio gates | 9/9 PASS (profile `web`, I -14.1 LUFS) |
| Drive id | `1IqiBAO2k3z0DmO8I8g5XzsGFEc3-TcBn` |
| permission | `anyone / reader`, discovery on |

## Why v3 looked wrong

Not taste. Two arithmetic bugs in the depth path, both silent.

**`linear_depth()` inverted a different projection than `draw()` used.**
`perspective()` sets `w=+z` and stores `d=(z-near)/(z*(far-near))` with `far=200`.
`linear_depth()` applied the OpenGL `[-1,1]` inverse with hard-coded `0.05/400`.
Measured: a body 10 m away reported **0.100 m** — off by 100x, in every frame.

Every post effect reads that number. Fog keyed on it and reached ~0.90 on every
pixel, which is why all eight sampled frames had a **median luminance of exactly
0.098** — the background had no gradient at all. The CoC keyed on it too, so
`|z-focus|` saturated and the whole film took the widest blur kernel.

**`depth_of_field()` was a switch, not a lens.** `coc = clip(|z-focus|/focus *
strength, 0, 1)` hits 1.0 at twice the focus distance, and subjects sit at 10-30 m.
Setting `focus=1.0` and `focus=9.0` produced **byte-identical** output.

Now the thin-lens relation `c = A*f*|z-s|/(z*(s-f))`, clamped and applied as a
4-rung blur ladder. Focused vs defocused differ by **1.59x** in measured sharpness.

Fog recalibrated `L=13 m -> L=34 m`: a 10 m subject went from 43% fogged to 25%.

## Why the animal looked wrong

The ring table rounded the snout to a point and peaked the section at 0.86x0.72,
so the orca rendered as a pointed ellipsoid. Then:

- **two scale factors** were mixed, putting the dorsal fin at 2.65 m on an 8 m body
- markings were **shaded from the hull's albedo**, so 0.93 white rendered at 0.42
- the eye patch was built at the **cheek** angle, identical spans on both flanks,
  so it wrapped across the throat and read as a black hole under the jaw
- the belly ran to the **muzzle**, painting the face white and the chin dark
- `radius_at()` **snapped** to the row below instead of interpolating; a point at
  z=+2.27 got the radius for z=+2.0 and sat 4 cm **inside** the hull — buried, not
  mis-shaded, which is exactly what a black blob is
- the travelling wave normalised by each mesh's own z extent, and the patch's is
  shorter than the body's, so the same world z got two amplitudes and slipped
  **0.069 m**

All of it is now expressed as a fraction of `length_m` against one profile table,
and `scripts/tests/test_optics.py` pins the two optics invariants.

## Shot fixes

- **trophic pyramid** was four stacked slabs. Now four truncated pyramids, krill at
  the base, each tier flaring into the one below.
- **carousel** put six 8 m animals on a 5.8 m ring, so the flukes reached past their
  spacing and the pod drew a six-armed cross. Five animals on a 16 m ring now.
- **sonar** was near-black: focus 3.2 clipped the CoC at 6 m and the fog ate the
  rest. Focus 2.6, strength 1.6, deep-shot light rig.
- **pec-slap** is a humpback slapping with its 5 m pectoral, and it was drawing an
  **orca** plus a bare `flipper()` plate — a small black dolphin beside a white
  plank. The humpback mesh already carries its own pectoral.
- **contact shadow** ran after the post stack, so it darkened open water beside the
  animals and landed off the bottom of frame. It is now multiplied into the
  render buffer, behind the subject only.
