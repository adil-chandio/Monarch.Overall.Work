#!/usr/bin/env python3
"""Package measured evidence + explicitly sampled human observations. No media production."""
import argparse,csv,json,math,shutil
from pathlib import Path

NATIVE_CHECKS={'01-hearts':[360],'02-stomach':[480],'03-splinter':[330],'04-balloon':[180],'05-surfer':[870],'06-concert':[150],'07-balcony':[540],'08-ai':[60,1600],'09-fight':[780],'10-jerboa':[60,1049]}
CRAFT={
'01-hearts':('Mechanism lives inside a body, not on an isolated display pedestal.',
'0–8s: exposed torso → removed organ/device comparison. 9–13s: chamber cutaway with diaphragm and red particles. 14–18s: external controller/patient relationship. 19–28s: circulation markers return to the implanted device.',
'Visible assets include vessel-connected dual chambers, diaphragm, tubes, torso, gloves, bed and external controller. At f360 the chamber wall is sliced open, blood-colored particles sit inside the passage, and foreground reflective housing contrasts with soft background anatomy. These are observed appearance properties, not recovered shader nodes. The causal unit is pressure/displacement and flow through a bounded structure. Cyan emphasis and red/blue/purple paths isolate function without abandoning context. The 406×720 edition limits fine texture judgments.'),
'02-stomach':('The removal/reconnection verbs receive actual visual consequences.',
'0–8s: incision, organ exposure, highlighted target and instruments. 10–12s: removed organ held in hands. 13–18s: transparent digestive route and connection. 19–26s: face/body context → close food pathway.',
'Visible assets: layered abdomen, gloved hands, scissors-like tools, stomach, esophagus and intestinal loops. The f480 check shows a continuous upper passage joining highlighted intestine within a transparent blue torso. Organ removal and route explanation are distinct scales, not the same model orbiting. Yellow light-like outlining and translucent surroundings direct attention. No medical accuracy or invisible surgical technique is certified here.'),
'03-splinter':('Scale changes trace a local object into a body-wide consequence.',
'0–4s: wooden contact and finger presentation. 5–9s: skin redness/swelling. 10–18s: transparent finger → hand/forearm → torso warning. 20–24s: character returns and tweezers appear.',
'The finger, embedded fragment, skin, internal red branching structures and particles retain a spatial relationship. At f330 the long yellow fragment sits inside a translucent finger with yellow-green points along the internal path; the real underlying rig or particle system is unknown. The blue background isolates the finger silhouette; blurred character context preserves ownership. Visible tweezers turn the ending back into a concrete action. Warning graphics are not independent medical evidence.'),
'04-balloon':('The view changes to show controls, forces, landing area and consequences.',
'0–2s: basket action. 3–7s: envelope → burner controls. 8–21s: airflow, target area, side vent and descent/rotation views. 22–29s: pilot reaction/collapse. 30–34s: power lines and crash/fire.',
'At f180 twin ribbed burner housings, brackets, cables and basket supports occupy the foreground while flame and yellow envelope connect vertically; the pilot looks toward them below. Metallic highlights distinguish hardware from cloth/landscape. White airflow marks and a colored ground region make forces and target space visible. Wide-to-control-scale changes are motivated by the explanation. This is an observation of an illustrated sequence, NOT validated emergency guidance.'),
'05-surfer':('Body state and environment change through a rescue/recovery chain.',
'0–7s: attack/injury at board/water level. 8–14s: helpers and coast geography. 15–16s: ambulance/hospital. 17–22s: patient-oriented clinical viewpoint. 23–24s: recovery bed. 25–31s: ocean return and rise on board.',
'Visible assets include articulated surfers, changed arm silhouette, boards, water, shark, coast, vehicle and clinical staff/equipment. f870 shows the survivor crouched with weight lowered over a board before a large wave; foam, glossy wave surface and body/board contact are readable. The scene is not merely an orbit around an intact generic avatar. Clinical shots place staff near the viewpoint, making scale personal. Exact wave simulation, character rig and motion capture cannot be recovered.'),
'06-concert':('Actual impact is contrasted with an explanatory crowd-support schematic.',
'0–6s: stage dive, fan impact and cervical cutaway. 7–11s: gold/cyan crowd-surf illustration. 12–17s: actual fan on floor. 18–21s: ambulance and surgery. 23–27s: care and raised hands.',
'Crowd, performer and injured fan occupy a shared contact space. The f150 native check shows vertebrae around a highlighted red cord, with translucent external tissue: a location-specific injury explanation rather than an unrelated skeleton prop. Gold/cyan figures distinguish a comparison from the character-level scene. Surgery and care use a teal clinical palette. The ending visibly changes pose and face; captions indicate recovery, but no continuous narration has been independently transcribed or clinical outcome verified.'),
'07-balcony':('Suspension, support and relief are expressed through load-bearing poses.',
'0–7s: railing gap and caught head. 8–11s: hanging height and people below. 12–17s: chair-stack/climb. 18–24s: leg support and strain. 26–32s: grandmother reaches, lifts and holds child.',
'Bars, building wall, chairs, helper hands, child pajamas and doorway preserve spatial context. At f540 both hands physically bracket/support the lower legs, upward arrows occupy the side, and the child grips near the bars with a worried-looking face. The patterned garment, metal rail, textured wall and skin remain visually distinct. Later red arm highlight plus wavy marks explain effort. This supports a load-bearing interpretation, not a verified physics simulation. Subsecond intersections/sliding still require dense review.'),
'08-ai':('An object handoff carries a fictional comparison between abstract agents.',
'0–9s: oversized hand/glove transfer and screen setup. 10–30s: imagined city consequences and disappearance. 31–42s: other logo figures and refusal bubbles. 43–52s: pending-answer setup. 52.986267s onward: measured white tail in this edition.',
'At f60 a large hand visibly grips a reflective gold gauntlet above a smaller logo-faced humanoid; the size hierarchy, plaid trousers, white shoes and colored stones are legible. The glove persists across several settings and stands in for power. City chaos, particle disappearance and UI-like bubbles visualize a hypothetical, not an independently reproducible model experiment. f1600 is white. The retrieved edition does not visibly resolve the promised last answer before its white tail; do not invent an ending or infer creator/platform intent.'),
'09-fight':('Escalating numbers become coordinated body contacts, not just larger text.',
'0–4s: one-child forehead restraint. 5–12s: group/count and weight comparisons. 13–17s: single-child handling and evasive poses. 18–23s: larger approaching group. 24–28s: guard, tackle and pile.',
'The blue perspective grid gives position and scale while bright repeated garments separate the children. At f780 the adult is falling/prone and multiple children overlap above him; outstretched arms, shoe orientation and floor contact carry the action. This source uses comparatively simple scenery yet changes poses and contact relationships. Therefore expensive scenery alone cannot explain the reference gap. Weight numbers and labels are explanatory graphics, not validated biomechanical results or actual counted impact forces.'),
'10-jerboa':('A tactile construction hook develops into locomotion and a mascot payoff.',
'0–9s: hand-held animal, long legs/tail/ears and table presentation. 10–19s: owl threat, jump-height and turning graphics. 20–27s: tail angles, balance and relaunch. 28–38s: human scale → larger stylized mascot.',
'At f60 fine fur, whiskers, small feet and fingers establish a tactile creature rather than a smooth primitive. At f1049 a larger mascot has layered pale/orange fur, oversized glossy eyes, pink/orange inner ears, a blue collar and pendant, distinct long dark legs and a held prop; girl/shoes/grass give scale. Foreground grass detail and a soft background separate the hero. Degree numbers describe depicted rotation only; exact measured animal biomechanics are not independently validated. The mascot is a stylistic/brand shift, not evidence that real jerboas have those proportions.')
}

