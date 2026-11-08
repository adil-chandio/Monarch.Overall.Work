"""Local-only authenticated decryption of private research inputs. Never prints keys."""
import argparse,base64,hashlib,json
from pathlib import Path
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--transfer-dir',type=Path,required=True);ap.add_argument('--private-key',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 m=json.loads((a.transfer_dir/'manifest.json').read_text());private=serialization.load_pem_private_key(a.private_key.read_bytes(),password=None)
 pub=private.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo)
 if hashlib.sha256(pub).hexdigest()!=m['public_key_sha256']:raise ValueError('Local key does not match research-transfer recipient')
 a.out.mkdir(parents=True,exist_ok=True);result=[]
 for row in m['cases']:
  if 'envelope' not in row:continue
  e=row['envelope']
  for field in ['file','decrypted_filename']:
   if Path(e[field]).name!=e[field]:raise ValueError('Unexpected source filename')
  if e['aad']!=row['key']:raise ValueError('Envelope/source mismatch')
  data=(a.transfer_dir/e['file']).read_bytes()
  if hashlib.sha256(data).hexdigest()!=e['ciphertext_sha256']:raise ValueError('Ciphertext checksum mismatch')
  symmetric=private.decrypt(base64.b64decode(e['wrapped_key_b64']),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
  raw=AESGCM(symmetric).decrypt(base64.b64decode(e['nonce_b64']),data,e['aad'].encode())
  if hashlib.sha256(raw).hexdigest()!=row['plaintext_sha256']:raise ValueError('Decrypted source checksum mismatch')
  target=a.out/e['decrypted_filename'];target.write_bytes(raw)
  result.append({'key':row['key'],'file':target.name,'bytes':len(raw),'sha256':row['plaintext_sha256'],'source_url':row['source_url'],'publisher_metadata':row['publisher_metadata']})
  print(row['key'],'authenticated source restored',len(raw),'bytes')
 (a.out/'local-source-manifest.json').write_text(json.dumps({'production_hold':True,'local_actual_source_count':len(result),'sources':result},indent=2)+'\n')
if __name__=='__main__':main()
