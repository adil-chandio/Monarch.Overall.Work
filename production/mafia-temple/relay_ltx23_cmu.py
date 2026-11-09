"""Relay only generated video and receipt, never private source media."""
import base64,hashlib,json,os,pathlib,requests
root=pathlib.Path(os.environ['LTX_OUTPUT']); names=['ltx23-cmu-pose.mp4','ltx23-cmu-receipt.json']; files={n:next(root.rglob(n)) for n in names}
r=json.loads(files[names[1]].read_text())
if r.get('status')!='complete_research_only' or r.get('original_photo_used') is not False: raise ValueError('Invalid safety receipt')
if hashlib.sha256(files[names[0]].read_bytes()).hexdigest()!=r.get('output_sha256'): raise ValueError('Video checksum mismatch')
headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'};results=[]
for n,p in files.items():
 data=p.read_bytes()
 if not data or len(data)>30_000_000: raise ValueError('Unexpected output size: '+n)
 resp=requests.post(f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/git/blobs",json={'content':base64.b64encode(data).decode(),'encoding':'base64'},headers=headers,timeout=120);resp.raise_for_status();results.append(n+'='+resp.json()['sha'])
print('::notice title=LTX23 CMU research only::'+','.join(results),flush=True)
