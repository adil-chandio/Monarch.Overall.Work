# Head-turn tests — research only

Actions 42421577708 produced two 78-frame, 25 fps tests from the approved generated side keyframe. Sampled frames show that the negative-yaw version turns the face toward the camera; positive yaw turns away. This is a 2.5D portrait-animation test, not a true reconstructed 3D head. The background and shoulders remain essentially static, the face can change subtly and lacks a deliberate sinister smile or red-eye reveal. The turn must be assessed at full size and is not final footage.

Model weights/detectors and example-driver permissions must be cleared before commercial use; InsightFace weights are research-only. The user's original reference photo was not used.

## Retimed turn-and-smile test (v2)

The 96-frame, 24 fps `side-turn-v2--turn-driver.mp4` uses a synthetic, eased -40° yaw and a retimed example facial driver. Sampled frames show a turn from three-quarter view toward the camera with a slight smile near the end. It still fails the final quality gate: gaze drifts away from the camera, apparent face shape changes during rotation, hair/neck edges and facial detail are imperfect, the smile is not convincingly sinister, and the background and shoulders remain still. It does not contain the red-eye effect. A local landmark-tracked red-eye experiment put small red points over the irises, but does not solve the gaze, motion, lighting, identity, or license issues. Neither is approved final footage.

## Front-anchored test (v1)

Actions 42433693275 produced 96 frames at 24 fps from a generated neutral front portrait. The initial attempt accidentally began facing camera and turned *away* instead of toward camera. The upstream CLI defaulted to expression-friendly motion, which normalizes the initial pose; changing only the intended yaw did not change the starting direction as assumed. The shot is rejected. The next experiment explicitly selects pose-friendly mode to preserve the intended initial pose. Results and identity remain unverified, and the model is research-only.
