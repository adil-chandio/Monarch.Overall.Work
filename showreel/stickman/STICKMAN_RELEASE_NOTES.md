A stick figure that is a rig, not a drawing of one.

What this is
------------

One figure, five shots, one continuous piece of business: walk, stop, look back,
run, jump, land, walk out. Thirteen seconds, 320 frames, 24 fps, 1080x1920.

| file | what it is |
| --- | --- |
| monarch-stickman-1080x1920.mp4 | master, 13.33 s, 1080x1920, 24 fps |
| monarch-stickman-preview.mp4 | same cut at 540x960, small enough to scrub in a browser |

Why a stick figure
------------------

Because it can actually be animated. The previous cut in this repository was
built from painted poses, and its ceiling was that there were six of them and no
side view of an elbow — so the only honest thing it could do was cut between held
images. A stick figure has no painted surface to interpolate. That means an
inverse-kinematics solve has nothing to ghost, and the ceiling moves from "what an
artist happened to paint" to "whatever four bones can reach."

That limit is honest and visible in the poses themselves.

What is actually solved
-----------------------

Feet are pinned in world space. During stance a foot holds a fixed world
position, so the contact cannot slide; the swing foot is a cubic Hermite whose
end slopes match the stance velocity, so there is no hitch at the hand-off.
Verified at 2.3e-13 px of drift over four cycles.

Stride is bounded by contact geometry. To take a long step the leg has to bend,
and the only way to bend it is to stand lower, so `Gait.max_stride` solves the
reach triangle for a given hip height. The walk uses 0.53 of figure height
because anything longer over-extends the leg at touchdown.

Flight time follows the apex. For a rise h under gravity g, launch speed is
sqrt(2gh) and the full flight is 2*sqrt(2h/g). Choosing a flight time and hoping
the apex looked right produced a hop; deriving it produces a jump.

Everything that gets knocked settles. Stops, landings and impacts are damped
oscillators that overshoot and recover, which is what makes the figure read as
having mass rather than as being eased between keyframes.

The world is a function of the camera. The backdrop is redrawn every frame — sky
gradient, three ridge layers with aerial perspective, a floor plane with marks
spaced uniformly in world depth. One projection serves the scenery and the
figure, so a push-in separates the layers for the reason real parallax does.

What this is not
----------------

- One figure, one camera. No dialogue, no background action, no story beyond a
  walk, a look and a jump.
- No face. Expression is carried by silhouette, timing and where the single eye
  dot points.
- Constant limb thickness. There is near/far separation and a rim light, but no
  real cel-shaded volume.
