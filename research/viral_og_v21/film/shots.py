#!/usr/bin/env python3
"""
EP01 "The Largest Bear That Ever Hunted Humans" — shot list.

One row per shot. `sec` is the target screen time; the editor snaps to the VO
so the cut lands on the word, not on the arithmetic.

cam: (kind, params)
    push   zoom 1.00 -> z
    pull   zoom z    -> 1.00
    pan    drift (dx, dy) in fractions of frame
    drift  slow lateral with a little zoom
    shake  handheld micro-motion, amplitude
xfade: seconds of dissolve into the *next* shot (0.0 = hard cut)
"""
SHOTS = [
    # ---------- COLD OPEN 0:00
    dict(id="S01", ch=0, sec=7.0, img="kf_C", cam=("push", 1.14), xfade=0.35,
         text="37,000 – 28,000 YEARS AGO", textpos="low"),
    dict(id="S02", ch=0, sec=6.0, img="kf_B", cam=("push", 1.10), xfade=0.35,
         text="A SKULL ON A ROCK", textpos="low"),
    dict(id="S03", ch=0, sec=5.0, img="kf_C", cam=("drift", (0.035, 0.0), 1.06), xfade=0.25,
         text="PLACED.", textpos="mid"),
    dict(id="S04", ch=0, sec=6.0, img="kf_A", cam=("push", 1.12), xfade=0.30,
         text="600 KG — NOT THE BIGGEST", textpos="low"),

    # ---------- CH1 THE SHAPE 0:48
    dict(id="S05", ch=1, sec=7.0, img="kf_F", cam=("push", 1.10), xfade=0.30, text="", textpos="low"),
    dict(id="S06", ch=1, sec=7.0, img="kf_G", cam=("drift", (-0.03, 0.0), 1.05), xfade=0.30, text="GRINDING, NOT SLICING", textpos="low"),
    dict(id="S07", ch=1, sec=6.0, img="kf_A", cam=("push", 1.16), xfade=0.25, text="", textpos="low"),
    dict(id="S08", ch=1, sec=6.0, img="kf_H", cam=("shake", 0.004, 1.05), xfade=0.30, text="ONE DOOR", textpos="low"),

    # ---------- CH2 IT ATE PLANTS 1:33
    dict(id="S09", ch=2, sec=6.0, img="kf_I", cam=("drift", (0.02, 0.01), 1.06), xfade=0.25, text="MOSTLY PLANTS", textpos="low"),
    dict(id="S10", ch=2, sec=6.0, img="kf_J", cam=("push", 1.08), xfade=0.25, text="", textpos="low"),
    dict(id="S11", ch=2, sec=5.0, img="kf_K", cam=("push", 1.12), xfade=0.30, text="...AND SOMETIMES NOT", textpos="low"),

    # ---------- CH3 WHY THAT'S WORSE 2:01
    dict(id="S12", ch=3, sec=7.0, img="kf_L", cam=("drift", (0.03, 0.0), 1.06), xfade=0.28, text="A PREDATOR CALCULATES", textpos="low"),
    dict(id="S13", ch=3, sec=7.0, img="kf_A", cam=("push", 1.18), xfade=0.25, text="", textpos="low"),
    dict(id="S14", ch=3, sec=6.0, img="kf_H", cam=("shake", 0.003, 1.04), xfade=0.28, text="FURNITURE IN THE WAY", textpos="low"),
    dict(id="S15", ch=3, sec=5.0, img="kf_M", cam=("drift", (0.0, -0.02), 1.05), xfade=0.35, text="", textpos="low"),

    # ---------- CH4 THE SAME ADDRESS 2:48
    dict(id="S16", ch=4, sec=7.0, img="kf_N", cam=("drift", (0.04, 0.0), 1.08), xfade=0.28, text="THOUSANDS OF BEARS", textpos="low"),
    dict(id="S17", ch=4, sec=7.0, img="kf_O", cam=("push", 1.10), xfade=0.28, text="", textpos="low"),
    dict(id="S18", ch=4, sec=6.0, img="kf_D", cam=("push", 1.12), xfade=0.30, text="", textpos="low"),
    dict(id="S19", ch=4, sec=6.0, img="kf_P", cam=("drift", (-0.03, 0.0), 1.06), xfade=0.30, text="THE SAME ADDRESS", textpos="low"),
    dict(id="S20", ch=4, sec=5.0, img="kf_A", cam=("push", 1.10), xfade=0.30, text="", textpos="low"),

    # ---------- CH5 THE TWO DOORS 3:42
    dict(id="S21", ch=5, sec=6.0, img="kf_Q", cam=("drift", (0.03, 0.0), 1.05), xfade=0.30, text="OPTION ONE", textpos="low"),
    dict(id="S22", ch=5, sec=6.0, img="kf_M", cam=("shake", 0.005, 1.06), xfade=0.25, text="", textpos="low"),
    dict(id="S23", ch=5, sec=6.0, img="kf_H", cam=("push", 1.20), xfade=0.25, text="ONE EXIT", textpos="low"),
    dict(id="S24", ch=5, sec=5.0, img="kf_R", cam=("push", 1.10), xfade=0.35, text="", textpos="low"),

    # ---------- CH6 WHAT THE BONES ADMIT 4:21
    dict(id="S25", ch=6, sec=7.0, img="kf_E", cam=("push", 1.12), xfade=0.25, text="STILL IN IT", textpos="low"),
    dict(id="S26", ch=6, sec=6.0, img="kf_S", cam=("drift", (0.03, 0.0), 1.06), xfade=0.25, text="CUT MARKS", textpos="low"),
    dict(id="S27", ch=6, sec=6.0, img="kf_T", cam=("push", 1.10), xfade=0.25, text="", textpos="low"),
    dict(id="S28", ch=6, sec=6.0, img="kf_U", cam=("drift", (0.02, 0.0), 1.06), xfade=0.28, text="", textpos="low"),
    dict(id="S29", ch=6, sec=6.0, img="kf_V", cam=("push", 1.14), xfade=0.30, text="SPRING", textpos="mid"),

    # ---------- CH7 THE OTHER DIRECTION 5:32
    dict(id="S30", ch=7, sec=6.0, img="kf_W", cam=("push", 1.16), xfade=0.30, text="", textpos="low"),
    dict(id="S31", ch=7, sec=5.0, img="kf_M", cam=("drift", (0.0, 0.02), 1.05), xfade=0.35, text="", textpos="low"),
    dict(id="S32", ch=7, sec=4.0, img="kf_X", cam=("push", 1.08), xfade=0.35, text="", textpos="low"),

    # ---------- CH8 THE SKULLS 5:59
    dict(id="S33", ch=8, sec=7.0, img="kf_C", cam=("pull", 1.10), xfade=0.25, text="", textpos="low"),
    dict(id="S34", ch=8, sec=7.0, img="kf_Y", cam=("drift", (0.05, 0.0), 1.06), xfade=0.30, text="PUT THERE", textpos="low"),
    dict(id="S35", ch=8, sec=6.0, img="kf_Z", cam=("push", 1.12), xfade=0.30, text="", textpos="low"),
    dict(id="S36", ch=8, sec=6.0, img="kf_AA", cam=("drift", (0.03, 0.0), 1.05), xfade=0.30, text="...OR IT FELL", textpos="low"),
    dict(id="S37", ch=8, sec=6.0, img="kf_AB", cam=("push", 1.10), xfade=0.30, text="", textpos="low"),
    dict(id="S38", ch=8, sec=6.0, img="kf_AC", cam=("drift", (0.04, 0.0), 1.06), xfade=0.30, text="RED BEARS", textpos="low"),

    # ---------- CH9 FALSE ENDING 7:05
    dict(id="S39", ch=9, sec=5.0, img="kf_C", cam=("push", 1.08), xfade=0.40, text="", textpos="low"),
    dict(id="S40", ch=9, sec=3.0, img="kf_AD", cam=("push", 1.02), xfade=0.50, text="", textpos="low"),

    # ---------- CH10 TWO CAMPS 7:20
    dict(id="S41", ch=10, sec=7.0, img="kf_AE", cam=("drift", (0.03, 0.0), 1.06), xfade=0.30, text="", textpos="low"),
    dict(id="S42", ch=10, sec=6.0, img="kf_AF", cam=("push", 1.10), xfade=0.30, text="", textpos="low"),
    dict(id="S43", ch=10, sec=6.0, img="kf_AG", cam=("drift", (0.02, 0.0), 1.05), xfade=0.30, text="TWO CAMPS", textpos="low"),
    dict(id="S44", ch=10, sec=6.0, img="kf_AH", cam=("push", 1.08), xfade=0.30, text="", textpos="low"),

    # ---------- CH11 THE ROOM 8:27
    dict(id="S45", ch=11, sec=7.0, img="kf_C", cam=("push", 1.14), xfade=0.30, text="", textpos="low"),
    dict(id="S46", ch=11, sec=6.0, img="kf_AI", cam=("drift", (0.03, 0.0), 1.05), xfade=0.30, text="", textpos="low"),
    dict(id="S47", ch=11, sec=5.0, img="kf_B", cam=("pull", 1.12), xfade=0.35, text="", textpos="low"),
    dict(id="S48", ch=11, sec=5.0, img="kf_AJ", cam=("drift", (0.02, 0.0), 1.04), xfade=0.35, text="", textpos="low"),
    dict(id="S49", ch=11, sec=5.0, img="kf_C", cam=("push", 1.10), xfade=0.60, text="", textpos="low"),
    dict(id="S50", ch=11, sec=4.0, img="kf_AD", cam=("push", 1.03), xfade=0.0, text="NOT A BEAR'S ANY MORE", textpos="mid"),
]

