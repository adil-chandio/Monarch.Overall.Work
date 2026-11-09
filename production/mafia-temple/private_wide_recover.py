"""Recover a queued private Kaggle output -> user's private Drive upload session.

No generated media, transfer URLs or credentials are printed or put into Git.
Only an ephemeral RSA public key and a run-bound encrypted capability are
posted to the repository. Reference and pose inputs were already public in
historical commits; this script does not publish additional images or footage.
"""
import base64,hashlib,json,os,pathlib,re,shutil,subprocess,sys,tempfile,time,urllib.error,urllib.request,zipfile
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding,rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

b64=lambda x:base64.b64encode(x).decode('ascii')
unb64=lambda x:base64.b64decode(x,validate=True)
ROOT='https://api.github.com/repos/adil-chandio/Monarch.Overall.Work/contents/production/mafia-temple/'
BRANCH='arena/6101616c-monarch-overall-work'

def api_req(url,method='GET',data=None):
    h={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'}
    if data is not None:h['Content-Type']='application/json';data=json.dumps(data).encode()
    with urllib.request.urlopen(urllib.request.Request(url,data=data,headers=h,method=method),timeout=30) as r:return json.load(r)

def capability():
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    pub=key.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
    run=os.environ['GITHUB_RUN_ID'];fp=hashlib.sha256(pub).hexdigest();endpoint=ROOT+'private-wide-key.json'
    try:old=api_req(endpoint+'?ref='+BRANCH)['sha']
    except urllib.error.HTTPError as e:
        if e.code!=404:raise
        old=None
    obj={'message':'Publish ephemeral private research transfer public key','branch':BRANCH,'content':b64(json.dumps({'run_id':run,'head_sha':os.environ['GITHUB_SHA'],'public_key':b64(pub)}).encode())}
    if old:obj['sha']=old
    api_req(endpoint,'PUT',obj)
    endpoint=ROOT+'private-wide-envelope.json?ref='+BRANCH
    for _ in range(160):
        try:
            obj=api_req(endpoint);v=json.loads(base64.b64decode(obj['content']))
            if v.get('run_id')==run and v.get('public_key_sha256')==fp:
                k=key.decrypt(unb64(v['wrapped_key']),padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
                data=AESGCM(k).decrypt(unb64(v['nonce']),unb64(v['ciphertext']),(run+':'+fp).encode());values=json.loads(data)
                url=values['upload_url']
                if not url.startswith('https://www.googleapis.com/upload/drive/v3/files?'):raise ValueError('Invalid Drive session host')
                return url
        except (urllib.error.HTTPError,KeyError,ValueError):pass
        time.sleep(5)
    raise RuntimeError('Private capability not received')

def kaggle_env():
    raw=os.environ['S_COMPALI'].strip();username='compali'
    if raw.startswith('{'):
        doc=json.loads(raw);raw=doc.get('key') or doc.get('token');username=doc.get('username') or username
    elif ':' in raw and not raw.startswith('KGAT_'):
        user,raw=raw.split(':',1);username=user.strip() or username;raw=raw.strip()
    if not raw or not re.fullmatch(r'[a-z0-9_-]+',username):raise ValueError('Invalid Kaggle account configuration')
    env=dict(os.environ);env['KAGGLE_USERNAME']=username
    if raw.startswith('KGAT_'):env['KAGGLE_API_TOKEN']=raw;env['KAGGLE_KEY']='placeholder'
    else:env['KAGGLE_KEY']=raw;env.pop('KAGGLE_API_TOKEN',None)
    return env,username

def main():
    session=capability();print('::notice title=private-research::Private transfer configured',flush=True)
    env,user=kaggle_env();slug='monarch-private-wide-42648167419';ref=user+'/'+slug
    with tempfile.TemporaryDirectory(prefix='private-research-') as tmp:
        root=pathlib.Path(tmp);out=root/'out';out.mkdir()
        # Recover the already-submitted private kernel; never push or expose media.
        print('::notice title=private-research::Waiting on existing private GPU research',flush=True)
        for _ in range(150):
            r=subprocess.run(['kaggle','kernels','status',ref],env=env,capture_output=True,text=True,timeout=45)
            status=(r.stdout+' '+r.stderr).upper()
            if r.returncode==0 and 'COMPLETE' in status:break
            if any(x in status for x in ('ERROR','CANCEL','FAIL')):raise RuntimeError('Private GPU research did not complete')
            time.sleep(45)
        else:raise RuntimeError('Private GPU research timed out')
        subprocess.run(['kaggle','kernels','output',ref,'-p',str(out),'--file-pattern','(^|/)(private-wide-[0-9]+\\.mp4|private-wide-receipt\\.json)$'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
        receipt_paths=list(out.rglob('private-wide-receipt.json'))
        if len(receipt_paths)!=1:raise RuntimeError('Missing receipt')
        receipt=json.loads(receipt_paths[0].read_text());variants=receipt.get('variants',[])
        if receipt.get('status')!='complete_research_only' or len(variants)!=1:raise RuntimeError('Incomplete output')
        files=[receipt_paths[0]]
        for v in variants:
            name=v['name']
            if not re.fullmatch('private-wide-[0-9]+\\.mp4',name):raise ValueError('Bad output name')
            matches=list(out.rglob(name))
            if len(matches)!=1 or hashlib.sha256(matches[0].read_bytes()).hexdigest()!=v['sha256']:raise RuntimeError('Output checksum mismatch')
            files.append(matches[0])
        archive=root/'research.zip'
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for file in files:z.write(file,file.name)
        data=archive.read_bytes()
        req=urllib.request.Request(session,data=data,method='PUT',headers={'Content-Type':'application/zip','X-Goog-Upload-Command':'upload, finalize','X-Goog-Upload-Offset':'0','X-Goog-Upload-Total-Size':str(len(data))})
        with urllib.request.urlopen(req,timeout=180) as r:
            status=r.headers.get('X-Goog-Upload-Status');result=json.load(r)
        if status!='final' or not result.get('id'):raise RuntimeError('Private delivery did not finalize')
        print('::notice title=private-research::Research output delivered to private Drive',flush=True)

if __name__=='__main__':
    try:main()
    except Exception as exc:
        # Do not publish exception text: it might contain a secret URL or data.
        detail=type(exc).__name__
        if isinstance(exc,urllib.error.HTTPError):detail+=' HTTP '+str(exc.code)
        print('::error title=private-research-failure::'+detail,flush=True);sys.exit(1)
