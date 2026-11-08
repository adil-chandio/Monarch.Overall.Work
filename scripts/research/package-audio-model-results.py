"""Package model-derived audio evidence without publishing verbatim source transcripts."""
import argparse,csv,json,math
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def summarize(case):
 words=[w for s in case.get('asr_segments',[]) for w in s.get('words',[])]
 duration=case.get('decoded_audio_seconds',0);labels=defaultdict(list)
 for window in case.get('event_windows',[]):
  for label in window['labels']:labels[label['label']].append((label['model_score'],window['start'],window['end']))
 suspicious=[];prev=0
 for i,w in enumerate(words):
  if w['start']<-.1 or w['end']<w['start'] or w['end']>duration+.5 or w['start']<prev-.1:suspicious.append(i)
  prev=w['end']
 return {'key':case['key'],'status':case['status'],'encoded_audio_matches_local':case.get('encoded_audio_matches_local',False),'source_audio_verified':case.get('source_audio_verified',case.get('encoded_audio_matches_local',False)),'input_association_method':case.get('input_association_method','exact_encoded_audio_packet_hash'),'pcm_sha256_matches_local':case.get('pcm_sha256_matches_local'),'decoded_audio_seconds':duration,'asr_word_count':len(words),'asr_segment_count':len(case.get('asr_segments',[])),'words_per_full_clip_minute_MODEL_DERIVED':len(words)*60/duration if duration else None,'words_with_model_score_below_0_8':sum(w['probability']<.8 for w in words),'timestamp_review_word_indices':suspicious,'first_model_word_start':words[0]['start'] if words else None,'last_model_word_end':words[-1]['end'] if words else None,'event_window_count':len(case.get('event_windows',[])),'top_candidate_labels_NOT_confirmed':[{'label':k,'peak_model_score':max(x[0] for x in v),'number_of_top5_windows':len(v),'first_window_start':min(x[1] for x in v),'last_window_end':max(x[2] for x in v)} for k,v in sorted(labels.items(),key=lambda kv:max(x[0] for x in kv[1]),reverse=True)[:10]],'continuous_perceptual_listening':False,'word_alignment_manually_verified':False,'sound_effects_music_verified':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True,help='Explicit authenticated private result JSON; use combined-ten input for final report');a=p.parse_args();data=json.loads(a.input.read_text())
 out=ROOT/'docs/research/zack-original-access/actual-editions-evidence/third-pass';out.mkdir(exist_ok=True);private=ROOT/'reports-private/reference-forensics/zack-ten/audio-models'
 results=[]
 for case in data['cases']:
  r=summarize(case);results.append(r)
  if case['status']!='model_analysis_complete':continue
  if not r['source_audio_verified']:raise ValueError('Reject unverified source-audio association')
  if r['input_association_method']=='authenticated_local_PCM_transfer':
   if case.get('pcm_sha256_matches_local') is not True or case.get('encoded_audio_matches_local') is not None:raise ValueError('Reject unproven PCM association or conflated encoded hash claim')
  elif r['input_association_method']!='exact_encoded_audio_packet_hash' or case.get('encoded_audio_matches_local') is not True:raise ValueError('Reject unsupported audio source association')
  d=private/case['key'];d.mkdir(parents=True,exist_ok=True)
  words=[{**w,'segment_index':i,'review_status':'ASR_model_output_not_human_corrected'} for i,s in enumerate(case['asr_segments']) for w in s.get('words',[])]
  if words:
   with (d/'narration-words-MODEL-ONLY.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(words[0]),lineterminator='\n');w.writeheader();w.writerows(words)
  (d/'event-windows-MODEL-CANDIDATES.json').write_text(json.dumps(case['event_windows'],indent=2)+'\n')
 summary={'production_hold':True,'asr_model':data['asr_model'],'event_model':data['event_model'],'input_association':'Eight directly re-fetched exact encoded-audio hash matches; remaining originals may use authenticated encrypted local PCM, tied to original MP4 and encoded-audio hashes plus exact PCM integrity. Inspect per-case method; not a title/transcript substitute','model_analyzed_sources':sum(x['status']=='model_analysis_complete' and x['source_audio_verified'] for x in results),'total_asr_words_MODEL_DERIVED':sum(x['asr_word_count'] for x in results),'total_event_windows_MODEL_DERIVED':sum(x['event_window_count'] for x in results),'continuous_perceptual_listened_sources':0,'fully_manual_audiovisual_reviews_complete':0,'limits':[data['alignment_limit'],data['event_parameters']['limits'],'ASR may mistranscribe names, terms, punctuation and boundaries; model score is not calibrated correctness probability','Event windows overlap. Count is not a count of discrete sound effects; labels are not verified stems or music identities','No full verbatim source transcripts published; raw model outputs and word ledgers remain private/ignored'],'cases':results}
 (out/'audio-model-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(private/'model-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 text=['# Actual soundtrack model evidence — NOT verified listening','',f"Source-verified actual soundtracks analyzed: **{summary['model_analyzed_sources']}/10**. ASR words: **{summary['total_asr_words_MODEL_DERIVED']}**. Overlapping audio-event windows: **{summary['total_event_windows_MODEL_DERIVED']}**.",'','Models: `'+summary['asr_model']+'` and `'+summary['event_model']+'`. Speech-to-text and broad AudioSet labels are model-derived aids, not perceptual listening, isolated stems, precise SFX timing or verified music identification.','', '| Case | Seconds | ASR words | ASR words/full-clip minute | Word scores <0.8 | Event windows |','|---|---:|---:|---:|---:|---:|']
 for r in results:
  rate=r['words_per_full_clip_minute_MODEL_DERIVED'];rate=f'{rate:.1f}' if rate is not None else 'unavailable'
  text.append(f"| {r['key']} | {r['decoded_audio_seconds']:.3f} | {r['asr_word_count']} | {rate} | {r['words_with_model_score_below_0_8']} | {r['event_window_count']} |")
 for r in results:
  text+=['',f"## {r['key']}",f"Status: `{r['status']}`; source audio verified: `{r['source_audio_verified']}`; method: `{r['input_association_method']}`; direct remote encoded-audio comparison: `{r['encoded_audio_matches_local']}`.",f"Model first-word start: {r['first_model_word_start']}s; last-word end: {r['last_model_word_end']}s. Timestamp-review indices: {r['timestamp_review_word_indices']}.",'','Broad candidate labels (top five labels per overlapping window; scores not calibrated truth):']
  for label in r['top_candidate_labels_NOT_confirmed'][:6]:text.append(f"- {label['label']}: peak model score {label['peak_model_score']:.4f}; appears in {label['number_of_top5_windows']} top-five windows. This does not establish an audible event at an exact timestamp.")
 text+=['','## Required verification','',*['- '+x for x in summary['limits']],'','Raw narration word timing and event-window outputs remain private for correction against source captions and an actual listening-capable review. Do not claim this model pass completes the requested ten-video forensic study. No production was performed.']
 (out/'AUDIO-MODEL-EVIDENCE.md').write_text('\n'.join(text).rstrip()+'\n')
 print(json.dumps({k:summary[k] for k in ['model_analyzed_sources','total_asr_words_MODEL_DERIVED','total_event_windows_MODEL_DERIVED','continuous_perceptual_listened_sources']},indent=2))
if __name__=='__main__':main()