# image prompt for every keyframe, in the same visual language as kf_A/C
PROMPTS = {
"kf_A": "already generated",
"kf_B": "Extreme wide from deep inside a huge limestone cave looking toward the entrance: the cave mouth is a small ragged dot of cold blue twilight far away, wet reflective floor, rock pillars framing the shot, fine mist and dust in a faint shaft of light. Almost total darkness in the foreground, pale cyan spill on wet rock. 24mm anamorphic, T2.8, teal shadows, faint amber bounce. Film grain, no text.",
"kf_C": "Extreme close macro of a prehistoric cave bear skull (Ursus spelaeus) on a flat rock ledge in near-darkness, single low warm firelight from the left. Long snout, steep domed forehead with pronounced sagittal crest, heavy brow ridges, empty eye sockets, aged ivory bone with dark mineral staining. 100mm macro, T2.0, warm amber key, teal shadow fill, black background, dust. Film grain, no text.",
"kf_D": "A hibernating cave bear curled inside a large limestone cave in soft cold winter light from the mouth on the right. Faint vapour from slow breath, frost on the fur, dry grass bedding, snow dusting behind. The animal is huge and rounded, a rim of pale blue light along its back. 50mm, T1.8, shallow depth of field, teal grade, atmospheric haze. Film grain, no text.",
"kf_E": "Extreme macro of an Ice Age cave bear vertebra, fossilised grey-brown bone, on a dark surface with the tip of a flint projectile point still embedded in it. Raking warm light from the right showing the flint cutting edge inside the bone, shallow depth of field, black background, forensic archaeology detail, bone pores and flint fracture lines. 100mm macro, T2.8. Film grain, no text.",
"kf_F": "Cinematic film still, 2.39:1, photoreal. Side-by-side head study of a prehistoric cave bear skull (Ursus spelaeus) and a modern brown bear skull, resting on dark wet rock, lit by one warm firelight from the left. The cave bear skull is visibly longer with a much steeper domed forehead and a high sagittal crest. Museum anatomy accuracy, shallow depth of field, black background, dust. 100mm macro, T2.8, amber key, teal fill. Film grain, no text.",
"kf_G": "Cinematic film still, 2.39:1, photoreal extreme macro. The open lower jaw of a prehistoric cave bear: broad flat grinding molars with worn crowns, heavy bone, wet dark detail, one warm light raking across from the left, deep shadows. Clinical museum accuracy, 100mm macro, T2.0. Amber key, teal fill, film grain, no text.",
"kf_H": "Cinematic film still, 2.39:1, photoreal. Point of view from deep inside a narrow limestone tunnel: a single ragged bright opening ahead, blocked by the black silhouette of a huge bear standing in it, backlit so only its outline and a pale rim of light along its shoulders is visible. Wet reflective floor, torch light behind camera throwing orange onto the near walls. Claustrophobic wide angle 24mm, T2.8, teal shadows, strong contrast, film grain, no text.",
"kf_I": "Cinematic film still, 2.39:1, photoreal macro. A pile of Ice Age plant food on a cave floor: dry grasses, roots, berries, crushed seed husks, in cold daylight from the cave mouth, with a bear's muzzle just touching the edge of frame out of focus. Natural history photography, shallow depth of field, subtle fog, teal and pale amber. 50mm macro, T2.2, film grain, no text.",
"kf_J": "Cinematic film still, 2.39:1, photoreal. A massive prehistoric cave bear grazing low vegetation on a cold open Ice Age plain at dusk, grasses and low shrubs, distant blue ridge, overcast sky, the animal's huge hump and steep forehead clearly readable in silhouette. Natural history documentary look, 135mm lens, T4, cold teal and faint amber sky, fine grain, no text.",
"kf_K": "Cinematic film still, 2.39:1, photoreal macro. A single cracked animal bone with a scrap of dried meat lying on wet cave floor gravel, isolated, lit by a narrow warm firelight from the left, everything else falling to black. Slightly disturbing, clinical, museum-quality texture detail on bone and gravel. 100mm macro, T2.0, film grain, no text.",
"kf_L": "Cinematic film still, 2.39:1, photoreal. A grey wolf standing at a distance on a snowy Ice Age plain at dusk, half-lit, watching, then turning away, tail low. Cold blue light, mist, deep blacks, distant ridge line. 200mm telephoto compression, T2.8, teal grade, film grain, no text.",
"kf_M": "Cinematic film still, 2.39:1, photoreal. A hand-held burning torch moving through a pitch black cave tunnel, only the flame and the orange pool it throws on wet rock visible, everything else black, faint dust in the beam. Extreme contrast, 35mm lens, T2.0, warm orange against pure black, film grain, no text.",
"kf_N": "Cinematic film still, 2.39:1, photoreal. A cave floor covered in hundreds of fossilised cave bear bones and skulls in situ, half buried in sediment, lit by a single cold shaft of daylight from above. Archaeology documentary, high detail on bone texture and wet clay, moody, desaturated teal with warm bone tones. 35mm lens, T2.8, film grain, no text.",
"kf_O": "Cinematic film still, 2.39:1, photoreal. Exterior of a limestone cliff in deep winter, snow falling, one dark cave mouth in the rock face, bare trees, blue hour light, footprints in the snow leading to the opening. Wide 28mm, T4, cold blue and grey, subtle warm glow inside the cave mouth, film grain, no text.",
"kf_P": "Cinematic film still, 2.39:1, photoreal. A small group of Ice Age humans in fur clothing around a low fire just inside a cave entrance, seen from behind, warming their hands, snow blowing in past them, the cave going to black behind. Firelight warm amber on fur and skin, cold blue exterior. 35mm lens, T2.0, shallow depth of field, film grain, no text.",
"kf_Q": "Cinematic film still, 2.39:1, photoreal. Two sets of tracks in fresh snow at dusk on an Ice Age plain: one leads away across open ground, one leads into the dark mouth of a limestone cave. Low raking light, long shadows, cold blue and pale amber horizon. 35mm lens, T2.8, film grain, no text.",
"kf_R": "Cinematic film still, 2.39:1, photoreal macro. A burning torch flame guttering low, almost out, held in a fur-wrapped hand, embers and smoke, everything around it black. Extremely shallow depth of field, warm orange on skin and fur, 85mm lens, T1.8, film grain, no text.",
"kf_S": "Cinematic film still, 2.39:1, photoreal macro. A fragment of fossil bone with fine, straight stone-tool cut marks across its surface, lying beside a flint blade for scale on dark cloth, raking warm light from the right. Forensic archaeology photography, extreme detail, shallow depth of field, black background. 100mm macro, T2.8, film grain, no text.",
"kf_T": "Cinematic film still, 2.39:1, photoreal macro. A long bone broken open lengthwise, the marrow cavity empty and dry, splinters and bone dust visible, lying on dark wet rock, single warm light raking from the left. Clinical, forensic, high detail, black background. 100mm macro, T2.0, film grain, no text.",
"kf_U": "Cinematic film still, 2.39:1, photoreal. A thin, hungry cave bear standing in a winter cave, ribs and shoulder blades readable under sparse fur, head low, frost on the fur, cold light from the cave mouth behind, long shadow across wet floor. Documentary realism, 50mm lens, T2.0, teal grade with faint amber rim, film grain, no text.",
"kf_V": "Cinematic film still, 2.39:1, photoreal. A cave bear emerging from hibernation into spring light at the mouth of a cave, thin and slow, two small cubs behind it in the shadow, meltwater dripping, moss and new green outside. Soft warm morning light against cold cave interior, 50mm lens, T2.0, shallow depth of field, film grain, no text.",
"kf_W": "Cinematic film still, 2.39:1, photoreal macro. A fragment of human bone with clear carnivore tooth pits and scoring, lying on dark wet cave floor gravel, single cold light from the side, everything else black. Restrained, not gory, forensic archaeology realism, extreme texture detail. 100mm macro, T2.2, film grain, no text.",
"kf_X": "Cinematic film still, 2.39:1, photoreal. An empty cave interior at first light: cold pale light at the entrance, undisturbed floor, one abandoned fur bundle, everything still. Wide 28mm, T4, pale blue and grey, deep blacks, faint mist, film grain, no text.",
"kf_Y": "Cinematic film still, 2.39:1, photoreal. Several fossilised cave bear skulls arranged on natural rock ledges deep inside a cave, lit only by a torch off-frame, dust, deep black background, dry bones with mineral staining. Archaeology of ritual, unsettling, museum-quality detail. 35mm lens, T2.0, warm amber key, film grain, no text.",
"kf_Z": "Cinematic film still, 2.39:1, photoreal macro. A cave bear skull on a rock ledge with long bones crossed beneath it, torchlight raking from the right, dust in the air, deep black background. Precise archaeology detail, dry bone, mineral stains, 85mm lens, T2.0, warm amber and teal, film grain, no text.",
"kf_AA": "Cinematic film still, 2.39:1, photoreal. A single fossil bone at the moment it topples off a rock ledge in a dark cave, caught mid-fall, dust kicked up, torchlight from the left. High shutter action still, motion implied by dust and position, black background, 85mm lens, T2.0, film grain, no text.",
"kf_AB": "Cinematic film still, 2.39:1, photoreal macro. Water seeping down a wet limestone cave wall in slow sheets, carrying fine sediment, torchlight raking across the surface to reveal the flow, deep black background beyond. Extreme texture detail, 100mm macro, T2.8, teal and amber, film grain, no text.",
"kf_AC": "Cinematic film still, 2.39:1, photoreal. Three large prehistoric cave bears painted in red ochre on a limestone cave wall, an Upper Palaeolithic painting, the wall's natural relief used as the shoulder of the central bear, torchlight raking from below so the ochre glows and the texture of the rock is visible. Chauvet-style, archaeological accuracy, wide 28mm, T2.8, deep shadows, film grain, no text.",
"kf_AD": "Near-black cinematic film still, 2.39:1. Almost pure black frame with only an extremely faint cold blue glow at the far left edge, a trace of mist. Intentionally empty, for a hard cut to black. No text, no objects.",
"kf_AE": "Cinematic film still, 2.39:1, photoreal. A vast empty Ice Age steppe under a heavy grey sky, frozen ground, dead grass, snow patches, no animals, distant ridge, cold desaturated blue-grey. Epic emptiness, 35mm lens, T5.6, film grain, no text.",
"kf_AF": "Cinematic film still, 2.39:1, photoreal. A glacial ice edge advancing across frozen ground, blue ice and shattered rock, a wall of ice filling the frame, cold light, fine snow blowing. Epic scale, 24mm lens, T5.6, deep teal and white, film grain, no text.",
"kf_AG": "Cinematic film still, 2.39:1, photoreal. A lone Ice Age hunter in fur and hide standing at a cave mouth with a wooden spear, seen from inside the cave, backlit by cold daylight, silhouette, snow beyond. 50mm lens, T2.0, strong contrast, teal and pale amber, film grain, no text.",
"kf_AH": "Cinematic film still, 2.39:1, photoreal macro. An ancient bear bone drilled and polished into a simple pendant, with a hole worn smooth, lying on dark cloth beside a stone awl, single warm light from the right, forensic detail, black background. 100mm macro, T2.8, film grain, no text.",
"kf_AI": "Cinematic film still, 2.39:1, photoreal macro. A human hand reaching toward a cave bear skull on a rock ledge, not touching, firelight from behind the hand so the fingers glow translucent and the skull stays in shadow. Intimate, restrained, shallow depth of field, 85mm lens, T1.8, warm amber and deep black, film grain, no text.",
"kf_AJ": "Cinematic film still, 2.39:1, photoreal. A modern brown bear standing at the entrance of a modern cave at night, same silhouette as a prehistoric cave, cold moonlight beyond, wet rock, faint mist. Contemporary wildlife photography feel, 70mm lens, T2.8, blue and grey, film grain, no text.",
}
