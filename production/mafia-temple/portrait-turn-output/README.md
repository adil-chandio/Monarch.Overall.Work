# Head-turn tests — research only

Actions 42421577708 produced two 78-frame, 25 fps tests from the approved generated side keyframe. Sampled frames show that the negative-yaw version turns the face toward the camera; positive yaw turns away. This is a 2.5D portrait-animation test, not a true reconstructed 3D head. The background and shoulders remain essentially static, the face can change subtly and lacks a deliberate sinister smile or red-eye reveal. The turn must be assessed at full size and is not final footage.

Model weights/detectors and example-driver permissions must be cleared before commercial use; InsightFace weights are research-only. The user's original reference photo was not used.

## Retimed turn-and-smile test (v2)

The 96-frame, 24 fps `side-turn-v2--turn-driver.mp4` uses a synthetic, eased -40° yaw and a retimed example facial driver. Sampled frames show a turn from three-quarter view toward the camera with a slight smile near the end. It still fails the final quality gate: gaze drifts away from the camera, apparent face shape changes during rotation, hair/neck edges and facial detail are imperfect, the smile is not convincingly sinister, and the background and shoulders remain still. It does not contain the red-eye effect. A local landmark-tracked red-eye experiment put small red points over the irises, but does not solve the gaze, motion, lighting, identity, or license issues. Neither is approved final footage.

## Front-anchored test (v1)

Actions 42433693275 produced 96 frames at 24 fps from a generated neutral front portrait. The initial attempt accidentally began facing camera and turned *away* instead of toward camera. The upstream CLI defaulted to expression-friendly motion, which normalizes the initial pose; changing only the intended yaw did not change the starting direction as assumed. The shot is rejected. The next experiment explicitly selects pose-friendly mode to preserve the intended initial pose. Results and identity remain unverified, and the model is research-only.

## Front-anchored test (v2)

Actions 42434301418 rendered 96 frames at 24 fps with pose-friendly mode. The inspected frames show a leftward three-quarter view turning toward the lens, with a small late smile and much steadier direct gaze. It is a meaningful improvement over v1, but the generated portrait is still only an approximate likeness, the expression has subtle mouth/teeth distortion, the body and background are static, and no red-eye effect is included. Intermediate-frame identity and warp artifacts need further inspection; this is research-only, not a final shot or a commercial-clearance claim.

A local tracked-iris red-eye test was applied to front-turn v2 with `research_eye_vfx.py`. Iris detection succeeded through the 96 frames, and all 36 frames around the effect ramp were examined as cropped eye images. The red tint followed the eyes in those crops, but it reads more like red contacts than convincing emitted light; no full shot, blink, audio or final color-grade review has been performed. It remains a research test.
