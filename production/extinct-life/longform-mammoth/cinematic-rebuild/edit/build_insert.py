"""Integrate available sequences at provisional narrative offsets.

These are separate editorial inserts, not a complete film, not picture lock,
and not a substitute for the missing footage or continuous sound review.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys
import imageio_ffmpeg
base=Path(__file__).resolve().parent;root=base.parents[4]
audio=root/'production/extinct-life/longform-mammoth/cinematic-rebuild/soundtrack-draft/Narration-Score-DRAFT.m4a'
choices={
 # Trimmed to the 10 s the storyboard allows (130-140 s); the remaining 8 s of
 # this render is superseded by the compressed-season excerpt at 140 s.
 # Sea-level isolation and the three-populations caveat. 28 s schematic
 # cross-section, placed at 86.0 s on "around ten thousand years ago, sea levels
 # rose", carrying through the Wrangel / East European / St Paul dates to 114 s.
 'isolation-section':('.cache/mammoth-isolation-section/isolation-section-motion-review-silent.mp4',None,86.0,840,840),
 'island-approach':('.cache/mammoth-island-approach/island-approach-motion-review-silent.mp4',None,130.,300,540),
 # 2.7 s of the same 18 s render, second half, closing the cut between chapters.
 'chapter-breath':('.cache/mammoth-island-approach/island-approach-motion-review-silent.mp4',None,170.0,82,540),
 # 11 s: the 2017 cohort passage (172.7-192.7) opens on a second excerpt of the same render.
 'cohort-2017':('.cache/mammoth-island-approach/island-approach-motion-review-silent.mp4',None,5452/30,158,540),
 # The 8-second thaw/summer excerpt of the 30-second season study fits the
 # storyboard's compressed-season beat at 140-148s exactly.
 # island-thaw is not placed: island-chapter already holds 140-170 s, and the same
 # four seconds of island-years would read as a repeated shot.
 # 'island-thaw':(...,140.,240,900),
 # The first 30 s of the 60 s island chapter (dawn herd -> trunk to grass) sits
 # under "Picture an island population..." and the 2019 collagen passage.
 # Uses ffmpeg trim on a verified 1800-frame render; the manifest still records
 # 1800 frames, so the frame-count guard below accepts a trim of this source.
 'island-chapter':('.cache/mammoth-island-chapter/island-chapter-motion-review-silent.mp4',None,140.0,900,1800),
 # The coat section's five shots sit under the FOXQ1 passage and its "predicted,
 # never observed" caveat. 34 s render; 24 s placed from 250.0 s so the macro
 # texture lands with "a gloved researcher compares two markings" and the exit
 # hold runs into the isotope handoff at 305 s. Nothing at 244-250 s yet.
 # Second, disjoint excerpt of the SAME 60 s island render: the calf, the stream
 # crossing, the squall and dusk (30.0-60.0 s of the source). Different footage
 # from the 140 s excerpt, not a repeat of it. Sits under the premature-stop and
 # smell-receptor lines, ending on the squall-to-macro-fur handoff at 250 s.
 'island-chapter-2':('.cache/mammoth-island-chapter/island-chapter-motion-review-silent.mp4',None,220.0,900,1800),
 'coat-section':('.cache/mammoth-coat-section/coat-section-motion-review-silent.mp4',None,250.0,720,1020),
 'genome-comparison':('.cache/mammoth-comparison-lab/comparison-lab-motion-review-silent.mp4',None,5182/30,270,600),
 'stream':('.cache/mammoth-stream-scene/stream-scene-motion-review-silent.mp4',None,383.,480,480),
 'hypothesis':('.cache/mammoth-icing-hypothesis/icing-motion-review-silent.mp4','e2ed9b28d179b12d7e7d54d5be3bcbb782d61c6638df3f3c7f64cb75229f6040',369.0,420,420),
 # The verdict needs one sustained landscape, not another montage of evidence.
 # 24 s, placed at 759.0 s under "a dramatic clue is not the same thing as a cause"
 # and the conservation/devastating-final-question lines; the closing crossing then
 # begins at 783.0 s.
 # The human-evidence plate. 20 s of a dated, schematic record — no hunters, no
 # tools, no staged encounter. Placed at 391.0 s on "the third witness is us" and
 # the earliest-evidence caution; it ends before the "elsewhere" beat at 427 s,
 # which is a different claim and still has no picture.
 # The 2024 reversal: the chapter payoff, and the section most able to mislead.
 # 22 s, placed at 473.0 s on "the bottleneck was severe" through the
 # heterozygosity/homozygosity and immune-gene lines, ending before the
 # effective-size numbers at 518 s (which the curve's own labels must not pre-empt).
 # The 2024 genome record: seven mainland and fourteen Wrangel marks, opened out.
 # 16 s, placed at 455.0 s on "In 2024, researchers published a wider genetic
 # record" and the 21-genome count. NOTE: this renderer writes no manifest of its
 # own; a pinned manifest was recorded afterwards and build_insert still performs a
 # full decode and frame check. It is the weakest-verified insert in the folder.
 'genome-record':('.cache/mammoth-genome-record/genome-record-motion-review.mp4','8aa59b8a9b5c5c199271f34a972f5e9892e342d79ed8292457ffa9ff9d9b43ea',455.0,480,480),
 # Coverage and data quality: the room-through-different-windows analogy, drawn
 # literally. 20 s, placed at 557.0 s on "ancient genomes differ in how much of
 # their sequence is readable"; it stops before the two opposing trends at 589 s.
 'coverage-section':('.cache/mammoth-coverage-section/coverage-section-motion-review-silent.mp4',None,562.0,510,600),
 'reversal-section':('.cache/mammoth-reversal-section/reversal-section-motion-review-silent.mp4',None,473.0,660,660),
 # St Paul's later loss and the regional-clue caution. 16 s at 114.0 s. One open-ended
 # span, no isotope series, no coastline.
 'other-islands':('.cache/mammoth-other-islands/other-islands-motion-review-silent.mp4',None,114.0,480,480),
 # The 2017 result in detail: three kinds of disruptive change, the 43x estimate kept
 # beside its caveat, and what a premature stop or a deletion actually does. 27.27 s at
 # 192.733 s. No tick field, no sequence, no diagnosis.
 'gene-disruption':('.cache/mammoth-gene-disruption/gene-disruption-motion-review-silent.mp4',None,5782/30,818,818),
 # One genome against one genome: the 2017 warning and the sample behind it. 31 s at 274.0 s.
 # Deliberately does not redraw the 2024 curve, which reversal-section owns at 473 s.
 'one-genome':('.cache/mammoth-one-genome/one-genome-motion-review-silent.mp4',None,280.0,930,930),
 # The 2024 two-trend result: bias tested first, two same-length opposing arrows, and a
 # record that visibly stops before the final generations. 52 s at 577.0 s.
 'trends-section':('.cache/mammoth-trends-section/trends-section-motion-review-silent.mp4',None,579.0,720,1562),
 # Genetic strain: two measures that are related but not interchangeable, the immune-gene
 # finding held as a finding, and effective size kept as a model parameter. 62 s at 495.0 s.
 # The bottleneck curve is NOT redrawn here — reversal-section owns it.
 # TRIMMED to 41 s (frames 0-1230) and moved to 539.0 s: the island hold now carries
 # 473-539 s, and shot 3 of this render (the "comparatively stable" beat, which speaks
 # at 538-546 s) is not used. Trimming keeps every remaining beat in sync, because both
 # inserts read from the same continuous narration track and nothing is retimed.
 # The bottleneck curve is still not redrawn here — reversal-section owns it.
 'genetic-strain':('.cache/mammoth-genetic-strain/genetic-strain-motion-review-silent.mp4',None,16200/30,510,1860),
 # The human-contact passage: two kept-apart registers of what the dates establish and
 # what stays unresolved. 44 s at 411.0 s. No person, no encounter, no kill site.
 'contact-section':('.cache/mammoth-contact-section/contact-section-motion-review-silent.mp4',None,411.0,1320,1320),
 # The isotopic witnesses: a register of what each system can report on, the 2019
 # broad-stability comparison, and the sparse-record caveat. 49 s at 305.0 s.
 # No isotope values or axes are depicted anywhere in it.
 'chemistry-section':('.cache/mammoth-chemistry-section/chemistry-section-motion-review-silent.mp4',None,319.0,765,1470),
 # The three-tier confidence ledger: what is supported, what is plausible, what is not
 # established. 70 s placed at 689.0 s, opening on "What can we say?" and closing on
 # "these categories do not have to compete". Deliberately no cause is illustrated.
 # The ledger now stops at 734 s: its final shot was "a possibility is not a verdict", and
 # that is now said over the island instead of over a table. Its three categories keep the
 # full 689-734 s, so the cut lands on a shot boundary rather than mid-enumeration.
 'ledger-section':('.cache/mammoth-ledger-section/ledger-section-motion-review-silent.mp4',None,684.0,1500,2100),
 # 49 s now, not 25: it absorbs what verdict-section used to cover (759-783), so the film
 # does not cut between two near-identical wide shots of the same plain.
 'verdict-close':('.cache/mammoth-verdict-close/verdict-close-motion-review-silent.mp4',None,734.0,1470,1470),
 # The 2025 microbial lead: an evidence ladder with the diagnosis rung left visibly
 # empty. 37 s, placed at 652.0 s on "a newer lead shows why careful questions
 # matter" through "the diagnosis is still missing".
 'new-lead-section':('.cache/mammoth-new-lead-section/new-lead-section-motion-review-silent.mp4',None,660.0,480,1110),
 # Native island picture under the genetic argument, cutting the longest plate run in the
 # film. 66 s at 473.0 s: it takes over the bottleneck/immune/two-measures passage and
 # hands back to genetic-strain at 539.0 s, just after "recovery did not mean its genetic
 # risks disappeared". No claim is made on screen beyond the disclosure line.
 'island-hold':('.cache/mammoth-island-hold/island-hold-motion-review-silent.mp4',None,14190/30,1980,1980),
 'people-section':('.cache/mammoth-people-section/people-section-motion-review-silent.mp4',None,411.4,600,600),
 'verdict-section':('.cache/mammoth-verdict-section/verdict-section-motion-review-silent.mp4',None,759.0,720,720),
 'final-crossing':('.cache/mammoth-final-crossing/final-crossing-motion-review-silent.mp4',None,783.,390),
 'genomic-gap':('.cache/mammoth-genome-gap/genome-gap-motion-review-silent.mp4',None,625.2,330,510),
 # ---- second pass: native picture under the long plate runs ----------------------
 # All four of these are EXISTING verified renders that were never placed. Using them
 # costs no render time, which is why the balance fix can move fast without lowering
 # the bar. Each is cut to the narration beat it answers, not to a round number.
 # "The animal itself is gone..." (275.8) / "cannot tell us exactly how the animal
 # looked" (278.0) / "coped with Arctic conditions" (280.5). The ONLY one of these
 # that faces the animal's condition rather than the record of it, so it is kept
 # short and the recording plates still carry the evidence.
 'animal-living':('.cache/mammoth-island-years/island-years-motion-review-silent.mp4',None,274.0,120,900),  # 0-6 s of 30 s
 # The isotope argument runs 308.4-354 s. The island-years render is a compressed
 # season cycle, which is exactly what "a stable sampled dietary signal can coexist
 # with seasonal stress" (344.9) needs and what the plate cannot show.
 'animal-season':('.cache/mammoth-island-years/island-years-motion-review-silent.mp4',None,344.5,219,900),  # 6-18 s
 # "The earliest known archaeological evidence of people on the island" (401.4).
 # A test pit and a fragment in section - no hunter, no encounter, no tool in use.
 # The glove shot in excavation is deliberately NOT used; it reads as a toy.
 'archaeology':('.cache/mammoth-excavation/excavation-motion-review-silent.mp4',None,401.4,288,420),  # 0-10 s of 14 s
 # "a human contribution could not be ruled out, because direct evidence of an
 # encounter would be difficult to find" (422.0) and "keep the known dates separate
 # from possibilities" (437.2). Foraging is the strongest unplaced landscape: the
 # second half of its 12 s render, so no crop and no repeat of the first half.
 'animal-foraging':('.cache/mammoth-foraging-review/foraging-motion-review-silent.mp4',None,431.4,168,360),
 # The 2017 result "came from one island genome compared with one mainland genome"
 # (291.9): two bones, two cases, side by side. Placed only for that sentence and
 # its "seven years later, a larger study" hand-off; the bone trays are what the
 # words describe, and nothing on screen claims more than two individuals.
 'two-genomes':('.cache/mammoth-comparison-lab/comparison-lab-motion-review-silent.mp4',None,311.0,240,600),  # 0-9 s of 20 s
 # "the apparent gap is not proof of innocence, and it is not proof of hunting
 # either" (446.4). Present-day coastlines only - the burn-in says so - because no
 # ancient shoreline is drawn anywhere in this film.
 # 437.2-455.0: "keep the known dates separate from possibilities that the record has
 # not resolved" and "human involvement is possible, but the known dates do not establish
 # it". The shore is where that uncertainty lives; 18 s of the 30 s shoreline render,
 # used none of it elsewhere in the film, so no repeat.
 # ---- third pass: the genetics chapter, which is the longest remaining plate run ------
 # 540-646 s was 106 s of unbroken paper. These three use the still-unused tail of
 # renders already placed elsewhere, so no new render is needed and nothing repeats.
 # "a population can recover demographically and still carry lasting genetic strain"
 # (621.8-627.3): the herd, alive, after the bottleneck - which is exactly the point.
 'chap-strain':('.cache/mammoth-island-years/island-years-motion-review-silent.mp4',None,617.0,240,900),   # 12.0-20.2 s
 # "The sampled genomes did not show a clear accelerating genomic collapse" (609.3).
 'chap-nocollapse':('.cache/mammoth-shoreline-review/shoreline-motion-review-silent.mp4',None,603.0,180,900),  # 18.0-24.0 s
 # "Imagine looking into the same room through windows of different sizes" (562.3) and
 # "a shallow sequence may miss changes" (571.7): real ground, not a diagram.
 'chap-windows':('.cache/mammoth-shoreline-review/shoreline-motion-review-silent.mp4',None,557.0,150,900),   # 24.0-29.0 s
 # 652-734 is the last long run: the 2025 microbial study, then the ledger. "host-
 # associated microbial DNA across hundreds of mammoth specimens" (659.5) and "some
 # bacteria were related to known pathogens" (665.8) are about material, not categories.
 'newlead-specimens':('.cache/mammoth-comparison-lab/comparison-lab-motion-review-silent.mp4',None,652.0,90,600),   # 8.0-16.0 s
 # "The diagnosis is still missing" (686.6) - the empty case, before the ledger speaks.
 'newlead-missing':('.cache/mammoth-shoreline-review/shoreline-motion-review-silent.mp4',None,676.0,240,900),        # 0.0-8.0 s
 # "a severe bottleneck, followed by a modelled recovery" (693.8) under the Supported list.
 'ledger-bottleneck':('.cache/mammoth-island-years/island-years-motion-review-silent.mp4',None,655.0,81,900),        # 20.2-30.0 s
 'trends-section-2':('.cache/mammoth-trends-section/trends-section-motion-review-silent.mp4',None,609.0,240,1562),  # 24.0-32.0 s of the same render
 'shore-uncertainty':('.cache/mammoth-shoreline-review/shoreline-motion-review-silent.mp4',None,437.0,330,900),  # 0-18 s
 'island-extent':('.cache/mammoth-island-map/island-map-motion-review-silent.mp4',None,638.2,360,360),
 # Closing the last four narrated holes, each from the unused tail of a render already in
 # the film: never a repeat of a second already on screen (see .cache/audit_duplicates.py).
 # Second batch: mid-length holes that still carried narration, each from native footage no
 # other insert uses (ledger 50-70, new-lead 16-37, chemistry 25.5+, coat 24-34,
 # genome-gap 11-17, coverage 17-20).
 # Batch 2: the mid-length holes that still carried narration. Each slice comes from
 # native footage no other insert uses, so the audit stays at zero repeats.
 'hole-join':('.cache/mammoth-excavation/excavation-motion-review-silent.mp4',None,85.0,30,420),
 'hole-season-tail':('.cache/mammoth-coat-section/coat-section-motion-review-silent.mp4',None,351.8,66,1020),
 # 354.0-365.83 is the sulfur/strontium passage. The chemistry plate's unused second half
 # is literally that evidence, and the stream render is already fully spent at 383-399,
 # so it cannot be used twice.
 'hole-water-chem':('.cache/mammoth-chemistry-section/chemistry-section-motion-review-silent.mp4',None,354.0,355,1470),
 # 365.83-369.0 "an inference, not a directly tested glass of ancient water" - a neutral
 # cutaway, making no claim, from the coat render's unused final generation.
 'hole-water-inference':('.cache/mammoth-coat-section/coat-section-motion-review-silent.mp4',None,10975/30,95,1020),
 'hole-record-tail':('.cache/mammoth-genome-gap/genome-gap-motion-review-silent.mp4',None,471.0,30,510),
 'hole-hold-open':('.cache/mammoth-ledger-section/ledger-section-motion-review-silent.mp4',None,539.0,30,2100),
 'hole-hold-close':('.cache/mammoth-ledger-section/ledger-section-motion-review-silent.mp4',None,625.0,6,2100),
 'hole-gap-open':('.cache/mammoth-new-lead-section/new-lead-section-motion-review-silent.mp4',None,636.2,60,1110),
 'hole-extent-tail':('.cache/mammoth-new-lead-section/new-lead-section-motion-review-silent.mp4',None,650.2,54,1110),
 'hole-after-excavation':('.cache/mammoth-coverage-section/coverage-section-motion-review-silent.mp4',None,411.0,12,600),
 'hole-ask-human':('.cache/mammoth-chemistry-section/chemistry-section-motion-review-silent.mp4',None,399.0,72,1470),
 'hole-three-witnesses':('.cache/mammoth-chemistry-section/chemistry-section-motion-review-silent.mp4',None,450.0,150,1470),
 'hole-fourteen':('.cache/mammoth-coverage-section/coverage-section-motion-review-silent.mp4',None,472.0,30,600),
 'hole-isolation':('.cache/mammoth-island-years/island-years-motion-review-silent.mp4',None,187.0,172,900),
 'hole-cold':('.cache/mammoth-island-years/island-years-motion-review-silent.mp4',None,278.0,60,900),
 'hole-record':('.cache/mammoth-foraging-review/foraging-motion-review-silent.mp4',None,448.0,60,348),
 'hole-otherevidence':('.cache/mammoth-chemistry-section/chemistry-section-motion-review-silent.mp4',None,657.7,69,1470),
}
if len(sys.argv)!=2 or sys.argv[1] not in choices:raise SystemExit('usage: build_insert.py island-approach|island-thaw|island-chapter|island-chapter-2|coat-section|contact-section|chemistry-section|other-islands|gene-disruption|one-genome|trends-section|genetic-strain|isolation-section|ledger-section|new-lead-section|island-hold|verdict-close|genome-record|reversal-section|coverage-section|people-section|verdict-section|genome-comparison|stream|hypothesis|final-crossing|genomic-gap|animal-living|animal-season|archaeology|animal-foraging|two-genomes|island-extent|shore-uncertainty|hole-join|hole-season-tail|hole-record-tail|hole-hold-open|hole-hold-close|hole-gap-open|hole-after-excavation|hole-ask-human|hole-three-witnesses|hole-fourteen|hole-extent-tail|hole-isolation|hole-cold|hole-record|hole-otherevidence|chap-strain|chap-nocollapse|chap-windows|newlead-specimens|newlead-missing|ledger-bottleneck|trends-section-2|chapter-breath|cohort-2017')
name=sys.argv[1];spec=choices[name];file,expected,offset,frames=spec[:4];source_frames=spec[4] if len(spec)>4 else frames;video=root/file
seek={'island-thaw':4.0,'island-chapter-2':30.0,
      # The first half of the 12 s foraging render frames the animal hard against the
      # left edge; the second half is the usable landscape. Start at 6.0 s so the whole
      # excerpt is the good framing rather than most of it being the bad one.
      'animal-foraging':6.0,
      # Second batch: mid-length holes that still carried narration, each from native footage no
 # other insert uses (ledger 50-70, new-lead 16-37, chemistry 25.5+, coat 24-34,
 # genome-gap 11-17, coverage 17-20).
      'hole-join':300/30,  # excavation 10.0-11.0 s (archaeology holds 0-9.6)
      'hole-season-tail':24.0,
      'hole-record-tail':11.0,
      'hole-hold-open':50.0,
      'hole-hold-close':51.0,
      'hole-gap-open':16.0,
      'hole-extent-tail':18.0,
      'hole-water-chem':35.4,     # chemistry 35.4-47.23 s (chemistry-section holds 0-25.5)
      'hole-water-inference':28.0,# coat 28-31.17 s (insert holds 0-24, hole-join 27-28)
      'hypothesis':0.0,         # icing render from frame 0, 369-383
      'hole-after-excavation':18.4, # coverage 18.4-18.8 s
      'hole-ask-human':28.0,      # chemistry 28-30.4 s (otherevidence holds 25.5-27.8)
      'hole-three-witnesses':30.4,# chemistry 30.4-35.4 s
      'hole-fourteen':17.0,       # coverage 17.0-18.4 s (insert holds 0-17)
      'hole-isolation':4.0,
      'hole-cold':9.7334,       # island-years 9.733-11.57 s
      'hole-record':4.0,        # foraging 4-6.0 s (living holds 0-4, foraging 6-11.6)
      'hole-otherevidence':25.5, # chemistry 25.5-27.8 s (insert holds 0-25.5)
      'chapter-breath':10.0,   # island-approach 10-12.733 s
      'cohort-2017':382/30,    # island-approach frame 382 (12.733 s) to the end
      # Each of these is a DISJOINT slice of a render used elsewhere. The audit script
      # (.cache/audit_duplicates.py) exists because check_coverage cannot see this: two
      # inserts can be at different points in the film and still be the same seconds of
      # picture, which reads as a repeated shot.
      'two-genomes':9.0,        # comparison-lab 9-17 s (genome-comparison has 0-9)
      'newlead-specimens':17.0, # comparison-lab 17-20 s
      'animal-season':12.0,     # island-years 12-19.3 s (thaw holds 4-12)
      'chap-strain':19.3,       # island-years 19.3-27.3 s
      'ledger-bottleneck':27.3, # island-years 27.3-30 s (last 2.7 s)
      'chap-windows':0.0,       # shoreline 0-5 s
      'chap-nocollapse':5.0,    # shoreline 5-11 s
      'newlead-missing':11.0,   # shoreline 11-19 s
 'shore-uncertainty':19.0, # shoreline 19-30 s
      'trends-section-2':24.0,  # trends 24-32 s (trends-section has 0-24)

      # Only shot 3 of the 62 s render survives: the island hold now carries 473-539 s,
      # so this excerpt is the "comparatively stable" plate read at 540-557 s.
      'genetic-strain':45.0}.get(name)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((video.parent/'render-manifest.json').read_text())
if manifest['fps']!=30:raise SystemExit('Wrong render rate')
if seek is None and manifest['frames']!=source_frames:raise SystemExit('Wrong render frame count')
avail=source_frames-(round(seek*30) if seek is not None else 0)
if avail<frames:raise SystemExit(f'Render too short for trim: need {frames}, have {avail}')
for source,checksum in manifest['input_sha256'].items():
 if not (root/source).is_file() or digest(root/source)!=checksum:raise SystemExit(f'Render source changed: {source}')
if expected is None:expected=manifest['output_sha256']
if manifest['output_sha256']!=expected:raise SystemExit('Unexpected render manifest')
if not video.is_file() or digest(video)!=expected:raise SystemExit('Missing or changed input render')
if digest(audio)!='434f2c344b428982edf8b00607b8361c4c45bec95da6ac5330c87428a45c3760':raise SystemExit('Unexpected soundtrack')
out=root/f'.cache/mammoth-edit/{name}-incomplete-workprint.mp4';out.parent.mkdir(parents=True,exist_ok=True)
ff=imageio_ffmpeg.get_ffmpeg_exe();duration=frames/30
cmd=[ff,'-y','-hide_banner','-loglevel','error']+(['-ss',str(seek)] if seek is not None else [])+['-i',str(video),'-ss',str(offset),'-i',str(audio)]
brook=None
if name=='stream':
 brook=root/'production/extinct-life/longform-mammoth/cinematic-rebuild/ambience-sources/brook-candidate/ambience-stream-clear.mp3'
 if not brook.is_file() or digest(brook)!='497209be73f6f05e46e924c6801dbab3921d1c587b531657120af14c546964dc':raise SystemExit('Unexpected brook ambience')
 cmd+=['-ss','8','-i',str(brook)]
 filters=f'[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS[base];[2:a]atrim=duration={duration},asetpts=PTS-STARTPTS,volume=0.20,afade=t=in:st=0:d=0.8,afade=t=out:st=14.5:d=1.5[water];[base][water]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.82:level=0[a]'
elif name=='island-approach':filters=f'[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS,volume=0.88[a]'
elif name=='chap-strain':
 # Peaks at -0.3 dBTP at 17 s into the render; 0.78 clears the guardrail.
 filters=f'[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS,volume=0.78[a]'
elif name in ('chap-windows','chapter-breath','cohort-2017','hole-fourteen'):
 # 8.2 s excerpt peaks at -0.7 dBTP untouched. 0.85 clears the -1 dBTP guardrail; a local
 # fix, not a mastering decision for the finished film.
 filters=f'[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS,volume=0.85[a]'
elif name=='genetic-strain':
 # This 41 s excerpt of the narration peaks at -0.4 dBTP untouched. 0.78 gain clears the
 # -1 dBTP guardrail; local fix, not a mastering decision for the finished film.
 filters=f'[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS,volume=0.78[a]'
elif name=='trends-section':
 # This stretch of narration peaks at -0.8 dBTP untouched. 0.88 gain clears the -1 dBTP
 # guardrail; a local fix, not a mastering decision for the finished film.
 filters=f'[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS,volume=0.88[a]'
elif name=='coverage-section':
 # The narration runs hot here (+/-0.4 dBTP before trimming). 0.80 gain keeps the
 # section under the -1 dBTP guardrail; it is a local fix, not a mastering decision.
 filters=f'[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS,volume=0.80[a]'
elif name=='island-years' or name=='island-thaw':
 # Low wind bed under the score; derivative identity/rights reviewed only by README.
 wind=root/'production/extinct-life/longform-mammoth/cinematic-rebuild/ambience-sources/felix-blume-wind-muges.ogg'
 if not wind.is_file() or digest(wind)!='debd59186e58b751eba29de80e1368c3234526f1efc89a91b40ce469cffb1479':raise SystemExit('Missing or changed wind candidate')
 cmd+=['-ss','6','-i',str(wind)]
 filters=f'[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS[base];[2:a]atrim=duration={duration},asetpts=PTS-STARTPTS,volume=0.11,afade=t=in:st=0:d=2.2,afade=t=out:st={duration-2.4}:d=2.4[wind];[base][wind]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.82:level=0[a]'
else:filters=f'[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS[a]'
cmd+=['-filter_complex',filters,'-map','0:v:0','-map','[a]','-frames:v',str(frames),'-c:v','libx264','-preset','fast','-crf','20','-threads','2','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)]
subprocess.run(cmd,check=True)
r=subprocess.run([ff,'-hide_banner','-i',str(out),'-filter_complex','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True)
f=re.findall(r'frame=\s*(\d+)',r.stderr);peak=re.findall(r'Peak:\s*(-?[\d.]+) dBFS',r.stderr);lu=re.findall(r'I:\s*(-?[\d.]+) LUFS',r.stderr)
if not f or int(f[-1])!=frames or not peak or float(peak[-1])>-1 or not lu:raise SystemExit('Decode/frame/peak failure')
report={'status':'incomplete separate editorial insert, not final','narration_offset_seconds':offset,'frames':frames,'fps':30,'lufs':float(lu[-1]),'true_peak_dbtp':float(peak[-1]),'input_sha256':expected,'audio_sha256':digest(audio),'brook_sha256':digest(brook) if brook else None,'wind_sha256':digest(root/'production/extinct-life/longform-mammoth/cinematic-rebuild/ambience-sources/felix-blume-wind-muges.ogg') if name in ('island-years','island-thaw') else None,'gain_note':('0.80 local gain to meet the true-peak guard' if name=='coverage-section' else ('0.78 local gain to meet the true-peak guard' if name=='genetic-strain' else ('0.88 local gain to meet the true-peak guard' if name in ('island-approach','trends-section') else ('0.85 local gain to meet the true-peak guard' if name in ('chap-strain','chap-windows','chapter-breath','cohort-2017','hole-fourteen') else None)))),'note':'island-approach has temporary 0.88 gain to limit AAC true peak; all clips need final continuous mix','output_sha256':digest(out)}
(out.parent/f'{name}-qc.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
