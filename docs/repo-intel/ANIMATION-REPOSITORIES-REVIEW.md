# Animation repositories: application to the celebrity POV

Scope: reviewed the eight unique repositories supplied by the user (React Bits was listed twice), their READMEs and selected source/examples and license files. This is a targeted technical review, **not** a claim to have studied every file or a demonstration of a finished video. No third-party code or visual assets from these repositories were copied into our project.

| Project | What it contributes | How to apply / limitation |
|---|---|---|
| [3b1b/manim](https://github.com/3b1b/manim) | Explicit scenes, transforms and interpolation; its `Transform` source separates start and target states. | Useful model for reproducible action beats and explanatory overlays, not a substitute for character performance or realistic sets. MIT. |
| [animate.css](https://github.com/animate-css/animate.css) | Named entrance/exit animations, reusable timing and reduced-motion handling. | Could inspire restrained title entrances, not scene or body movement; README says Hippocratic License, so review terms before reuse rather than assuming MIT. |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | [Production skill](https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/SKILL.md) specifies paused/seekable timeline, composition timing, frame-by-frame rendering and a check/preview/render workflow. | Take the deterministic-timeline and shot-review principles; optional future overlay compositing must not replace fully rendered environments. Apache-2.0. No CLI installed or run in this experiment. |
| [LeetCodeAnimation](https://github.com/MisterBooo/LeetCodeAnimation) | Explanatory animation, step/rewind/speed control as described in README. | Idea: inspect actions at key poses and subframe boundaries; not a 3D character animation engine. GitHub license API returned 404; do not copy assets/code without clear permission. |
| [Anime.js](https://github.com/juliangarnier/anime) | Lightweight timeline and interpolation library. | Useful for layered motion graphics and predictable timing, not a source of football actions. MIT. |
| [Motion](https://github.com/motiondivision/motion) | JS/React/Vue animation, easing and motion design. | Useful for restrained, responsive typography and easing experiments, not skeletal performance. MIT. |
| [Three.js](https://github.com/mrdoob/three.js) | Real 3D scenes, cameras, GLTF rigs; [skinning-blending example](https://github.com/mrdoob/three.js/blob/dev/examples/webgl_animation_skinning_blending.html) crossfades idle/walk/run actions via an animation mixer. | The immediate technical gap is sequencing and blending actual skeletal actions. Blender NLA can express a similar concept without converting all sets to WebGL. Example model itself is from Mixamo; do not assume its rights are MIT just because the engine is. Three.js code is MIT. |
| [React Bits](https://github.com/DavidHDev/react-bits) | Text animation, visual components and effects. | Reference for selective kinetic type; avoid decorative effects that distract from story. Repository license is MIT + Commons Clause with restrictions on redistributing components/tools/exports; inspect actual license before use. |

## Applied experiment

`showreel/celebrity_3d/action_timeline.py` introduces explicit timed skeletal clips, blends, optional looping, validation, and deterministic frame seeking in Blender NLA. `render_rigged.py --experimental-sequences` opts into idle, pickup, jog, interaction and formal walking clips rather than one unchanged action per hero. The generic CC0 mannequin and actions were already present; these repositories did not supply a new character or mocap.

Tests evaluated the imported real armature in Blender: invalid schedules rejected, sampled bone poses differ, and seeking the same frame out of order produces the same pose. A 24-frame render of 19–20 seconds at 180×320, one sample, completed technically. This is **not** visual proof of convincing performance and is not a replacement pilot. The timeline does not yet solve foot contact, positional pathing, ball contact, action intent, recognizable character, expression, detailed sets, proper first-person POV or final audio QC. In particular, `Interact_Rig` is not a kick. Do not describe the old or experimental output as premium or publication-ready.

## Next production gates

1. Shot-by-shot beat and blocking: what the character physically does, where camera is, contact frame, anticipation and follow-through, background activity, sound cue.
2. Obtain properly licensed football-specific motion and a character suitable for the intended visual style; retarget and check bone/foot contact. Design facial and hand action where visible.
3. Animate object interaction and locomotion together; sync SFX at contact rather than moving a ball independently.
4. Render a short representative action in the real environment, inspect every frame around transitions/contact plus continuous playback, then build remaining shots. Do not extrapolate quality from deterministic or technical tests.
5. Full sequence, narration/music/SFX mix, visual and listening QC, and GitHub download delivery only after the work is genuinely ready. Fictional story; no claim to an actual private routine or celebrity endorsement.
