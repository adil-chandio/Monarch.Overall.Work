# Monarch — POV: the stadium goes quiet · **second cut**

**90 s · 1080×1920 · 24 fps · 2 160 frames · stereo 48 kHz**

The first cut was six shots of seventeen seconds, one camera move each, and no
sound at all. It was honest and it was slow: the hush was carried entirely by a
crowd that stopped moving, and a viewer had nothing to listen to for a minute and
a half. This cut keeps the premise and fixes the two things that were wrong with
it — **it is cut**, and **it has a mix**.

---

## 1. The cut: six shots became ten, with nineteen camera setups

A shot is no longer one setup. The film cuts inside its own shots, on action, the
way a scene is actually edited:

| # | time | shot | setups | what it does |
|---|---|---|---|---|
| 1 | 0.0–5.0 | cold | 3 | half a second of black, an aperture, a snap in on the figure |
| 2 | 5.0–13.0 | walk | 3 | the stand towering, then the boots, then the face |
| 3 | 13.0–22.0 | warm | 3 | two touches, the second one a disaster, and his face after it |
| 4 | 22.0–31.0 | set | 3 | the ball is placed, he stands, then the eyes get a shot of their own |
| 5 | 31.0–41.5 | strike | 3 | run-up, closer, plant — contact at **37.30**, then a third of speed |
| 6 | 41.5–49.0 | roar | 3 | the net still moving, arms out, and the only pure wide in the film |
| 7 | 49.0–58.0 | replay | 1 | the same half second from behind the ball at a fifth of speed |
| 8 | 58.0–72.0 | turn | 5 | he turns into the lens, winks, and puts a finger to his lips |
| 9 | 72.0–82.0 | walk-off | 1 | no cut for ten seconds — he comes at the lens until it closes |
| 10 | 82.0–90.0 | card | 1 | black, and one question |

Two of the ten are deliberately uncut (the replay and the walk-off). Everything
else is two or three setups, because after eleven cuts in seventy seconds the last
thing the film should do is stop moving the camera.

**Framing is solved, not eyeballed.** `_eye_for_row()` inverts the projection to
put a named row — a head at 42 % of the frame, a ball at 70 % — at that row, for
whatever zoom the setup is using. The first assembly of this cut picked camera
heights by hand and every tight setup framed the head at a third of the frame with
the ankles cut off; the fix was to stop guessing and solve the one number the
projection already knew.

---

## 2. The sound: 90 seconds, synthesised from the film's own state

`pov_audio.py`. There is no library and no licence: a crowd is noise with a
spectrum, an impact is a low sweep plus a crack, and a stadium that goes quiet is
the same crowd with the gain taken away and a room left behind.

**Nothing is triggered by a clock.** The mix walks the film at 200 Hz and takes
what it needs from `Pov.state`: the crowd's gain *is* `churn` (the same number that
moves the stand in the picture), the footsteps are found by watching ankles arrive
at the ground plane, and the impact is the frame the ball's story clock starts. The
build reports 18 000 tracked states and **64 footfalls** found — not placed.

```
 0.0 –  7.9   crowd, muffled by the tunnel, and getting louder   -13.4 dBFS
 7.9         sub drop, one swish: the room empties                -18.9
 9.0 – 31.0   room tone, a heartbeat at 58 → 110 bpm, boots       -28.4
31.0 – 37.3   the run-up, a riser, breath                        -29.1
37.30        the boot, the crack, the thump (onset 37.298)        —
37.3 – 41.5   the ball in the air and the net, over silence      -29.3
41.5 – 49.0   the roar, a whistle, the stand letting go          -10.3
49.0 – 58.0   the replay: ducked, muffled, wobbling like tape    -19.7
58.0 – 72.0   the crowd, then one finger takes it down           -11.2
72.0 – 82.0   the roar again                                      -10.9
82.0 – 90.0   the tunnel, then only distance                     -29.5
```

Three decisions worth naming:

