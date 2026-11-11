A stick figure that is a rig, not a drawing of one.

The film
--------

One figure, one chasm, four shots, eleven and a half seconds:

  1. alone    -- standing back from the edge, breathing, then a head turn. The
                 camera dollies right so the gap creeps into frame before the
                 character admits it is there.
  2. coil     -- two strides to the lip, then a squat that holds. The lens pulls
                 back as the figure goes down, because a crouched figure is
                 short and a push-in would crop the feet that have to sit on the
                 edge.
  3. jump     -- anticipation, launch, flight, landing. The camera opens through
                 the arc so the far lip stays in shot and the ground reads as
                 coming up to meet the figure.
  4. after    -- a look back across the gap, then a walk away. The camera trails
                 at 0.86 of the figure's speed so it falls behind instead of
                 chasing.

| file | what it is |
| --- | --- |
| monarch-stickman-1080x1920.mp4 | master, 11.54 s, 1080x1920, 24 fps, 277 frames |
| monarch-stickman-preview.mp4 | same cut at 540x960, small enough to scrub in a browser |

Why a stick figure
------------------

Because it can actually be animated. The earlier cut in this repository was
built from painted poses, and its ceiling was that there were six of them and no
side view of an elbow -- so the only honest thing it could do was cut between
held images. A stick figure has no painted surface to interpolate, so an IK solve
has nothing to ghost, and the ceiling moves from "what an artist happened to
paint" to "whatever four bones can reach."

That limit is honest and visible in the poses themselves.

What is solved rather than posed
--------------------------------

Feet are pinned in world space. During stance a foot holds a fixed world
position, so the contact cannot slide; the swing foot is a cubic Hermite whose
end slopes match the stance velocity, so there is no hitch at the hand-off.
Measured drift: 2.3e-13 px over four cycles.

Stride is bounded by contact geometry. To take a long step the leg has to bend,
and the only way to bend it is to stand lower, so `Gait.max_stride` solves the
reach triangle for the hip height and the walk uses 0.53 of figure height.

Flight time follows the apex. For a rise A under gravity g, launch speed is
sqrt(2gA) and the whole flight is 2*sqrt(2A/g). Horizontal speed is then whatever
carries the figure across the gap in exactly that time, which is why the jump
looks committed to rather than floated.

The foot is placed from its contact. A stick figure's foot is one bone; the rule
that keeps it out of the ground is that whichever end is lower sits on the
contact point. Rotating about the ankle instead -- the obvious thing to write --
drives the toe a third of a foot-length under the floor on every toe-off.

The gap is real. It is a hole in the floor plane, not a painted shadow: the
floor fill, the floor marks, the cast shadow and the dust all agree about where
the ground stops. It is drawn as a trapezoid -- narrow at the far lip, wide at
the near one -- because a deep point projects smaller, and that foreshortening is
the whole read of a hole in a floor.

Everything that gets knocked settles. Stops, landings and impacts are damped
oscillators that overshoot and recover.

Verification
------------

`python -m showreel.stickman.verify` runs sixteen assertions, including:

    stance foot world-static            2.3e-13 px
    no foot below the floor             0.0000 px
    no grounded pose floats             0.00 px
    jump apex matches the arc           419.4 measured vs 420.0
    flight time is the one gravity allows
    horizontal speed carries exactly the gap
    limbs within bone length            max 99.8%
    no foot stands over the void        0 poses
    take-off and landing on solid ground
    the arc clears the lip              closest foot over the void: -132 px

Three of those failed on their first run and all three were real bugs: the
stance test had the contact equation backwards, the floor test had the y-axis
sign inverted, and the arm had a hand target that stacked offsets past the bone
length. Those are the kind of mistake nobody can diagnose by watching the
result, which is the argument for asserting them.

What this is not
----------------

- One figure, one camera, one location. No dialogue, no second character.
- No face. Expression is carried by silhouette, timing and where the single eye
  dot points.
- Constant limb thickness along a bone. There is near/far separation and a rim
  light, but no cel-shaded volume.
- Ink is drawn with a width profile and a generated paper grain, not with a
  brush engine, so it reads as technical pen rather than as paint.
