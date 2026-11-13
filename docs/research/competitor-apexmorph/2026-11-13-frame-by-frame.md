# Frame-by-frame forensics — "Why Orcas Are Terrified Of Humpback Whales"

607 seconds, sampled at **exactly 1 frame per second** (`ffmpeg -vf fps=1`), so every
line below maps to a real second of the video. Nine contact sheets are committed in
`frame-forensics/`, each covering 25 consecutive seconds, so any claim here can be
checked against the picture instead of taken on trust.

Source: Drive file `16vYFVlKJwTE7tZYJ5jSrv90KT09r4SgF`. Picture and audio container only —
**the narration is still not transcribed** (no speech model is reachable from the
sandbox). Where the writing is described below, it is from on-screen text.

## The one-line diagnosis

**This is not animation. It is PowerPoint with a camera.**

Every asset is a flat coloured shape that slides, scales or fades. There is no character
animation, no rigging, no physics, no particle simulation worth the name. The "movement"
is almost entirely: an animal shape *drifting slowly left or right* while a text label
holds on screen. What makes it feel produced is **motion-design discipline** — a consistent
language of wipes, counters and call-outs — not animation craft.

That is a replicable skill. It is also 20× cheaper than the Cycles 3D the repo currently
pays for, which is the single most useful finding in this document.

## Evidence: what a "moving" shot actually is

| Seconds | What is on screen | Is it animated? |
|---|---|---|
| 0–15 | An orca silhouette, slightly drifting, dark water | No — a static PNG with a slow pan |
| 15–25 | Blue whale silhouette beside 5 orcas, caption "THE BIGGEST ANIMAL THAT HAS EVER EVEN..." | No — one still, held 10 s |
| 25–37 | Krill cloud, then bait ball with fish | **Yes — particle drift** (the only real particle work in the video) |
| 37–47 | Text card "THE BOSS OF THE SEA" + food pyramid building | Yes — pyramid bars wipe in, one per beat |
| 50–70 | "WHAT SCARES AN ORCA?" card, three suspect panels arrive | Yes — 3 panels fly in, each with a `?` badge |
| 70–85 | Sea urchin / kelp rosette rotating | Yes — a slow rotation, nothing else |
| 85–100 | Great white swimming left, then orcas circle it with sonar rings | Yes — shape slides + repeating ring pulse |
| 100–110 | "GANSWAAI, SOUTH AFRICA · 2017" + sharks + orca silhouettes + a real EEG-style graph bottom right | Yes — a `PORT / STARBOARD` label pair and a live-looking waveform |
| 110–125 | Whale + orcas + three ticked checkboxes appearing one by one, then a red "SHOWS UP ANYWAY" stamp | Yes — **checklist reveal**, one tick per second |
| 125–140 | Krill in a red/orange blob labelled "KRILL: A FEW CENTIMETRES"; then "IT SINGS" over a waveform | Partial — a waveform drawn, that is all |
| 140–160 | A **notepad** prop: TEETH / SPEED / HUNTS IN PACKS / EATS with orca-vs-humpback ticks and crosses | No motion at all — a still page, held 20 s |
| 160–175 | "FIGHT SPECIES" card, three silhouettes listed (HUMPBACK, GREY WHALE, RIGHT WHALE), red FIGHT stamp | Yes — the same card language, restamped |
| 175–200 | Size comparison: 18 m whale vs 8 m orca, then a **grid of squares filling up** for tonnage | Yes — the grid is a *counting* device, and it is the cleverest thing in the video |
| 200–215 | "THE REAL WEAPONS" — the flipper, lit | Yes — light sweep |
| 215–225 | "UP TO 5 M" label tracked to the flipper, ending with a tiny human for scale | Yes — camera pans, label tracks |
| 225–240 | "THE ORCA PLAYBOOK": strike-through "BEAT AN ADULT HUMPBACK ✗", then "GET THE CALF ✓" | Yes — the strike and the tick are the whole beat |
| 240–255 | Real documentary plate: a lone swimmer in grey surf, then a splash | **Real footage** — the only live-action in ten minutes |
| 255–290 | "MOTHER / CALF / ESCORT" labels attached to three swimming whales | Yes — labels *track* the shapes; this is the most "animated" stretch |
| 290–310 | Whale **pushed up onto her back**, labelled; then 5×5 thumbnail grid of 25 whale photos ("1 IN 10") | Yes — the grid fills, one tile highlighted red |
| 310–320 | "89% NOT HUMPBACKS" — a circular gauge animating to 89% | Yes — **the number animates**, which is the pattern |
| 320–340 | Seals, sea lions, porpoises, grey whale calves, an ocean sunfish (a cartoon blob with one dot for an eye) | Real footage for 3 of 4, cartoon for the sunfish |
| 340–355 | "DOES THE HUMPBACK… EAT THEM? NEED THEM? GET ANYTHING BACK?" on a notepad, each line crossed out ✗ | Yes — crosses land one at a time |
| 355–380 | ANTARCTICA map, red marker, "2000" date, "WASHED OFF THE ICE" | Yes — map zoom + marker |
| 380–420 | "ONE FLIPPER ≈ 5 M", then **a red car** beside the flipper for scale | Yes — the car is the joke, and it works |
| 420–440 | "15 ORCAS", "4 HOURS", "5:05 HRS" ticking clock, "OUTLAST THEM" with an hourglass | Yes — **the clock is the tension device** |
| 440–460 | "HUMPBACKS: 16" vs "MONTEREY BAY · 2000" — a **REWIND** transport control sits in the corner | Yes — a fake playback UI |
| 460–480 | "6.4 → 6.5 HOURS OF FIGHTING", a counter stepping up; "FOOD: RIGHT THERE" | Yes — the number increments |
| 480–510 | "HUNT QUIETLY", a speech bubble "shhh…", concentric sonar rings, "THEY FOLLOW THE NOISE", "SPLASH!" | Yes — sound made visible: rings, bubble, splash |
| 510–530 | "PREDATOR / VICTIM" two-panel, then "TWO SUPERPOWERS" split by a jagged seam, then "MUTUAL HATRED" stamp | Yes — the seam is a drawn line |
| 530–560 | Back to the food pyramid, then the krill plate again | **Repetition** — this is the same asset as 37–47 |
| 560–590 | "WHICH ANIMAL NEXT?" + three comment cards ("leopard seal next?", "do the sperm whale vs orca one", "what about ...") | Yes — the cards are a fake UI |
| 590–607 | End on whale + sonar rings | Same opening asset, recycled |

