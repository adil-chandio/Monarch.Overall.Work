# Monarch — POV: the stadium goes quiet

**90 s · 1080×1920 · 24 fps · 2 160 frames**

A line figure walks out of a tunnel onto a floodlit pitch, is beaten by a bad
first touch, sets himself, strikes a ball at a goal — and the crowd, which has
been roaring since the first frame, is silent for the whole of it. Three lines of
type, one of which says the film is invented.

This is the topic the research desk had already written down: *"POV: You're
Ronaldo — But the Stadium Goes Silent"* (`docs/repo-intel/stickman-pov-research-report.md`).
The film keeps its premise and drops its likeness. There is no number 7 on the
shirt, no face modelled on a real person, and no claim that any of this happened.
The report's own rules ask for exactly that, and they are right: a stickman with
an original face can be anybody, and a stickman with Ronaldo's face can only be
one thing, all of which is legal risk purchased for nothing.

---

## What is actually new

### 1. The character has a face

`face.py`. Before this, the figure had one eye dot — enough to say which way it
was facing and nothing else. A film about a man under pressure is a film about a
face, so the head became a place you can act on.

Two decisions carry it:

**The head stays a circle.** An oval with a jaw would be a different character and
would fight the line drawing around it. So the head is the same circle the rig has
always drawn — filled with paper, given the same heavy rim — and the expression
lives inside it.

**Every feature is geometry, not art.** An eye is three marks (a dark oval, a paper
disc where the eye is looking, a pupil inside it); a brow is a tapered stroke whose
inner end moves independently of its outer end; a mouth is a sampled lens that
closes to a point at both corners. All of them are placed in a head-local frame
that rotates with `head_ang` and mirrors with `facing`. That means the face is
correct at 700 px (the close-up) and at 40 px (the wide), it turns with the head,
and it survives the figure turning around — none of which a set of pasted
expressions can do.

Fourteen named expressions ship with it, and shots compose them:
`FOCUS.blended(F.GRIT, k)`, `F.DISDAIN.at(sweat=0.22)`.

### 2. The stadium is a set, not a backdrop

`stadium.py`. A pitch solved per row (a floor point's screen row determines its
depth, so the mown stripes, the haze and the floodlight pool are one column
vector), a stand of ~15 000 spectators placed once and projected every frame, a
goal whose net is a real grid on the goal plane, two floodlight masts, and
advertising boards with seams in them.

Everything is projected through the same `Projector` the rig uses, so the hero
stands on the grass rather than in front of a picture of grass.

### 3. Silence is a thing you can see

There is no audio in this cut. The crowd is drawn, so the crowd has to *perform*
the sound: `churn` is how much the stand moves, and it is the film's only volume
control.

```
0 – 7 s    churn 0.50 → 1.00    loud, and getting louder, at the end of the tunnel
7 – 9 s    churn 1.00 → 0.00    he steps onto the grass and it goes
9 – 71 s   churn 0.00           sixty-two seconds of nothing
71 – 90 s  churn 0.00 → 1.00    the net settles, the noise comes back
```

At churn 0 the stand is a photograph. The palette cools with it, because a silent
stadium and a loud one cannot be the same colour.

The silence begins on the frame *before* the first footfall lands. Starting it on
the contact frame reads as a cue; starting a frame early reads as a room emptying.

### 4. Three lines of type, and one of them is a condition

`pov_text.py`, `pov_post.py`. The film names a real person in its first second, so
it has to say what it is in the same breath:

```
 0.0 –  6.8   POV: YOU'RE RONALDO
              One shot. Everyone's watching.
83.6 – 90.0   Whose POV should we animate next?
 0.0 –  6.8   An imagined scenario, not a real match.   ← under every card
83.6 – 90.0
```

**The third line is not fine print.** Every frame that carries a card carries the
disclaimer with it — the same fade in, the same fade out, never one without the
other. That is asserted rather than intended (`unattributed frames: 0` below), so
a later edit to the timing cannot quietly leave the claim standing alone.

**The hook is set against the picture, not over it.** The push-in crosses a
floodlight lamp, and a lamp is white: white type on a white lamp is gone for half
a second and nobody notices until they watch it twice. So the hook's block sits in
a band of shade, and the shade is *checked* — the verifier compares the density of
the card's own band against the open sky above the stand.

**The type is a post pass, not a re-render.** 2 160 frames at about a second each
is forty-five minutes to change a word. `pov_post.py` decodes the finished master,
composites the cached cards, and encodes the result — three minutes forty-seven,
one re-encode, no intermediate files. A card is built once as a full-frame RGBA
layer; a frame only pays for its alpha ramp and one paste.

---

## The measurements

`python -m showreel.stickman.verify_pov` — **23 assertions, all pass**

