"""Encrypt the user-supplied source and temporarily transfer it via unreferenced Git blobs.
The public key is per-run; the private key stays in the local workspace cache.
The public repository receives only ciphertext and a wrapped random password.
"""
import base64,hashlib,json,os,subprocess,tempfile,urllib.request
from pathlib import Path
root=Path(os.environ['RUNNER_TEMP']);source=root/'source.mp4';encrypted=root/'source.enc';password=root/'pass';wrapped=root/'pass.enc'
password.write_text(os.urandom(32).hex());os.chmod(password,0o600)
subprocess.run(['openssl','enc','-aes-256-cbc','-salt','-pbkdf2','-iter','200000','-in',str(source),'-out',str(encrypted),'-pass','file:'+str(password)],check=True)
subprocess.run(['openssl','pkeyutl','-encrypt','-pubin','-inkey','scripts/forensic/transfer-public.pem','-in',str(password),'-out',str(wrapped),'-pkeyopt','rsa_padding_mode:oaep','-pkeyopt','rsa_oaep_md:sha256'],check=True)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
manifest={'description':'Encrypted unreferenced Git blobs for temporary transport. Original video and decryption key are not committed.','source_sha256':digest(source),'encrypted_sha256':digest(encrypted),'source_bytes':source.stat().st_size,'wrapped_password_base64':base64.b64encode(wrapped.read_bytes()).decode(),'chunks':[]}
token=os.environ['GH_TOKEN'];api='https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY']+'/git/blobs'
with encrypted.open('rb') as f:
 while True:
  data=f.read(40*1024*1024)
  if not data:break
  req=urllib.request.Request(api,data=json.dumps({'content':base64.b64encode(data).decode(),'encoding':'base64'}).encode(),headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json','X-GitHub-Api-Version':'2022-11-28'},method='POST')
  with urllib.request.urlopen(req,timeout=180) as res: result=json.load(res)
  manifest['chunks'].append({'sha':result['sha'],'size':len(data),'sha256':hashlib.sha256(data).hexdigest()});print('Transferred encrypted chunk',len(manifest['chunks']),flush=True)
Path('docs/repo-intel/encrypted-screen-transfer.json').write_text(json.dumps(manifest,indent=2)+'\n')
password.unlink();wrapped.unlink();encrypted.unlink()
