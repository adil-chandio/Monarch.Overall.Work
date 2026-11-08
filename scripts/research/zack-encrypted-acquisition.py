"""Acquire public creator editions for private criticism/research, not production.
A public-key envelope protects full references in transit through the only reachable
Git host. The private key NEVER leaves the local ignored research directory.
No cookies, proxying, private endpoints, DRM workarounds or purchased APIs.
"""
import base64,datetime,hashlib,json,os,re,subprocess,sys,tempfile
from pathlib import Path
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'refs/research-transfer';OUT.mkdir(parents=True,exist_ok=True)
PUB=(OUT/'public.pem').read_bytes();PUBLIC=serialization.load_pem_public_key(PUB)
X='https://x.com/zackdfilms1/status/'
CASES=[('01-hearts',X+'1823736339659153776','x'),('02-stomach',X+'1857136424488976883','x'),
 ('03-splinter',X+'1886445157882401091','x'),('04-balloon',X+'1867208307653353881','x'),
 ('05-surfer',X+'1885327753261597019','x'),('06-concert',X+'1898041569250263526','x'),
 ('07-balcony',X+'2048825183453020551','x'),('08-ai',X+'2073754464993841303','x'),
 ('09-fight',X+'1897724425086120113','x'),
 ('10-jerboa','https://www.facebook.com/zackdfilms/videos/what-is-a-jerboa-/2330611454420496/','facebook')]
def clean(s):return re.sub(r'https?://\S+','[URL]',str(s))[-1500:]
def run(args,timeout=150):return subprocess.run(args,capture_output=True,text=True,timeout=timeout)
report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'production_hold':True,
 'purpose':'Actual audiovisual acquisition for private source study; NOT completed manual forensic review',
 'public_key_sha256':hashlib.sha256(PUB).hexdigest(),
 'edition_limit':'X and Facebook publisher editions, NOT assumed byte-identical to YouTube cuts or the earlier ten-ID cohort',
 'x_account_attribution':'@zackdfilms1 is corroborated by Wikitubia, its self-described verified profile and matching five latest official YouTube/X titles; not a primary Linktree cross-link',
 'x_identity_sources':['https://youtube.fandom.com/wiki/Zack_D._Films','https://x.com/zackdfilms1','https://www.youtube.com/@zackdfilms/about'],
 'facebook_identity_source':'https://linktr.ee/zackdfilmsofficial',
 'privacy':'Only AES-256-GCM ciphertext and RSA-OAEP-wrapped per-file keys transferred; no plaintext competitor clips or private decryption key committed',
 'cases':[]}
used=0;route_denied=set()
for key,url,platform in CASES:
 row={'key':key,'source_url':url,'platform':platform,'full_frame_manual_review':False,'continuous_audio_review':False}
 try:
  if platform in route_denied:
   row['status']='not_attempted_after_route_denial';report['cases'].append(row);continue
  with tempfile.TemporaryDirectory(prefix='reference-') as tmp:
   folder=Path(tmp)
   p=run([sys.executable,'-m','yt_dlp','--no-playlist','--no-progress','--write-info-json',
    '--socket-timeout','15','--retries','0','--extractor-retries','0','--js-runtimes','node',
    '--max-filesize','40M','-f','bestvideo[width<=?1080]+bestaudio/best[width<=?1080]',
    '--merge-output-format','mp4','-o',tmp+'/source.%(ext)s',url])
   if p.returncode:
    row.update(status='media_retrieval_failed',diagnostic=clean(p.stderr))
    if any(x in row['diagnostic'].lower() for x in ['http error 403','http error 429','not a bot','login required','sign in']):route_denied.add(platform)
   else:
    info=json.loads((folder/'source.info.json').read_text())
    row['publisher_metadata']={k:info.get(k) for k in ['id','title','uploader','uploader_id','channel_id','duration','webpage_url','format_id']}
    expected='zackdfilms1' if platform=='x' else '100089194705401'
    row['uploader_matches_expected_account']=str(info.get('uploader_id','')).lower()==expected
    if not row['uploader_matches_expected_account']:row['status']='excluded_uploader_mismatch'
    elif not 5<=float(info.get('duration') or 0)<=180:row['status']='excluded_duration'
    else:
     files=[f for f in folder.glob('source.*') if f.suffix in ['.mp4','.mkv','.webm'] and '.f' not in f.stem]
     if len(files)!=1:raise ValueError('No unique complete source file')
     media=files[0];p=run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(media)],100)
     if p.returncode:raise ValueError('Full probe failed')
     data=json.loads(p.stdout)
     row['streams']=[{k:s.get(k) for k in ['codec_type','codec_name','width','height','avg_frame_rate','nb_read_frames','duration','sample_rate','channels']} for s in data.get('streams',[])]
     if not {'audio','video'}<={s['codec_type'] for s in row['streams']}:raise ValueError('Missing audiovisual track')
     p=run(['ffmpeg','-v','error','-xerror','-i',str(media),'-map','0:v:0','-map','0:a:0','-f','null','-'],120)
     if p.returncode:raise ValueError('Full audiovisual decode failed: '+clean(p.stderr))
     raw=media.read_bytes();row.update(status='av_acquired_and_decoded',plaintext_bytes=len(raw),plaintext_sha256=hashlib.sha256(raw).hexdigest(),decode_exit=0)
     if used+len(raw)>80*1024*1024:
      row['transfer_status']='not_transferred_budget_limit'
     else:
      symmetric=AESGCM.generate_key(bit_length=256);nonce=os.urandom(12)
      ciphertext=AESGCM(symmetric).encrypt(nonce,raw,key.encode())
      wrapped=PUBLIC.encrypt(symmetric,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
      name=key+media.suffix+'.enc';(OUT/name).write_bytes(ciphertext)
      row['envelope']={'file':name,'cipher':'AES-256-GCM','key_wrap':'RSA-OAEP-SHA256','nonce_b64':base64.b64encode(nonce).decode(),
       'wrapped_key_b64':base64.b64encode(wrapped).decode(),'aad':key,'ciphertext_sha256':hashlib.sha256(ciphertext).hexdigest(),
       'decrypted_filename':key+media.suffix}
      row['transfer_status']='encrypted_for_local_private_research';used+=len(raw)
 except Exception as e:row.update(status='test_error',diagnostic=clean(type(e).__name__+': '+str(e)))
 report['cases'].append(row)
 report['av_acquired_and_decoded_count']=sum(x.get('status')=='av_acquired_and_decoded' for x in report['cases'])
 report['encrypted_transfer_count']=sum('envelope' in x for x in report['cases'])
 report['plaintext_total_transferred_bytes']=used
 (OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 print(key,row['status'],row.get('transfer_status',''),flush=True)
