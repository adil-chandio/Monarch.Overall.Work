# Revision 3 — soft material sound and surface detail

The owner's priority is pleasurable, smooth, non-irritating sound and stronger visual finish. This is a quality target, not evidence that a mix can hypnotize everyone, multiply quality by a measured 3×, guarantee retention or be flawless. Full-film scope remains 7:19; the current rendering schedule is still the selected 60.97-second development excerpt.

## Sound changes actually implemented

- Removed the previous shared 72 Hz sine/noise contact recipe. Feet, water, deposited grains and leaves now have different stochastic material textures, envelopes and durations.
- Soft 35–90 ms attacks and smoothly closing tails; waveform endpoints are zero. No hard panning, ear-to-ear whispers, riser spam or sub-bass booms.
- Deposition uses one softly rolling gesture per marker cohort instead of thirty same-sounding ticks.
- Context-weighted water ambience recedes during the exposed-section explanation and returns gradually in the living world. Centre-correlated stereo ambience and near-centre equal-power placement avoid aggressive headphone switching.
- Foley receives a 70 Hz high-pass, 4.2 kHz low-pass and broad 3.2 kHz reduction. This shapes the **foley bus**, not the entire narrator track. Unchanged approved voice stays intelligible and at its approved speed/pitch.
- Narration-aware gain uses a 10 ms RMS detector, 45 ms attack and 350 ms release; interpolation avoids sample-level gain jumps. The composed music is gently EQ-shaped and smoothly ducked, not replaced by a procedural tone bed.
- Foley gain has both an audibility target and a conservative peak cap. Actual foley peak, maximum adjacent-sample step, >6 kHz energy fraction and voiced-region foley/narration ratio are measured in `SOUND-QC.json`.
- Before WAV output, measured premaster headroom can apply one uniform safety attenuation rather than silently clipping. Final AAC is decoded and checked against the unchanged loudness acceptance range and ≤−1.5 dBTP ceiling; normalization targets −2.5 dBTP for margin.

This is **original synthesized illustrative sound design**, not recorded field foley, certified binaural ASMR or a verified human listening review. Signal metrics help reject obvious defects but cannot certify personal ear comfort or artistic taste.

## Visual refinements actually implemented

- Approximate sky/angle-dependent water shading and irregular micro-normal/flow variation replace the conspicuous uniform stripe motif. Not claimed as ray-traced reflections or a calibrated water simulation.
- Wind-responsive shoreline reed meshes, with matching wind deformation in shadow depth material, add a second scale of motion without new cuts or replacing the accepted 3D style.
- Fine section-surface grain geometry follows the growing cap; micro-scale bump strength is reduced to avoid oversized bumps on tiny grains. Grain shadows below the shadow-map's resolution are disabled to reduce sparkle/flicker risk.
- Environmental-DNA tag fades out rather than snapping off before the sample-location tags. Existing foot locking, growing bands, one-way takeoff and continuous leaf contact/release remain.

## Checks and limits

`check_sound.py` covers distinct material waveforms, silent edges, finite samples, gentle gain release and safe stereo placement. Full-duration foley checks run before mastering. Native 1080p sampled frames, deterministic seeks and locked-camera subject motion are checked; shader compilation errors are now explicitly fatal rather than only console messages.

No continuous human full-AV review, professional anatomy review, measured retention/engagement or owner approval of this new revision is claimed. The complete film's environment/action variety and high-end asset finish remain unfinished. This revision is not a declaration that the full 7:19 film—or every frame of it—is completed or “cinema quality.”