**The silence is not silence.** `churn` is zero for twenty-nine seconds and a
digital zero there sounds like a broken file. What is left is room tone at -46 dB
plus what you can actually hear in a stadium that has stopped: a heart, boots, a
ball being set down.

**The roar arrives late.** Contact is at 37.30; the crowd does not come back until
41.50. The ball hits in the quiet, the net swishes in the quiet, and only then does
the room let go. Bringing the noise in on contact throws away the four seconds the
whole film is built to reach.

**The replay is not the same sound.** It is the same event heard through a
broadcast: the crowd ducked under it, the impact muffled, and a slow pitch wobble
on everything, because a replay is tape.

---

## 3. The face now has a wink

`Face.wink` closes the near eye only, through the same eyelid-arc branch a blink
uses, so a wink is one eye shutting rather than both eyes scrunching. It is the
only authored motion in the film: there is no physics in eyelids, and a solve would
be a model of a face rather than a face.

The acting is otherwise unchanged in kind and larger in amount: `F.FEAR.blended(F.SHOCK)`
on the bad touch, `F.DISDAIN` after it, `F.GRIT` planted, `F.SHOCK → F.JOY` on the
roar, `F.BREATH` coming down, `F.DIRECT` with a wink, then a smirk.

---

## 4. Camera language

* **Snap cuts**: nineteen setups over ninety seconds, most of them under four.
* **Shake**: a decaying sine for a third of a second after contact — not noise,
  because noise on a locked-off frame reads as damage.
* **Flash**: two frames of white at contact, at 78 % — a full white-out hides the
  frame it is selling.
* **Speed ramps**: the strike runs at a third of speed after contact; the replay
  runs the same half second at a fifth. The rig is solved at true gravity inside
  the warp, so the ball is slow rather than floaty.
* **Replay grade**: a 12 % desaturation and a vignette, applied in the post pass,
  the way a broadcast packages a replay.

---

## 5. The measurements

`python -m showreel.stickman.verify_pov` — **32 assertions, all pass**

```
PASS  timeline: shots tile the film with no gap or overlap     10 shots, 90.0 s
PASS  timeline: no shot is shorter than four seconds           shortest 5.0 s
PASS  timeline: the film is at least 30 seconds                90.0 s = 2160 frames
PASS  sound: there is a real silence in the film               41.2 s below churn 0.02
PASS  sound: the crowd comes back and stays back               min churn 43.6-48.8 s = 1.00
PASS  sound: he can shut the crowd up with one finger          churn at 69.5 s = 0.28
PASS  sound: and it comes straight back afterwards             churn at 72 s = 1.00
PASS  sound: the silence arrives over time, not on a cut       collapse took 0.50 s
PASS  faces: every frame has one, and no field is out of range 180 frames sampled, 0 bad
PASS  faces: a blink lasts long enough to land on frames       0.208 s = 5.0 frames
PASS  faces: the eyes close at least once                      17 frames with the eyes shut
PASS  ball: the strike's vertical acceleration is gravity      fitted 2900.0 vs 2900.0
PASS  ball: it arrives at the height the net was framed for    -385.0 vs 385.0 below ground
PASS  ball: never below the ground in flight                   lowest point -424.6
PASS  ball: the juggle's acceleration is gravity               fitted 2900.0 vs 2900.0
PASS  figure: no foot is below the floor                       lowest point 0.00 units
PASS  figure: the pelvis never jumps between frames            max step 45.4 units
PASS  keeper: stands on the goal line, behind the hero         goal at z 2.71, hero at z 1.00
PASS  keeper: exists during the strike and not before it       absent at 8.0 s, present at 35.5 s
PASS  frames: all sampled frames render in range and finite    17 frames
PASS  frames: black only where the film means black            2 deliberate black frames
PASS  light: body is separated from the background by 0.20     worst excess -0.157
PASS  text: the hook runs 0.35-5.4 and the question 82.6-90    two windows, no others
PASS  text: no card is up without 'An imagined scenario'        0 unattributed frames
PASS  text: every card has ink and clears the edges by 24 px    4 cards inside
PASS  text: the hook's shade band is denser than open sky       band 114.3 vs open 0.0
PASS  sound: the quiet is at least 12 dB under the roar        -28.4 vs -10.3 dBFS
PASS  sound: the quiet is a room, not a zero                   0.0378 rms in the silence
PASS  sound: the impact lands on the contact frame             onset 37.298s vs 37.30s
PASS  sound: nothing clips and the peak has headroom           peak 0.890, clipped 0
PASS  sound: the roar is the loudest thing in the film         loudest: 41.5-49
PASS  sound: the replay is ducked under the roar               -19.7 vs -10.3 dBFS
```

