"""Small, read-only Google API diagnosis; no credentials in output.

Tests independently: YouTube metadata, Gemini models, Gemini text, then (only
if text succeeds) one public YouTube visual analysis. This is model sampling,
not proof of every-frame access. No video downloads or bypasses are performed.
"""
import os, json, urllib.request, urllib.parse, urllib.error
from pathlib import Path

YOUTUBE='https://www.googleapis.com/youtube/v3/videos?'+urllib.parse.urlencode({'part':'id','id':'aWHX5Awe_TI'})
GEMINI='https://generativelanguage.googleapis.com/v1beta/'
KEYS=['GEMINI_API_KEY','GOOGLE_API_KEY','YOUTUBE_API_KEY','YTAP1','YTAPI1','YT_KEY','YT_API_KEY']

def req(url,key,body=None):
    data=json.dumps(body).encode() if body is not None else None
    request=urllib.request.Request(url,data=data,headers={'x-goog-api-key':key,'Content-Type':'application/json'},method='POST' if data else 'GET')
    try:
        with urllib.request.urlopen(request,timeout=90) as response:return response.status,json.load(response)
    except urllib.error.HTTPError as e:
        try:return e.code,json.loads(e.read())
        except Exception:return e.code,{}

def summary(status,data):
    err=data.get('error',{});details=err.get('details',[])
    out={'http_status':status,'status':err.get('status')}
    out['reasons']=[x['reason'] for x in details if isinstance(x,dict) and isinstance(x.get('reason'),str)]
    # These fields are safe service identifiers, never project IDs, API keys or error text.
    services=[]
    for item in details:
        if isinstance(item,dict) and isinstance(item.get('metadata'),dict):
            service=item['metadata'].get('service')
            if service in ('generativelanguage.googleapis.com','youtube.googleapis.com','serviceusage.googleapis.com'):services.append(service)
    if services:out['services']=services
    return out

key=next((os.environ[k] for k in KEYS if os.environ.get(k)),None)
out={'method':'Compare YouTube metadata, Gemini models and a text-only call using one existing configured credential; attempt a 16-second public video URL only if text works. Error text/credentials are not stored.','video_id':'aWHX5Awe_TI','outcome':'not_run'}
if not key:out['outcome']='no_configured_key'
else:
    text={'contents':[{'parts':[{'text':'Reply only OK.'}]}], 'generationConfig':{'maxOutputTokens':128,'thinkingConfig':{'thinkingBudget':0}}}
    try:
        for name,url,body in [('youtube_metadata',YOUTUBE,None),('gemini_models',GEMINI+'models?pageSize=1',None),('gemini_text',GEMINI+'models/gemini-2.5-flash:generateContent',text)]:
            status,data=req(url,key,body);out[name]=summary(status,data)
        if out['gemini_text']['http_status']==200:
            video={'contents':[{'parts':[{'file_data':{'file_uri':'https://www.youtube.com/watch?v=aWHX5Awe_TI'}},{'text':'Describe visually observable actions in sequence, with approximate times. Mark uncertainty; do not guess from the title.'}]}],'generationConfig':{'maxOutputTokens':512,'thinkingConfig':{'thinkingBudget':0}}}
            status,data=req(GEMINI+'models/gemini-2.5-flash:generateContent',key,video)
            out['gemini_video']=summary(status,data)
            if status==200:
                candidates=data.get('candidates',[]);parts=candidates[0].get('content',{}).get('parts',[]) if candidates else []
                text='\n'.join(x.get('text','') for x in parts if x.get('text'))
                if text:out['model_description_unverified']=text[:4000]
        out['outcome']='completed'
    except Exception as e:out.update(outcome='request_failed',error_type=type(e).__name__)
Path('audit-output').mkdir(exist_ok=True)
Path('audit-output/google-video-access-diagnosis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='model_description_unverified'},indent=2))