## The grammar — 9 devices, used over and over

This is the actual "style". It is a fixed vocabulary, repeated until it looks deliberate.

1. **The stamp.** A word arrives in a coloured box with a border and a slight rotation:
   `THE BOSS OF THE SEA`, `JUST PLAYING DEFENCE`, `SHOWS UP ANYWAY`, `MUTUAL HATRED`,
   `FIGHT`. Same typeface, same treatment, eleven times. This is the single most
   recognisable element of the channel.
2. **The counting grid.** Tonnage as a 10×6 grid of squares that fill; 25 whale photos as
   a 5×5 grid; "1 IN 10" as one red tile. **Numbers become countable objects** instead of
   digits. This is why the video feels like it is *showing* you something.
3. **The animating number.** `0% → 89%`, `6.4 → 6.5`, `2049` counting up, `3:05 HRS` on a
   clock. A number that moves is a promise being kept in real time.
4. **The labelled animal.** Every creature gets a small caps label pinned to it —
   `MOTHER`, `CALF`, `ESCORT`, `MELON`, `RAKE MARKS`, `FLUKES`, `NEWBORN ≈ 5 M`. The label
   is often the only motion in the shot.
5. **The scale reveal.** Always ending in something the viewer knows: a **human figure**
   next to a 5 m flipper, a **car** beside the same flipper, "30+ TONNES" beside an orca.
6. **The fake UI.** A notepad with tickboxes, a comments box with three real comments, a
   `REWIND` transport control, an EEG waveform, a circular percentage gauge. Four different
   "screens" in ten minutes — each one borrows the credibility of a real interface.
7. **Sound made visible.** Concentric rings for sonar, a squiggle for "IT SINGS", a
   speech bubble `shhh…`, a `SPLASH!` word. Audio never just plays; something on screen
   always represents it.
8. **The question card.** `WHAT SCARES AN ORCA?` held for 8 s at 0:40 with an empty frame
   under it. **Deliberately boring** — it makes the viewer lean in before the answer arrives.
