"""OIDC-authenticated relay smoke test. No images, videos, or credentials logged."""
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

if os.environ.get('GITHUB_EVENT_NAME') == 'push':
    from pathlib import Path
    config=json.loads(Path('production/mafia-temple/relay-smoke.json').read_text())
    url=config['url'].rstrip('/')
    audience=config['audience']
else:
    url=os.environ['RELAY_URL'].rstrip('/')
    audience=os.environ['RELAY_AUDIENCE']
if not re.fullmatch(r'https://8765-[a-z0-9]+\.e2b\.app',url):
    raise ValueError('Unexpected relay host')
if not re.fullmatch(r'monarch-[A-Za-z0-9_-]{35,100}',audience):
    raise ValueError('Unexpected audience')

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl): return None
opener=urllib.request.build_opener(NoRedirect)

def token():
    issuer=os.environ['ACTIONS_ID_TOKEN_REQUEST_URL']
    req=urllib.request.Request(issuer+'&audience='+urllib.parse.quote(audience,safe=''),headers={'Authorization':'Bearer '+os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']})
    with opener.open(req,timeout=20) as r:
        result=json.load(r)['value']
    print('::notice title=relay-stage::OIDC token obtained',flush=True)
    return result

def request(path,data=None):
    headers={'Authorization':'Bearer '+token()}
    if data is not None:headers['X-Content-Sha256']=hashlib.sha256(data).hexdigest()
    req=urllib.request.Request(url+path,data=data,headers=headers)
    with opener.open(req,timeout=30) as r:return r.status,r.read()

# The locally controlled server pins this workflow run's ID and commit after
# dispatch. Retry only until that expected-run configuration has been written.
for attempt in range(24):
    try:
        code,body=request('/health')
        if code!=200 or body!=b'ok':raise ValueError('Unexpected health response')
        break
    except urllib.error.HTTPError as e:
        if e.code!=401 or attempt==23:raise RuntimeError('OIDC verification failed') from None
        time.sleep(5)
else:raise RuntimeError('Relay unavailable')
try:
    opener.open(url+'/health',timeout=20)
    raise RuntimeError('Unauthenticated request was accepted')
except urllib.error.HTTPError as e:
    if e.code!=401:raise RuntimeError('Unexpected unauthenticated response') from None
payload=b'private relay transport smoke test; no user media\n'
code,_=request('/smoke',payload)
if code!=204:raise RuntimeError('Smoke upload rejected')
print('OIDC verified and non-sensitive smoke payload delivered; no media transferred.')
