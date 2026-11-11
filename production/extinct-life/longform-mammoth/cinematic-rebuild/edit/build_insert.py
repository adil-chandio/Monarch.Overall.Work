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
 # The 8-second thaw/summer excerpt of the 30-second season study fits the
 # storyboard's compressed-season beat at 140-148s exactly.
 'island-thaw':('.cache/mammoth-island-years/island-years-motion-review-silent.mp4',None,140.,240,900),  # 4.0-12.0 s of the 30 s render
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
 'genome-comparison':('.cache/mammoth-comparison-lab/comparison-lab-motion-review-silent.mp4',None,5182/30,600),
 'stream':('.cache/mammoth-stream-scene/stream-scene-motion-review-silent.mp4',None,354.,480),
 'hypothesis':('.cache/mammoth-icing-hypothesis/icing-motion-review-silent.mp4','e2ed9b28d179b12d7e7d54d5be3bcbb782d61c6638df3f3c7f64cb75229f6040',370.,420),
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
 'coverage-section':('.cache/mammoth-coverage-section/coverage-section-motion-review-silent.mp4',None,557.0,600,600),
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
 'one-genome':('.cache/mammoth-one-genome/one-genome-motion-review-silent.mp4',None,274.0,930,930),
 # The 2024 two-trend result: bias tested first, two same-length opposing arrows, and a
 # record that visibly stops before the final generations. 52 s at 577.0 s.
 'trends-section':('.cache/mammoth-trends-section/trends-section-motion-review-silent.mp4',None,577.0,1562,1562),
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
 'chemistry-section':('.cache/mammoth-chemistry-section/chemistry-section-motion-review-silent.mp4',None,305.0,1470,1470),
 # The three-tier confidence ledger: what is supported, what is plausible, what is not
 # established. 70 s placed at 689.0 s, opening on "What can we say?" and closing on
 # "these categories do not have to compete". Deliberately no cause is illustrated.
 # The ledger now stops at 734 s: its final shot was "a possibility is not a verdict", and
 # that is now said over the island instead of over a table. Its three categories keep the
 # full 689-734 s, so the cut lands on a shot boundary rather than mid-enumeration.
 'ledger-section':('.cache/mammoth-ledger-section/ledger-section-motion-review-silent.mp4',None,689.0,1350,2100),
 'verdict-close':('.cache/mammoth-verdict-close/verdict-close-motion-review-silent.mp4',None,734.0,750,750),
 # The 2025 microbial lead: an evidence ladder with the diagnosis rung left visibly
 # empty. 37 s, placed at 652.0 s on "a newer lead shows why careful questions
 # matter" through "the diagnosis is still missing".
 'new-lead-section':('.cache/mammoth-new-lead-section/new-lead-section-motion-review-silent.mp4',None,652.0,1110,1110),
 # Native island picture under the genetic argument, cutting the longest plate run in the
 # film. 66 s at 473.0 s: it takes over the bottleneck/immune/two-measures passage and
 # hands back to genetic-strain at 539.0 s, just after "recovery did not mean its genetic
 # risks disappeared". No claim is made on screen beyond the disclosure line.
 'island-hold':('.cache/mammoth-island-hold/island-hold-motion-review-silent.mp4',None,14190/30,1980,1980),
 'people-section':('.cache/mammoth-people-section/people-section-motion-review-silent.mp4',None,391.0,600,600),
 'verdict-section':('.cache/mammoth-verdict-section/verdict-section-motion-review-silent.mp4',None,759.0,720,720),
 'final-crossing':('.cache/mammoth-final-crossing/final-crossing-motion-review-silent.mp4',None,783.,390),
 'genomic-gap':('.cache/mammoth-genome-gap/genome-gap-motion-review-silent.mp4',None,629.0666666667,510),
}
if len(sys.argv)!=2 or sys.argv[1] not in choices:raise SystemExit('usage: build_insert.py island-approach|island-thaw|island-chapter|island-chapter-2|coat-section|contact-section|chemistry-section|other-islands|gene-disruption|one-genome|trends-section|genetic-strain|isolation-section|ledger-section|new-lead-section|island-hold|verdict-close|genome-record|reversal-section|coverage-section|people-section|verdict-section|genome-comparison|stream|hypothesis|final-crossing|genomic-gap')
name=sys.argv[1];spec=choices[name];file,expected,offset,frames=spec[:4];source_frames=spec[4] if len(spec)>4 else frames;video=root/file
seek={'island-thaw':4.0,'island-chapter-2':30.0,
      # Only shot 3 of the 62 s render survives: the island hold now carries 473-539 s,
      # so this excerpt is the "comparatively stable" plate read at 540-557 s.
      'genetic-strain':45.0}.get(name)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((video.parent/'render-manifest.json').read_text())
if manifest['fps']!=30:raise SystemExit('Wrong render rate')
if seek is None and manifest['frames']!=source_frames:raise SystemExit('Wrong render frame count')
if source_frames<frames:raise SystemExit('Render too short for trim')
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
report={'status':'incomplete separate editorial insert, not final','narration_offset_seconds':offset,'frames':frames,'fps':30,'lufs':float(lu[-1]),'true_peak_dbtp':float(peak[-1]),'input_sha256':expected,'audio_sha256':digest(audio),'brook_sha256':digest(brook) if brook else None,'wind_sha256':digest(root/'production/extinct-life/longform-mammoth/cinematic-rebuild/ambience-sources/felix-blume-wind-muges.ogg') if name in ('island-years','island-thaw') else None,'gain_note':('0.80 local gain to meet the true-peak guard' if name=='coverage-section' else ('0.78 local gain to meet the true-peak guard' if name=='genetic-strain' else ('0.88 local gain to meet the true-peak guard' if name in ('island-approach','trends-section') else None))),'note':'island-approach has temporary 0.88 gain to limit AAC true peak; all clips need final continuous mix','output_sha256':digest(out)}
(out.parent/f'{name}-qc.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
