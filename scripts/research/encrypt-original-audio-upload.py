"""LOCAL ONLY: bind original-source PCM to the current ephemeral runner public key.
Does not read/upload the local private key. Never publishes plaintext source audio.
"""
import argparse,base64,hashlib,json,os,subprocess
from pathlib import Path
import imageio_ffmpeg
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-run-id',required=True);a=p.parse_args()
 out=ROOT/'refs/research-audio-bridge';receiver=json.loads((out/'receiver.json').read_text());pub=(out/'receiver-public.pem').read_bytes();pubhash=hashlib.sha256(pub).hexdigest()
 if receiver['run_id']!=a.expected_run_id or receiver['public_key_sha256']!=pubhash:raise ValueError('Stale or mismatched ephemeral recipient')
 public=serialization.load_pem_public_key(pub);sources={x['key']:x for x in json.loads((ROOT/'refs/research-transfer/manifest.json').read_text())['cases']};expected=json.loads((ROOT/'docs/research/zack-original-access/encoded-audio-hashes.json').read_text());rows=[]
 ff=imageio_ffmpeg.get_ffmpeg_exe()
 for key in ['02-stomach','08-ai']:
  source=ROOT/'.cache/reference-forensics/zack-ten/videos'/f'{key}.mp4';sourcehash=hashlib.sha256(source.read_bytes()).hexdigest()
  if sourcehash!=sources[key]['plaintext_sha256']:raise ValueError('Local original MP4 checksum mismatch')
  encoded=subprocess.run([ff,'-v','error','-i',str(source),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],capture_output=True,text=True,check=True).stdout.strip()
  if encoded!=expected[key]:raise ValueError('Original encoded soundtrack mismatch')
  raw=subprocess.run([ff,'-v','error','-i',str(source),'-vn','-ac','1','-ar','16000','-f','s16le','-'],capture_output=True,check=True).stdout
  digest=hashlib.sha256(raw).hexdigest();aad=a.expected_run_id+':'+key+':'+digest;symmetric=AESGCM.generate_key(bit_length=256);nonce=os.urandom(12);cipher=AESGCM(symmetric).encrypt(nonce,raw,aad.encode());wrapped=public.encrypt(symmetric,padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None));name=key+'.pcm.enc';(out/name).write_bytes(cipher)
  rows.append({'key':key,'source_mp4_sha256':sourcehash,'source_encoded_audio_hash':encoded,'pcm_sha256':digest,'pcm_bytes':len(raw),'pcm_format':'16kHz mono signed little-endian int16; relative to decoded source audio start','envelope':{'file':name,'ciphertext_sha256':hashlib.sha256(cipher).hexdigest(),'aad':aad,'nonce_b64':base64.b64encode(nonce).decode(),'wrapped_key_b64':base64.b64encode(wrapped).decode()}})
  print(key,'original PCM encrypted',len(raw),'bytes; no plaintext audio written')
 (out/'upload-manifest.json').write_text(json.dumps({'production_hold':True,'receiver_run_id':a.expected_run_id,'receiver_public_key_sha256':pubhash,'local_private_key_used':False,'cases':rows},indent=2)+'\n')
if __name__=='__main__':main()