9. **The fake rewind.** At 7:20 a `◀◀ REWIND` control appears, and the video actually
   restates an earlier beat. It is a *structural* trick disguised as a widget.

## Measured rhythm

Sampled at 1 fps, so these are second-accurate.

| | |
|---|---|
| Total seconds | 607 |
| Hard visual changes (frame diff > 30 % of max) | **32** |
| Grouped scene beats (cuts within 2 s merged) | **24** |
| Mean frame-to-frame difference | 18.5 / 255 |
| Median | 7.7 / 255 |
| Longest **static** stretch | **20 s** (the notepad at 2:20–2:40) |
| Frames where nothing moves at all (diff < 1.0) | **0** |

That last row is the interesting one: **there is not a single frozen frame in ten
minutes.** Even the notepad is held over a slowly drifting water background. "Static" here
means "no new information", never "no movement".

### Motion energy, minute by minute

```
1  10.8  #####
2  20.9  ##########
3  22.2  ###########
4  12.6  ######
5  16.4  ########
6  28.6  ##############   ← busiest: the fight montage
7  15.3  #######
8  18.5  #########
9  22.7  ###########
10 17.5  ########
```

Minute 6 is nearly **3× busier** than minute 1. The video **starts calm and speeds up** —
the opposite of the Shorts instinct to open at maximum. Minute 4 (12.6) is the calmest,
and it lands right on the size-comparison sequence, which is information-dense but visually
still. **Pace follows the argument, not a timer.**

### Scene beat map

```
1:13  1:27  1:33  1:40  1:45  2:13  2:18  2:28  3:24  3:42  4:48  5:03
5:21  5:41  7:22  7:48  7:52  7:59  8:16  8:31  8:36  8:44  9:21  10:03
```

Count the gaps: **1:45 → 2:13 is 28 seconds with no cut.** **5:41 → 7:22 is 101 seconds.**
A channel chasing retention would never hold a shot for 101 seconds — unless the shot is
*doing work*, which it is: that stretch is the "mother/calf/escort" story.

## Three flaws, stated plainly

The operator asked for the flaws as well as the strengths. These are real:

1. **The ending is a recycle, not an ending.** 530–560 reuses the 37–47 food pyramid, and
   590–607 reuses the 0–15 opening shot. For a video whose whole engine is "new information
   every few seconds", the last minute stops delivering any.
2. **"1 IN 10" contradicts "89 %".** At 4:48 the grid says one tile in ten (10 %), then at
   5:10 the gauge says 89 %. Both are shown as facts about the same thing and neither is
   sourced on screen. A viewer who is paying attention catches this.
3. **The ocean sunfish is a cartoon blob with a dot for an eye**, dropped between three
   sequences of real footage (5:20–5:35). Everywhere else the vocabulary is consistent;
   here it looks like a placeholder that shipped.

## What to steal, in priority order

1. **The stamp vocabulary.** Eleven repeated stamps make a channel feel authored. It costs
   one font, one border, one rotation value — and it is why this looks like a *channel* and
   not a video.
2. **Numbers as objects.** The filling grid and the animating gauge do more persuasive work
   than any 3D model in the video. Both are 20 lines of code.
3. **Labels pinned to things.** `MOTHER` / `CALF` / `ESCORT` tracking three swimming whales
   is the single most "produced" moment, and it is three text layers with a path follower.
4. **A question card held deliberately empty.** 8 seconds of near-nothing at 0:40 is the
   boldest choice in the video and it is what makes the answer land.

## What not to copy

- The recycled ending. It is the cheapest-looking minute in the video.
- The 89 % / 1-in-10 contradiction. A channel claiming evidence cannot afford an
  unsourced number that argues with its own graphic.
- The car. It is funny once; as a recurring scale device it will read as filler.

## Honest limits

- **1 fps sampling.** Anything shorter than a second — a 12-frame flicker, a title that
  pops and leaves — is invisible to this method. The 32 hard changes are a *floor*, not a
  count.
- **No narration.** Every claim about writing is read from on-screen text.
- **Colour and motion are measured numerically** (mean, stddev, frame difference); the
  descriptions of *intent* are my reading of the sheets.
- The figures in `frame-forensics/` are 320×180 samples of a 1280×720 source. They are
  evidence of composition and sequence, not of sharpness.