def validate(corpus, observations):
 cases=corpus['cases']
 if len(cases)!=10 or {r['key'] for r in cases}!=set(observations):raise ValueError('Expected exactly ten corresponding cases')
 for r in cases:
  notes=observations[r['key']].split(';')
  if len(notes)!=math.ceil(r['source_video_seconds_from_pts']) or any(not x.strip() for x in notes):raise ValueError('One nonempty sampled note required per second: '+r['key'])
  if r['every_frame_visually_inspected'] or r['continuous_audio_listened']:raise ValueError('This first-pass package cannot certify exhaustive review')
 return cases

def main():
 p=argparse.ArgumentParser();p.add_argument('--analysis',type=Path,default=Path('.cache/reference-forensics/zack-ten/analysis'));p.add_argument('--observations',type=Path,default=Path('docs/research/zack-original-access/first-pass-observations.json'));p.add_argument('--out',type=Path,default=Path('reports-private/reference-forensics/zack-ten'));p.add_argument('--public-evidence',type=Path,default=Path('docs/research/zack-original-access/actual-editions-evidence'));a=p.parse_args()
 corpus=json.loads((a.analysis/'corpus-evidence.json').read_text());observations=json.loads(a.observations.read_text());cases=validate(corpus,observations)
 for dest in [a.out,a.public_evidence]:dest.mkdir(parents=True,exist_ok=True)
 parts=['''# Ten actual Zack D. Films platform editions — evidence-backed FIRST PASS

**Production remains STOPPED. This is a research dossier, not authorization to make a video.**

## What has genuinely happened

- Ten actual MP4s acquired by ordinary public platform retrieval, both audiovisual tracks decoded remotely, then authenticated/checksummed after encrypted local transfer. Workflow: https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/42438157062
- **9,772 decoded frames** indexed with source presentation timestamps. This is numerical coverage, not 9,772 visually examined frames.
- **342 source image positions across 21 contact sheets opened for visual review**, spanning every second and an extra final frame for each clip. The contact sheets reduce display size. **12 native-resolution stills** additionally inspected for contact/material detail.
- **332 one-second intervals** now have coarse sampled visual notes, plus frame coverage and mixed-track energy measurements. A note describes the near-start image, not everything occurring during that second.
- **0/10 exhaustive manual frame-and-continuous-audio studies completed.** Continuous audio listening, word timing, SFX/music identification, all native frames and subsecond contacts remain unverified. No hidden software settings or stems were recovered.

## Source identity and scope

This is a new ten-source cohort, NOT the earlier fixed ten YouTube IDs. Nine files are X editions from `@zackdfilms1`, corroborated by a verified/self-described profile, Wikitubia's listed handle and matching titles on the official YouTube channel. No primary Linktree→X cross-link was found, so identity is corroborated, not cryptographically established. Jerboa is a Facebook edition from the account directly linked by the publisher's Linktree. Uploader fields were checked on retrieval. These are not claims of source-project access, original YouTube bytes, matching cuts or highest original render resolution.

Provenance anchors: https://linktr.ee/zackdfilmsofficial ; https://youtube.fandom.com/wiki/Zack_D._Films ; https://x.com/zackdfilms1 ; https://www.youtube.com/@zackdfilms/about . Source-specific URLs and hashes are preserved below and in JSON. Public API view counts from the older cohort are NOT assigned to this new cohort; a ten-million-view qualification has not been established for these exact editions.

The 74,458,545 plaintext source bytes remain local/ignored, not public playable uploads. Public transport files are encrypted. The private key must never be published. Measured ledgers and our paraphrased research notes can be kept separately from copyrighted source media.

## Evidence vocabulary

- **Measured:** decoded frame/PTS, dimensions, mixed-audio energy, integrated LUFS/true peak, white-pixel tail test.
- **Observed, sampled:** objects, poses, colors, cutaway layouts and visible captions in opened source stills. Not a complete motion watch or narration transcript.
- **Inferred:** explanatory purpose, probable load support, attention direction, causal narrative structure; grounded examples are given, not asserted as production metadata.
- **Unavailable/unverified:** native project/rig/lens/shader/light settings, exact authored camera curves, separated audio stems, full narration/SFX/music audit and physical/medical factual validation.

## Technical inventory

Duration below is last video PTS + median decoded frame interval − first PTS. It can differ slightly from container/API duration or decoded audio length. Frames are zero-indexed; timestamps are source-relative seconds, not editorial timecode. Contact sheets use first frame at/after each second; native-check frames use exact FFmpeg source frame numbers.

| Case | Source edition | Frames | Video seconds | Decoded size | Mixed LUFS-I | Measured dBTP |
|---|---|---:|---:|---|---:|---:|''']
 for r in cases:
  parts.append(f"| {r['key']} | {'Facebook' if r['key']=='10-jerboa' else 'X'} | {r['decoded_frame_count']} | {r['source_video_seconds_from_pts']:.6f} | {r['native_frame_size_from_decode_log']} | {r['integrated_lufs']} | {r['true_peak_dbtp']} |")
 parts.append('''
### Audio: actual measurement, not a guessed sound-design review

The table uses FFmpeg loudnorm **input** statistics on the decoded mixed soundtrack; no audio was normalized or altered. LUFS-I is a short-clip integrated measurement, not a voice-stem target. Positive dBTP occurs in some retrieved editions; this indicates measured reconstructed/inter-sample overshoot, NOT proof of audible clipping, nor a recommendation to target overshoot. Platform encoding may affect these readings. Per-second RMS is the combined voice/music/effects signal and cannot identify an effect, musical cue, ducking or voice clarity. No continuous perceptual audio review has been completed, so exact narration, SFX names, music entry/exit and mix quality are deliberately not invented.

### A concrete source-edition anomaly

The AI clip ends with **48 near-white decoded frames, starting f1588 at 52.986267s**. Test: at least 99% of 90×160 downsampled pixels have every RGB channel ≥250/255; measured on the final continuous run. A native export at f1600 was also opened and is white. This is present in this retrieved edition, not an export placeholder in our contact sheet. Do not assume it is the intended original ending, a loop, corruption, censorship or a defect in every platform edition. Its cause is unestablished.

## Cross-case craft findings — observed pattern, not a virality guarantee

1. **An action is the explanatory unit.** Stomach removal has tools and held organ (10–12s); balcony support has hands under legs (f540); surfer returns from crouch to standing (29–31s). Moving a camera around a passive model does not substitute for these relations.
2. **Scale changes answer a new question.** Splinter goes skin → internal finger → arm → torso → tweezers. Heart moves chest → chamber → controller → flow. This is motivated reframing, not proof of a particular focal length or camera rig.
3. **Contacts carry stakes.** Rail/neck, hand/leg, foot/board, performer/fan and gauntlet/hand relationships need authored poses and continuity. First-pass stills cannot certify absence of sliding/interpenetration between samples.
4. **Hero assets have local, readable structure.** Chamber wall/diaphragm, burner ribs/brackets, patterned pajamas, anatomy and fur/eyes are visible, not substituted with labels on primitive shapes. This is not a claim of exact polygon counts or expensive rendering engines.
5. **Color and material serve hierarchy.** Reflective hardware vs soft tissue; cyan/transparent context vs highlighted path; blue grid vs warm clothes; foreground fur/grass vs soft background. Perceptual contrast is observable; shader graphs/light counts are not.
6. **Graphics supplement geometry.** Arrows sit by the supported legs; particles stay inside the chamber/path; turning angles follow the animal. Captions do not perform the physical verb on their own.
7. **Simple scenery is not automatically weak.** Fight's blue-grid space still contains distinct contact/pose states and group escalation. More background assets alone would not repair the rejected production's action/character gap.
8. **The benchmark is not one immutable style or zero defects.** Clinical, schematic, character-story, city-fiction and furry-mascot styles coexist. Low-resolution editions, overshoot and a white tail must be recorded rather than erased to support a “perfect source” story.

### What these findings imply for our rejected Short — diagnosis, NOT new production

The user has rejected its quality. These references suggest that the needed improvement is authored subject performance, articulated contact, readable hero construction, causal scene progression and motivated scale changes—not another export check, louder mix, extra labels, a different orbit or an opening-only cosmetic patch. This is a craft hypothesis supported by the references; it is not a completed side-by-side frame-matched evaluation of the rejected export. No new scene, asset, narration, music or film render has been made.

## Ten case studies and second-by-second sampled ledger

**Read each row correctly:** the interval is a coverage bin, but its visual sentence describes one coarse near-start sample. The exact sampled source frame and PTS are supplied so the claim can be checked. Rapid contact, a cut or a caption could occur later within that interval. Camera verbs in these notes describe apparent view changes across samples; object scaling/editing cannot always be distinguished from an authored camera move. Visible medical/safety/AI claims are not independently fact-checked here.
''')
 total_intervals=0
 for r in cases:
  key=r['key'];folder=a.analysis/key
  with (folder/'every-frame.csv').open() as f:frames=list(csv.DictReader(f))
  with (folder/'second-by-second.csv').open() as f:seconds=list(csv.DictReader(f))
  if len(frames)!=r['decoded_frame_count'] or sum(int(x['frame_count']) for x in seconds)!=len(frames):raise ValueError('Coverage mismatch: '+key)
  if len(seconds)!=len(observations[key].split(';')):raise ValueError('Interval mismatch: '+key)
  title,beats,craft=CRAFT[key]
  parts.extend([f"\n### {key}: {r['publisher_metadata']['title']}\n",f"Source: {r['source_url']}\n\nSHA-256: `{r['sha256']}`\n",f"**Craft finding:** {title}\n\n**Sampled progression:** {beats}\n\n**Objects, character, framing, appearance and explanatory graphics:** {craft}\n"])
  inspected=[]
  for n in NATIVE_CHECKS[key]:inspected.append({'frame':n,'relative_seconds':float(frames[n]['relative_pts_seconds'])})
  parts.append('**Additional native stills actually opened:** '+', '.join(f"f{x['frame']} @ {x['relative_seconds']:.6f}s" for x in inspected)+'. Exact still checks do not certify neighboring motion.\n')
  parts.append('| Interval seconds | Sample f / exact PTS seconds | Sampled visible action/state |\n|---|---|---|')
  for i,(interval,note) in enumerate(zip(seconds,observations[key].split(';'))):
   sample=r['sampled_source_frame_ids'][i];t=float(frames[sample]['relative_pts_seconds'])
   interval.update(sampled_frame=sample,sampled_relative_pts_seconds=t,visible_at_near_start_sample=note,visual_review_status='one_second_sample_inspected_not_all_native_frames',audio_listening_status='not_perceptually_listened')
   parts.append(f"| {i}–{float(interval['end_relative_seconds']):.3f} | f{sample} / {t:.6f} | {note} |")
  total_intervals+=len(seconds)
  evidence={**r,'native_stills_opened':inspected,'every_frame_visually_inspected':False,'continuous_audio_listened':False,'sampled_second_notes_count':len(seconds),'sample_grid_positions_opened':len(r['sampled_source_frame_ids'])}
  for dest in [a.out,a.public_evidence]:
   sub=dest/key;sub.mkdir(exist_ok=True)
   (sub/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
   (sub/'every-frame.csv').write_text((folder/'every-frame.csv').read_text())
   with (sub/'second-by-second-observed.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(seconds[0]),lineterminator='\n');w.writeheader();w.writerows(seconds)
   if (folder/'white-tail-check.json').exists():shutil.copy2(folder/'white-tail-check.json',sub/'white-tail-check.json')
 parts.append('''
## Completion gate and remaining work

| Requested layer | Current honest state |
|---|---|
| Actual audiovisual access | Ten source editions acquired, authenticated and decoded |
| Every-frame numeric timeline | 9,772/9,772 decoded frames indexed |
| Second-by-second sampled visual notes | 332/332 bins; 342 image positions opened across 21 sheets |
| Native material/contact spot checks | 12 stills opened; all ten sources represented |
| Every-frame perceptual visual review | NOT complete; dense micro-event inspection still required |
| Narration/word timestamps | NOT transcribed/aligned; captions are not assumed verbatim audio |
| Continuous audio/SFX/music listening | NOT complete; mixed-track numerical measurements only |
| Exact cut list/camera trajectories | NOT established; RGB-change candidates are not verified cuts |
| Renderer/lens/rig/material node settings | Unavailable from rendered frames; do not invent |
| Source facts/virality causation | Not established by this animation study |
| Permission to make another video | Still NO |

Next research pass must prioritize short contact/change windows (tool/organ separation and reconnect; balloon controls; splinter removal; head/rail and supporting hands; surfboard rise; crowd impact and tackle; tail turn), open adjacent native frames and record exact before/contact/after PTS rather than extrapolate smoothness from 1Hz. Then a real continuous perceptual listen and time-aligned narration/effects/music ledger is needed. Without that, the user's requested full audiovisual microscope review is unfinished.

## Reproduction and preservation

- `scripts/research/decrypt-reference-transfer.py`: authenticated local source restore, requires the existing PRIVATE ignored key. Never print/commit/upload the key.
- `scripts/research/audit-actual-source-corpus.py`: full decode/index, native 1Hz exports, grids and mixed-track measurements.
- `scripts/research/build-ten-source-first-pass.py`: validates and packages measured ledgers with these explicitly sampled observations. It does not regenerate media or certify a full manual watch.
- `docs/research/zack-original-access/first-pass-observations.json`: our paraphrased sampled notes, one per second.
- `docs/research/zack-original-access/actual-editions-evidence/`: small persistent numeric evidence, hashes, provenance and sampled-note CSVs. No plaintext video, audio or screenshots published there.
- Private local dossier and mirrored evidence: `reports-private/reference-forensics/zack-ten/`.
- Source images/audio/raw media: `.cache/reference-forensics/zack-ten/`; cache does not persist in snapshots. Encrypted transfer + retained local key allow restoration. Individual PNG stills/contact sheets are review aids, not recovered project files.
''')
 report='\n'.join(parts).rstrip()+'\n'
 (a.out/'ACTUAL-FOOTAGE-FIRST-PASS.md').write_text(report)
 (a.public_evidence/'FIRST-PASS.md').write_text(report)
 manifest={'production_hold':True,'source_count':len(cases),'decoded_frames':sum(r['decoded_frame_count'] for r in cases),'sample_grid_positions_opened':sum(len(r['sampled_source_frame_ids']) for r in cases),'contact_sheets_opened':sum(len(r['timeline_sheets']) for r in cases),'sampled_second_intervals':total_intervals,'native_stills_opened':sum(map(len,NATIVE_CHECKS.values())),'fully_manually_reviewed_sources':0,'continuous_audio_listened_sources':0,'scope':'First-pass one-second sampled visual observations plus numerical audiovisual audit; not full frame-by-frame perceptual/audio review'}
 for dest in [a.out,a.public_evidence]:(dest/'review-status.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(manifest,indent=2));print(a.out/'ACTUAL-FOOTAGE-FIRST-PASS.md')
if __name__=='__main__':main()
