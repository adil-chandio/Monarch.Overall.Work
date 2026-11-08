"""LOCAL ONLY: merge eight hash-matched results with two provenance-bound PCM results."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 private=ROOT/'reports-private/reference-forensics/zack-ten'
 a=json.loads((private/'audio-models/ten-audio-model-results.json').read_text());b=json.loads((private/'audio-bridge/ten-audio-model-results.json').read_text())
 upload=json.loads((ROOT/'refs/research-audio-bridge/upload-manifest.json').read_text());uploads={r['key']:r for r in upload['cases']}
 if str(b['receiver_run_id'])!=str(upload['receiver_run_id']):raise ValueError('Wrong bridge session')
 if a['asr_model']!=b['asr_model'] or a['event_model']!=b['event_model']:raise ValueError('Model names differ; cannot silently combine')
 result={r['key']:r for r in a['cases']}
 for row in b['cases']:
  u=uploads.get(row['key'])
  if u is None or row.get('status')!='model_analysis_complete' or not row.get('source_audio_verified') or not row.get('pcm_sha256_matches_local'):raise ValueError('Unverified bridge result')
  for field,sourcefield in [('pcm_sha256','pcm_sha256'),('source_mp4_sha256','source_mp4_sha256'),('source_encoded_audio_hash','source_encoded_audio_hash')]:
   if row[field]!=u[sourcefield]:raise ValueError('Bridge provenance field mismatch: '+field)
  if abs(row['decoded_audio_seconds']-u['pcm_bytes']/32000)>1/16000:raise ValueError('PCM duration mismatch')
  result[row['key']]=row
 expected=json.loads((ROOT/'docs/research/zack-original-access/encoded-audio-hashes.json').read_text())
 for key,row in result.items():
  actual=row.get('source_encoded_audio_hash') if row.get('input_association_method')=='authenticated_local_PCM_transfer' else row.get('encoded_audio_hash')
  if actual!=expected.get(key):raise ValueError('Expected original encoded-audio provenance mismatch')
 if set(result)!=set(expected) or any(r['status']!='model_analysis_complete' or not r.get('source_audio_verified',r.get('encoded_audio_matches_local',False)) for r in result.values()):raise ValueError('Not ten verified model-complete soundtracks')
 merged={**a,'cases':[result[k] for k in sorted(result)],'bridge_receiver_run_id':b['receiver_run_id'],'provenance_runs':['42452351652','42452846962'],'input_association_limit':'Eight exact encoded-audio packet matches on re-fetch; two originally acquired local MP4s checked by MP4 hash and encoded-audio hash, then their derived 16kHz mono s16 PCM transferred with ephemeral-recipient RSA-OAEP/AES-GCM, verified against exact PCM hash. PCM reduction is not original full-band stereo fidelity.','perceptual_audio_listening':False,'model_revision_limit':'Model names and inference code recorded; do not assume independently pinned/identical model-weight revisions for both jobs.'}
 target=private/'audio-models/combined-ten-audio-model-results.json';target.write_text(json.dumps(merged,indent=2)+'\n');print('Merged ten verified model-derived soundtrack records; perceptual listening remains false')
if __name__=='__main__':main()
