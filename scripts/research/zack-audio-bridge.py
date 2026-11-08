"""Bounded ephemeral-key bridge for the two original local soundtracks.
Runner private key exists only in this process, never committed/transferred. Local
source PCM arrives encrypted, gets model-analyzed, results encrypted to LOCAL pubkey.
No perceptual-listening claim; no production; no public playable audio/transcripts.
"""
import base64,hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
import numpy as np
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
ROOT=Path(__file__).resolve().parents[2];BRANCH='arena/ba8d901e-monarch-overall-work';OUT=ROOT/'refs/research-audio-bridge';OUT.mkdir(parents=True,exist_ok=True)
def run(args,check=True):return subprocess.run(args,capture_output=True,check=check,timeout=90)
def main():
 runid=os.environ['GITHUB_RUN_ID'];private=rsa.generate_private_key(public_exponent=65537,key_size=3072);pub=private.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo);pubhash=hashlib.sha256(pub).hexdigest()
 (OUT/'receiver-public.pem').write_bytes(pub);(OUT/'receiver.json').write_text(json.dumps({'run_id':runid,'public_key_sha256':pubhash,'allowed_source_keys':['02-stomach','08-ai'],'production_hold':True,'private_key_location':'runner process memory only','wait_seconds':600},indent=2)+'\n')
 run(['git','add','refs/research-audio-bridge/receiver-public.pem','refs/research-audio-bridge/receiver.json']);run(['git','commit','-m','Publish ephemeral audio-analysis recipient public key [skip ci]']);run(['git','pull','--rebase','origin',BRANCH]);run(['git','push','origin','HEAD:'+BRANCH]);print('Ephemeral receiver public key published; waiting for encrypted local input',flush=True)
 deadline=time.monotonic()+600;upload=None
 while time.monotonic()<deadline:
  run(['git','fetch','origin',BRANCH]);p=run(['git','show','FETCH_HEAD:refs/research-audio-bridge/upload-manifest.json'],check=False)
  if p.returncode==0:
   candidate=json.loads(p.stdout)
   if str(candidate.get('receiver_run_id'))==runid and candidate.get('receiver_public_key_sha256')==pubhash:upload=candidate;break
  time.sleep(15)
 if upload is None:raise TimeoutError('No current-recipient encrypted upload received within bounded wait')
 expected=json.loads((ROOT/'docs/research/zack-original-access/encoded-audio-hashes.json').read_text());sources={r['key']:r for r in json.loads((ROOT/'refs/research-transfer/manifest.json').read_text())['cases']}
 spec=importlib.util.spec_from_file_location('audio',ROOT/'scripts/research/zack-audio-model-analysis.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 resultdir=OUT/'results';resultdir.mkdir(exist_ok=True);m.OUT=resultdir
 report={'production_hold':True,'asr_model':'Systran/faster-whisper-base.en','event_model':'MIT/ast-finetuned-audioset-10-10-0.4593','event_parameters':{'window_seconds':10,'stride_seconds':5,'limits':'Overlapping broad AudioSet model candidates, not calibrated certainty, listening, stems or exact SFX timings.'},'alignment_limit':'Times relative to locally decoded 16kHz mono PCM; model alignment not human-corrected or certified frame-accurate.','receiver_run_id':runid,'perceptual_audio_listening':False,'cases':[]}
 try:
  import torch
  from faster_whisper import WhisperModel
  from transformers import AutoFeatureExtractor,ASTForAudioClassification
  torch.set_num_threads(2);asr=WhisperModel('base.en',device='cpu',compute_type='int8',cpu_threads=2,num_workers=1);feature=AutoFeatureExtractor.from_pretrained(report['event_model']);events=ASTForAudioClassification.from_pretrained(report['event_model']).eval()
  for row in upload['cases']:
   key=row['key'];r={'key':key,'source_url':sources[key]['source_url'],'perceptually_listened':False,'transcription_human_verified':False,'effects_music_human_verified':False,'input_association_method':'authenticated_local_PCM_transfer','encoded_audio_matches_local':None}
   try:
    if key not in ['02-stomach','08-ai'] or row['source_mp4_sha256']!=sources[key]['plaintext_sha256'] or row['source_encoded_audio_hash']!=expected[key]:raise ValueError('Original source provenance mismatch')
    e=row['envelope'];name=e['file']
    if Path(name).name!=name:raise ValueError('Unsafe ciphertext filename')
    cipher=run(['git','show','FETCH_HEAD:refs/research-audio-bridge/'+name]).stdout
    if hashlib.sha256(cipher).hexdigest()!=e['ciphertext_sha256']:raise ValueError('Ciphertext mismatch')
    aad=runid+':'+key+':'+row['pcm_sha256']
    if e['aad']!=aad:raise ValueError('Input binding mismatch')
    symmetric=private.decrypt(base64.b64decode(e['wrapped_key_b64']),padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None));raw=AESGCM(symmetric).decrypt(base64.b64decode(e['nonce_b64']),cipher,aad.encode())
    if hashlib.sha256(raw).hexdigest()!=row['pcm_sha256'] or len(raw)!=row['pcm_bytes']:raise ValueError('PCM integrity mismatch')
    audio=np.frombuffer(raw,dtype='<i2').astype(np.float32)/32768.;r.update(source_audio_verified=True,pcm_sha256_matches_local=True,source_mp4_sha256=row['source_mp4_sha256'],source_encoded_audio_hash=row['source_encoded_audio_hash'],pcm_sha256=row['pcm_sha256'],decoded_audio_seconds=len(audio)/16000)
    segments,_=asr.transcribe(audio,language='en',beam_size=5,word_timestamps=True,vad_filter=False,condition_on_previous_text=False)
    r['asr_segments']=[{'start':s.start,'end':s.end,'text':s.text,'avg_logprob':s.avg_logprob,'no_speech_prob':s.no_speech_prob,'compression_ratio':s.compression_ratio,'words':[{'start':w.start,'end':w.end,'text':w.word,'probability':float(w.probability),'low_score_review_candidate':bool(w.probability<.8)} for w in (s.words or [])]} for s in segments]
    r['event_windows']=[]
    for start in range(0,len(audio),5*16000):
     clip=audio[start:start+10*16000];inputs=feature(clip,sampling_rate=16000,return_tensors='pt')
     with torch.inference_mode():scores=events(**inputs).logits[0].sigmoid();values,ids=torch.topk(scores,5)
     r['event_windows'].append({'start':start/16000,'end':min(start+10*16000,len(audio))/16000,'labels':[{'label':events.config.id2label[int(i)],'model_score':float(v),'status':'model_candidate_not_confirmed'} for v,i in zip(values,ids)]})
    r.update(status='model_analysis_complete',asr_word_count=sum(len(s['words']) for s in r['asr_segments']),event_window_count=len(r['event_windows']))
   except Exception as e:r.update(status='analysis_failed',diagnostic=m.clean(e))
   report['cases'].append(r);print(key,r['status'],flush=True)
 except Exception as e:report['setup_error']=m.clean(e)
 envelope=m.envelope(json.dumps(report,indent=2,default=m.json_native).encode())
 manifest={'production_hold':True,'public_key_sha256':hashlib.sha256(m.PUB).hexdigest(),'receiver_run_id':runid,'model_analyzed_case_count':sum(r.get('status')=='model_analysis_complete' for r in report['cases']),'perceptual_audio_listening':False,'cases':[envelope]}
 (resultdir/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