```
PASS  timeline: shots tile the film with no gap or overlap     6 shots, 90.0 s
PASS  timeline: no shot is shorter than four seconds           shortest 7.0 s
PASS  timeline: the film is at least 30 seconds                90.0 s = 2160 frames
PASS  sound: there is a real silence in the film               64.0 s below churn 0.02
PASS  sound: the crowd is back at the end                      min churn in the last 2 s = 1.00
PASS  sound: the silence arrives gradually                     max change per 0.25 s = 0.24
PASS  faces: every frame has one, and no field is out of range 180 frames sampled, 0 bad
PASS  faces: a blink lasts long enough to land on frames       0.208 s = 5.0 frames
PASS  faces: the eyes close at least once                      37 frames with the eyes shut
PASS  ball: the strike's vertical acceleration is gravity      fitted 2900.0 vs 2900.0
PASS  ball: it arrives at the height the net was framed for    -385.0 vs 385.0 below ground
PASS  ball: never below the ground in flight                   lowest point -424.6
PASS  ball: the juggle's acceleration is gravity               fitted 2900.0 vs 2900.0
PASS  figure: no foot is below the floor                       lowest point 0.00 units
PASS  figure: the pelvis never jumps between frames            max step 45.3 units
PASS  keeper: stands on the goal line, behind the hero         goal at z 2.71, hero at z 1.00
PASS  keeper: exists during the strike and not before it       absent at 0.5 s, present at 8 s
PASS  frames: all sampled frames render in range and finite    17 frames
PASS  frames: none of them is blank                            all have image
PASS  light: body is separated from the background by 0.20     worst excess -0.100
PASS  text: the hook runs 0-6.8 and the question 83.6-90        two windows, no others
PASS  text: no card is up without 'An imagined scenario'        0 unattributed frames
PASS  text: every card has ink and clears the edges by 24 px    3 cards inside
PASS  text: the hook's shade band is denser than open sky       band 114.3 vs open 0.0
```

The two text failures this caught before the film shipped are worth naming, because
both were invisible in a still:

* the disclaimer started 0.4 s after the hook, so ten frames showed a card with
  nobody's caveat under it
* the first legibility check measured the scrim, which is *meant* to reach both
  frame edges, instead of the type — so it reported a layout that was fine as if it
  were broken

The v2 and v3 verifiers still pass on the code this shares with them.

### Three bugs these caught, all invisible in a still

1. **The struck ball's arc was shaped, not solved.** `lerp` plus a `sin` bump
   reads as fine for two seconds and as wrong for ten: the ball hangs, then drops.
   It is now `y = y₀ + v_y·e + ½g·e²` with the launch velocity solved from where
   the ball has to arrive, and the fit returns gravity to the decimal.
2. **The juggle was bouncing downward.** World y grows down, so a rising ball has
   an increasingly *negative* y. The sign was wrong and the fit reported
   `g = −2900` — a plausible-looking arc accelerating the wrong way.
3. **The half-resolution backdrop moved the horizon.** `eye` is a fraction of the
   frame height, not a height, so rendering the set at half size put the camera at
   half the height and painted the pitch 400 px from where the hero's feet were.
   The set is rendered at `0.5` with `zoom × 0.5` and `eye ÷ 0.5`.

---

## Limits, stated plainly

**The set is a depth model, not a 3-D scene.** The goal, the stands and the pylons
live at different depths along the camera axis and are placed laterally by one
world x. That is why the goal sits *behind* the action as a backdrop rather than
off to one side, and why a shot that wants the goal visible has to move the goal
further away rather than turn the camera. The strike is therefore from about
24 m, not from the penalty spot. The alternative — leaving it at 11 m — means a
7.32 m goal that is wider than the frame, which does not read as a goal at all.

**There is no audio.** The crowd is shown, not heard. A mix would need a licence
for the crowd and a voice for the narration, and neither is in this repository.
The film is therefore silent everywhere, including where it is meant to be loud —
which is the one place a viewer will notice the absence. The words carry the
premise instead, and the words are also where the disclaimer lives, so a silent
cut is not a cut without a caveat.

**The crowd is a texture, not a crowd.** Fifteen thousand marks placed once, none
of them an individual, none of them moving independently. At the size they appear
this is honest; if the camera ever came within ten metres of the stand it would
not be.

**One figure, one keeper, one ball.** The keeper is a silhouette with no face —
he is a shape at the far end of the pitch, which is what a keeper is from twenty
metres, and giving him a face would compete with the hero for the only thing the
frame has room for.

**The failure shot is the weakest beat.** The bad touch reads as a ball squirming
away rather than as a skill failing; the recovery is a single lunge. It is the one
place in the film where the animation is describing a moment rather than
simulating one.

---

## Files

| path | what it is |
|---|---|
| `face.py` | expressions, presets, and the raster |
| `stadium.py` | the pitch, the stands, the goal, the light |
| `pov.py` | the six shots, as functions of time |
| `pov_film.py` | frame assembly, the ffmpeg encode, `--stills` for a contact sheet |
| `pov_text.py` | the three cards: hook, question, and the line that qualifies them |
| `pov_post.py` | lays the cards over a finished master and makes the preview |
| `verify_pov.py` | the twenty-three assertions above |
| `probe_face.py` | contact sheet of the expression vocabulary |
| `probe_set.py` | the set at four camera positions |

```bash
python -m showreel.stickman.verify_pov
python -m showreel.stickman.pov_film --stills 12
python -m showreel.stickman.pov_film --out /tmp/silent.mp4 --preset medium --crf 24
python -m showreel.stickman.pov_post --src /tmp/silent.mp4 \
       --out deliverables/monarch-pov-stadium-1080x1920.mp4 \
       --preview deliverables/monarch-pov-stadium-preview.mp4
```

| asset | bytes | |
|---|---|---|
| `monarch-pov-stadium-1080x1920.mp4` | 67 727 934 | 90.00 s, 1080×1920, 24 fps, 6 020 kb/s, bt709 |
| `monarch-pov-stadium-preview.mp4` | 3 432 726 | half resolution, 540×960, 305 kb/s |
| `monarch-pov-stadium-contact-sheet.png` | 8 frames | one row per 20 s, from the shipped encode |

Frames stream into ffmpeg one at a time; a ninety-second cut held in RAM is 12 GB
of float32 and nothing here needs it.
