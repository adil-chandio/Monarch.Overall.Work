"""Non-sensitive cloud transfer smoke test; never prints capabilities or media.

Generate an ephemeral RSA keypair, publish only the public key as a check-run
annotation, receive a run-bound encrypted upload capability from the branch,
and send eight fixed test bytes to the user's private Drive upload session.
No real user media is handled by this diagnostic.
"""
import base64,hashlib,json,os,sys,time,urllib.error,urllib.request
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding,rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

b64=lambda x:base64.b64encode(x).decode('ascii')
unb64=lambda x:base64.b64decode(x,validate=True)
def main():
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    public=key.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
    run=os.environ['GITHUB_RUN_ID']
    fingerprint=hashlib.sha256(public).hexdigest()
    # Publish only the ephemeral public key. The private key stays on this runner.
    endpoint='https://api.github.com/repos/adil-chandio/Monarch.Overall.Work/contents/production/mafia-temple/cloud-smoke-key.json'
    headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'}
    try:
        with urllib.request.urlopen(urllib.request.Request(endpoint+'?ref=arena/6101616c-monarch-overall-work',headers=headers),timeout=20) as r: old=json.load(r).get('sha')
    except urllib.error.HTTPError as e:
        if e.code!=404:raise
        old=None
    publication={'run_id':run,'head_sha':os.environ['GITHUB_SHA'],'public_key':b64(public)}
    obj={'message':'Publish ephemeral cloud smoke public key','branch':'arena/6101616c-monarch-overall-work','content':b64(json.dumps(publication).encode())}
    if old:obj['sha']=old
    req=urllib.request.Request(endpoint,data=json.dumps(obj).encode(),headers={**headers,'Content-Type':'application/json'},method='PUT')
    with urllib.request.urlopen(req,timeout=30) as r:
        if r.status not in (200,201):raise RuntimeError('Public-key publication failed')
    print('::notice title=cloud-smoke-status::Waiting for run-bound encrypted capability',flush=True)
    path='https://api.github.com/repos/adil-chandio/Monarch.Overall.Work/contents/production/mafia-temple/cloud-smoke-envelope.json?ref=arena/6101616c-monarch-overall-work'
    request=urllib.request.Request(path,headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','Cache-Control':'no-cache'})
    envelope=None
    for _ in range(80):
        try:
            with urllib.request.urlopen(request,timeout=20) as r: obj=json.load(r)
            candidate=json.loads(base64.b64decode(obj['content']))
            if candidate.get('run_id')==run and candidate.get('public_key_sha256')==fingerprint:
                envelope=candidate;break
        except (urllib.error.HTTPError,KeyError,ValueError):pass
        time.sleep(5)
    if envelope is None:raise RuntimeError('No valid capability received')
    keybytes=key.decrypt(unb64(envelope['wrapped_key']),padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
    data=AESGCM(keybytes).decrypt(unb64(envelope['nonce']),unb64(envelope['ciphertext']),(run+':'+fingerprint).encode())
    values=json.loads(data)
    url=values['upload_url']
    if not url.startswith('https://www.googleapis.com/upload/drive/v3/files?'):raise ValueError('Unexpected upload host')
    payload=b'\x00\x01\x80\xfeABC\x00'
    req=urllib.request.Request(url,data=payload,method='PUT',headers={'Content-Type':'application/octet-stream','X-Goog-Upload-Command':'upload, finalize','X-Goog-Upload-Offset':'0','X-Goog-Upload-Total-Size':str(len(payload))})
    with urllib.request.urlopen(req,timeout=60) as r:
        status=r.headers.get('X-Goog-Upload-Status');response=json.load(r)
    if status!='final' or not response.get('id'):raise RuntimeError('Upload did not finalize')
    print('::notice title=cloud-smoke-status::Eight non-sensitive bytes uploaded to Drive',flush=True)

if __name__=='__main__':
    try:main()
    except Exception as exc:
        # Capability URLs must not appear in public logs.
        detail=type(exc).__name__
        if isinstance(exc,urllib.error.HTTPError):detail+=' HTTP '+str(exc.code)
        print('::error title=cloud-smoke-failure::'+detail,flush=True)
        sys.exit(1)