### What this cut's verifier caught before anything shipped

1. **Every shot was playing its first setup.** Shot functions receive *local*
   time; the new code compared against global times, so every `if` was true at the
   top of every shot. Six of the nineteen setups never appeared, and the stills
   showed the same three framings over and over.
2. **The close-ups framed the head at a third of the frame.** `eye` is a camera
   height, and raising the zoom pushed the head up and out. Solved with
   `_eye_for_row()`.
3. **The run-up left the hero a third of the frame away from his own action** for
   three seconds, because the camera was aimed at a fixed x instead of at him.
4. **The disclaimer trailed the hook by 0.4 s**, so ten frames carried a title
   about a real man with no caveat under it.
5. **A diving silhouette read as a black sack standing next to him** at a 2.1 zoom;
   the keeper is now out of the replay and the plant insert entirely.

---

## 6. Limits, stated plainly

**The set is a depth model, not a 3-D scene.** The goal sits behind the action
rather than beside it, which is why the strike is from about 24 m and not from the
penalty spot: at 11 m a 7.32 m goal is wider than the frame.

**One figure, one keeper, one ball.** The keeper has no face and is a silhouette
by design; the crowd is fifteen thousand marks placed once and never individuals.

**The failure beat is still the weakest moment.** The bad touch reads as a ball
squirting away rather than as a skill failing; the recovery is a single lunge.

**The mix is synthesised, not recorded.** It is honest about being a synthesis —
there is no crowd, no boot, no net in it. A recorded foley pass would beat it and
is not in this repository.

**No likeness, no number 7, no claim about a real match.** Every frame that
carries a card also carries *"An imagined scenario, not a real match."*

---

## 7. Files

| path | what it is |
|---|---|
| `pov.py` | ten shots and nineteen setups, as functions of time |
| `pov_film.py` | frame assembly: shake, flash, blank frames, the encode |
| `pov_audio.py` | the mix: crowd, feet, heart, impacts, score |
| `pov_text.py` | three cards and the replay bug |
| `pov_post.py` | text + replay grade over a finished master, then the mix |
| `verify_pov.py` | the thirty-two assertions above |

| asset | bytes | |
|---|---|---|
| `monarch-pov-stadium-v2-1080x1920.mp4` | 64 671 929 | 90.00 s, 1080×1920, 24 fps, 5 748 kb/s, **AAC 48 kHz stereo 194 kb/s** |
| `monarch-pov-stadium-v2-preview.mp4` | 2 862 638 | half resolution, 540×960, same mix |
| `monarch-pov-stadium-v2-contact-sheet.png` | 22 frames | taken from the shipped encode |

Loudness, measured on the shipped file: **mean -17.8 dB, peak -2.2 dB**, normalised
to -15 LUFS with `loudnorm` at the mux so the quiet actually reads as quiet.

```bash
python -m showreel.stickman.verify_pov
python -m showreel.stickman.pov_film --out /tmp/silent.mp4 --preset medium --crf 24
python -m showreel.stickman.pov_audio  --out /tmp/mix.wav
python -m showreel.stickman.pov_post   --src /tmp/silent.mp4 --audio /tmp/mix.wav \
       --out deliverables/monarch-pov-stadium-v2-1080x1920.mp4 \
       --preview deliverables/monarch-pov-stadium-v2-preview.mp4
```
