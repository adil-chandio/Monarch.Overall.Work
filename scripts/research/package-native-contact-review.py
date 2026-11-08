#!/usr/bin/env python3
"""Derive exact coverage from explicit manual-review attestations, never from extraction."""
import csv,json,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def compile_coverage(base,notes):
 spec=importlib.util.spec_from_file_location('first_pass',ROOT/'scripts/research/build-ten-source-first-pass.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 windows=notes['windows'];full={(k,n) for k,ids in m.NATIVE_CHECKS.items() for n in ids};roi=set();grid=set();ledgers={}
 for p in sorted(base.glob('*/evidence.json')):
  r=json.loads(p.read_text());key=r['key'];grid.update((key,n) for n in r['sampled_source_frame_ids'])
  with (p.parent/'every-frame.csv').open() as f:ledgers[key]=list(csv.DictReader(f))
 for k,ids in notes['additional_full_native_stills_opened'].items():full.update((k,n) for n in ids)
 for w in windows:
  if not w['all_frames_in_this_window_opened'] or w['every_frame_of_source_reviewed'] or w['continuous_audio_listened']:raise ValueError('Inconsistent first dense-pass attestation')
  key=w['key'];start=w['start_frame'];stop=w['end_frame_inclusive']
  if not 0<=start<=stop<len(ledgers[key]):raise ValueError('Out-of-range window')
  target=full if w['scope']=='full_native_stills_individually_opened' else roi
  target.update((key,n) for n in range(start,stop+1))
 rows=[]
 for key,frames in ledgers.items():
  for r in frames:
   pair=key,int(r['frame'])
   rows.append({'key':key,'frame':r['frame'],'source_pts_seconds':r['source_pts_seconds'],'one_second_grid_position_opened':pair in grid,'native_full_still_opened':pair in full,'native_ROI_opened':pair in roi,'source_exhaustive_review_complete':False,'continuous_audio_listened':False})
 status={'production_hold':True,'total_source_frames':len(rows),'one_second_grid_positions_opened':len(grid),'native_full_stills_opened_unique':len(full),'native_ROI_positions_opened_unique':len(roi),'native_ROI_only_not_full_still':len(roi-full),'unique_positions_opened_in_any_visual_scope':len(grid|full|roi),'positions_not_opened_in_any_visual_scope':len(rows)-len(grid|full|roi),'dense_windows':len(windows),'dense_window_frame_positions':sum(w['end_frame_inclusive']-w['start_frame']+1 for w in windows),'fully_manually_reviewed_sources':0,'continuous_audio_listened_sources':0,'warning':'ROI inspection is NOT whole-frame inspection. Full-still opening is NOT certification of all details. No complete source or full audio watch certified.'}
 return rows,status

def main():
 base=ROOT/'docs/research/zack-original-access/actual-editions-evidence';out=base/'second-pass';notes=json.loads((out/'observations.json').read_text());rows,status=compile_coverage(base,notes)
 with (out/'manual-coverage.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
 (out/'review-status.json').write_text(json.dumps(status,indent=2)+'\n')
 parts=['''# Native contact and sub-second review — SECOND PASS, still incomplete

**Production STOPPED. This is a bounded research increment, not the completed ten-source forensic study.**

## What advanced

Ten contiguous critical windows now have explicit scope and adjacent-frame observations. Two windows were inspected as individual full native stills; eight as source-pixel ROI sequences. Splinter was extended through the complete local grasp/withdrawal event, not left at a single sampled pose. Incorrect/insufficient crop selections were identified and corrected, not counted as proof of the missing contact.

**Important limitation:** This interface currently has no established route for me to continuously hear the sources. Mixed audio statistics, caption reading or prospective ASR cannot be relabeled as listening. A public official Whisper model retrieval was tested and failed at its release-asset transport. No model/transcription or SFX/music perceptual audit resulted. The existing Gemini video route also remains denied. Audio review is a real unsolved capability/access blocker, not merely a report section I can truthfully fill with guesses.

## Exact cumulative coverage

Counts below deduplicate source frame numbers, not calls or repeated exports. The 342 contact-sheet sample positions are a different inspection scope from full native stills and ROI sequences; counts must NOT be added blindly.
''']
 parts.extend(f'- **{k}:** {v}' for k,v in status.items() if k not in ['warning','production_hold'])
 parts.append('\n'+status['warning']+'\n\nThe complete requested every-native-frame/perceptual-audio review remains **0/10**. Numerical indexing remains 9,772/9,772.\n')
 for w in notes['windows']:
  parts.extend([f"\n## {w['key']} — f{w['start_frame']}–f{w['end_frame_inclusive']} inclusive",f"\nSource PTS: **{w['first_pts_seconds']:.6f}–{w['last_pts_seconds']:.6f}s**. Scope: `{w['scope']}`. ROI `(left,top,right,bottom)`: `{w['roi_source_pixels']}`. No native frame was skipped within this specified window; everything outside it remains governed by the separate coverage ledger.\n",w['observations']+'\n'])
 parts.append('''
## Revised craft conclusions

- A causal verb can be decomposed into **approach → grip → maintained grip → withdrawal → separated object → resulting state**. Splinter now supplies adjacent-frame evidence for that local sequence, not just a before/after pair. The first clear visible separation is f710; physical contact timing finer than source frames is unavailable.
- **Holding can be meaningful performance.** Balcony support and the held organ have low-motion intervals whose contact relationships explain the situation. More camera motion or cutting is not automatically better.
- **Red anatomical emphasis is a separate explanatory layer from physical impact.** Concert's f93/f94 introduces neck highlighting/transparency within the observed sequence. Do not interpret that rendered effect as measured biological deformation.
- **Context and ROI answer different questions.** A burner-only crop can show flame but cannot certify fingers on controls; tail-only crop cannot establish whole-body counter-rotation. This is why crop failure/correction is recorded.
- The inspected poses do NOT recover exact rigs, collision constraints, keyframes, lenses or renderer settings; no zero-intersection/zero-sliding guarantee is made.

## Corrections and unfinished checks

1. Balloon at the near-7s source sample shows a raised hand at the red burner control, not a demonstrated pull on a separate control line. First-pass sampled wording is corrected. Do not treat this fictional/illustrated safety sequence as verified emergency instructions.
2. Stomach's 9.88–10.14s window shows a held removed organ; it does not cover actual detachment. Tool/attachment separation still needs another window.
3. Surfer's f866–874 is only the beginning of the rise; the rest of the 29–31s change is still sampled, not exhaustively opened.
4. Jerboa's tail-root crop does not validate the angle numbers or body-wide mechanics. Wider sequential native views remain necessary.
5. Subsecond caption changes were observed in the corrected burner crop; this is not word-aligned narration evidence. No sound cue is assigned from visuals.
6. All native frames outside the explicit sets remain unreviewed at that scope. Continuous audio, voice/SFX/music separation by listening and exact sound timings remain uncompleted.

## Evidence/reproduction

- `observations.json`: exact window bounds, ROIs, manual scope, observations and bounded audio-access probe.
- `manual-coverage.csv`: 9,772-row per-frame scope ledger with PTS; separate grid/native-full/native-ROI flags, no exhaustive-source flag set true.
- `review-status.json`: reproducible deduplicated counts.
- `scripts/research/package-native-contact-review.py`: derives these counts from explicit manual attestations and existing frame ledgers, NOT from extracted files.
- `scripts/research/extract-native-contact-windows.py`: source-native window/ROI extraction helper; extraction alone does not certify review.
- Pixel-preserving crop sheets remain PRIVATE/ignored at `reports-private/reference-forensics/zack-ten/contact-windows/`. No source screenshots, plaintext media, audio or private key added to public Git.
- Full source-native PNGs remain cached locally; their source IDs/PTS allow restoration from the encrypted corpus and local key. No replacement animation or synthetic comparison film has been created.
''')
 report='\n'.join(parts).rstrip()+'\n';(out/'SECOND-PASS.md').write_text(report)
 private=ROOT/'reports-private/reference-forensics/zack-ten';(private/'SECOND-PASS.md').write_text(report)
 print(json.dumps(status,indent=2))
if __name__=='__main__':main()
