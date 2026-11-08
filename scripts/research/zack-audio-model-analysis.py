"""Actual-audio model analysis on a runner with model access. NOT perceptual listening.
Public ordinary source re-fetch; exact encoded-audio hash gate; encrypted results only.
No plaintext media/transcripts published, no private key used, no video production.
"""
import base64,datetime,hashlib,json,os,re,subprocess,sys,tempfile
from pathlib import Path
from importlib.metadata import version
import numpy as np
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'refs/research-audio-models';OUT.mkdir(parents=True,exist_ok=True)
PUB=(ROOT/'refs/research-transfer/public.pem').read_bytes()
EXPECTED=json.loads((ROOT/'docs/research/zack-original-access/encoded-audio-hashes.json').read_text())
SOURCES=json.loads((ROOT/'refs/research-transfer/manifest.json').read_text())['cases']

def run(args,timeout=180):return subprocess.run(args,capture_output=True,timeout=timeout,check=True)
def clean(e):
 if isinstance(e,subprocess.CalledProcessError):text=(e.stderr or b'').decode(errors='replace')
 else:text=type(e).__name__+': '+str(e)
 return re.sub(r'https?://\S+','[URL]',text)[-1400:]
def envelope(raw):
 key='ten-audio-model-results';symmetric=AESGCM.generate_key(bit_length=256);nonce=os.urandom(12)
 data=AESGCM(symmetric).encrypt(nonce,raw,key.encode());public=serialization.load_pem_public_key(PUB)
 wrapped=public.encrypt(symmetric,padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
 name=key+'.json.enc';(OUT/name).write_bytes(data)
 return {'key':key,'source_url':'https://github.com/adil-chandio/Monarch.Overall.Work/actions','publisher_metadata':{},'plaintext_sha256':hashlib.sha256(raw).hexdigest(),'envelope':{'file':name,'decrypted_filename':key+'.json','aad':key,'ciphertext_sha256':hashlib.sha256(data).hexdigest(),'nonce_b64':base64.b64encode(nonce).decode(),'wrapped_key_b64':base64.b64encode(wrapped).decode()}}

def main():
 report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'production_hold':True,'perceptual_audio_listening':False,'purpose':'Model-derived transcription and broad audio-event candidates from exact source soundtracks; NOT verified listening or a complete forensic review','asr_model':'Systran/faster-whisper-base.en','asr_parameters':{'device':'cpu','compute_type':'int8','beam_size':5,'language':'en','word_timestamps':True,'vad_filter':False},'event_model':'MIT/ast-finetuned-audioset-10-10-0.4593','event_parameters':{'window_seconds':10,'stride_seconds':5,'top_labels':5,'activation':'sigmoid','limits':'Multi-label model scores are not calibrated confidence, source stems or exact event timings; coarse overlapping windows, possible false positives/negatives.'},'alignment_limit':'ASR word/window times relative to decoded mono 16kHz WAV, not human-corrected or guaranteed frame-accurate. Container start times recorded for review.','packages':{n:version(n) for n in ['faster-whisper','transformers','torch','yt-dlp']},'cases':[]}
 public={'production_hold':True,'perceptual_audio_listening':False,'model_setup_status':'not_attempted','cases':[]}
 def save():
  raw=json.dumps(report,indent=2).encode();row=envelope(raw)
  public['analyzed_case_count']=sum(r.get('status')=='model_analysis_complete' for r in report['cases'])
  public['same_encoded_audio_case_count']=sum(r.get('encoded_audio_matches_local') is True for r in report['cases'])
  public['public_key_sha256']=hashlib.sha256(PUB).hexdigest();public['cases']=[row]
  public['case_statuses']=[{k:r.get(k) for k in ['key','status','encoded_audio_matches_local','asr_segment_count','asr_word_count','event_window_count','diagnostic']} for r in report['cases']]
  (OUT/'manifest.json').write_text(json.dumps(public,indent=2)+'\n')
 try:
  import torch
  from faster_whisper import WhisperModel
  from transformers import AutoFeatureExtractor,ASTForAudioClassification
  torch.set_num_threads(2)
  asr=WhisperModel('base.en',device='cpu',compute_type='int8',cpu_threads=2,num_workers=1)
  feature=AutoFeatureExtractor.from_pretrained(report['event_model'])
  events=ASTForAudioClassification.from_pretrained(report['event_model']).eval()
  report['resolved_event_model_commit']=getattr(events.config,'_commit_hash',None)
  public['model_setup_status']='both_models_loaded';print('Both audio models loaded',flush=True)
 except Exception as e:
  public['model_setup_status']='failed';report['setup_error']=clean(e);save();print('Audio model setup failed; result encrypted',flush=True);return
 denied=set()
 for source in SOURCES:
  key=source['key'];platform=source['platform'];r={'key':key,'source_url':source['source_url'],'perceptually_listened':False,'transcription_human_verified':False,'effects_music_human_verified':False}
  try:
   if platform in denied:r['status']='not_attempted_after_platform_denial'
   else:
    with tempfile.TemporaryDirectory(prefix='audio-research-') as tmp:
     folder=Path(tmp)
     try:
      run([sys.executable,'-m','yt_dlp','--no-playlist','--no-progress','--write-info-json','--socket-timeout','15','--retries','0','--extractor-retries','0','--js-runtimes','node','--max-filesize','40M','-f','bestvideo[width<=?1080]+bestaudio/best[width<=?1080]','--merge-output-format','mp4','-o',tmp+'/source.%(ext)s',source['source_url']])
     except subprocess.CalledProcessError as e:
      diagnostic=clean(e)
      if any(s in diagnostic.lower() for s in ['403','429','not a bot','sign in','login required']):denied.add(platform)
      raise
     info=json.loads((folder/'source.info.json').read_text());expected='zackdfilms1' if platform=='x' else '100089194705401'
     if str(info.get('uploader_id','')).lower()!=expected:raise ValueError('Uploader mismatch')
     files=[p for p in folder.glob('source.*') if p.suffix in ['.mp4','.mkv','.webm'] and '.f' not in p.stem]
     if len(files)!=1:raise ValueError('No unique merged media file')
     media=files[0]
     encoded=run(['ffmpeg','-v','error','-i',str(media),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).stdout.decode().strip()
     r.update(encoded_audio_hash=encoded,encoded_audio_matches_local=encoded==EXPECTED[key],retrieved_format_id=info.get('format_id'))
     if not r['encoded_audio_matches_local']:raise ValueError('Exact encoded-audio hash mismatch: analysis withheld rather than assigned to old source')
     probe=json.loads(run(['ffprobe','-v','error','-show_streams','-of','json',str(media)]).stdout)
     r['stream_starts']=[{k:s.get(k) for k in ['codec_type','start_time','duration','sample_rate']} for s in probe['streams']]
     pcm=run(['ffmpeg','-v','error','-i',str(media),'-vn','-ac','1','-ar','16000','-f','s16le','-']).stdout
     audio=np.frombuffer(pcm,dtype='<i2').astype(np.float32)/32768.;r['decoded_audio_seconds']=len(audio)/16000
     segments,meta=asr.transcribe(audio,language='en',beam_size=5,word_timestamps=True,vad_filter=False,condition_on_previous_text=False)
     r['asr_segments']=[]
     for s in segments:
      r['asr_segments'].append({'start':s.start,'end':s.end,'text':s.text,'avg_logprob':s.avg_logprob,'no_speech_prob':s.no_speech_prob,'compression_ratio':s.compression_ratio,'words':[{'start':w.start,'end':w.end,'text':w.word,'probability':w.probability,'low_score_review_candidate':w.probability<.8} for w in (s.words or [])]})
     r['event_windows']=[]
     for start in range(0,len(audio),5*16000):
      clip=audio[start:start+10*16000]
      inputs=feature(clip,sampling_rate=16000,return_tensors='pt')
      with torch.inference_mode():scores=events(**inputs).logits[0].sigmoid();values,ids=torch.topk(scores,5)
      r['event_windows'].append({'start':start/16000,'end':min(start+10*16000,len(audio))/16000,'labels':[{'label':events.config.id2label[int(i)],'model_score':float(v),'status':'model_candidate_not_confirmed'} for v,i in zip(values,ids)]})
     r.update(status='model_analysis_complete',asr_segment_count=len(r['asr_segments']),asr_word_count=sum(len(s['words']) for s in r['asr_segments']),event_window_count=len(r['event_windows']))
  except Exception as e:r.update(status='analysis_failed',diagnostic=clean(e))
  report['cases'].append(r);save();print(key,r['status'],r.get('asr_word_count',0),'model words',flush=True)
 save()
if __name__=='__main__':main()
