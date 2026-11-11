"""Probe configured Google API access without logging secrets or downloading media."""
import hashlib, json, os, urllib.error, urllib.request
from pathlib import Path

BASE='https://generativelanguage.googleapis.com/v1beta'
VIDEO='https://www.youtube.com/watch?v=aWHX5Awe_TI'
NAMES=('GEMINI_API_KEY','GOOGLE_API_KEY','YOUTUBE_API_KEY','YTAP1','YTAPI1','YT_KEY','YT_API_KEY')
out={'provider':'Google Gemini API','video':VIDEO,'source':'public YouTube URL','sampling':'default static sampling; typically 1 fps','raw_frames_received':False,'keys_checked':[],'result':'not_attempted'}

def request(url,key,data=None):
    req=urllib.request.Request(url,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key},method='GET' if data is None else 'POST')
    try:
        with urllib.request.urlopen(req,timeout=100) as response:return response.status,json.load(response)
    except urllib.error.HTTPError as e:
        try:return e.code,json.loads(e.read())
        except Exception:return e.code,{}

seen=set(); chosen=None
for name in NAMES:
    key=os.getenv(name,'')
    if not key:continue
    digest=hashlib.sha256(key.encode()).digest()
    if digest in seen:continue
    seen.add(digest)
    try:
        status,data=request(BASE+'/models?pageSize=1',key)
        err=data.get('error',{})
        # Error reason enums, never raw messages, metadata, URLs or credentials.
        reasons=[d.get('reason') for d in err.get('details',[]) if isinstance(d,dict) and d.get('reason')]
        out['keys_checked'].append({'slot':name,'http_status':status,'error_status':err.get('status'),'reasons':reasons})
        if status==200:chosen=key;break
    except Exception as e:out['keys_checked'].append({'slot':name,'error_type':type(e).__name__})
if chosen:
    body={'contents':[{'parts':[{'file_data':{'file_uri':VIDEO}},{'text':'Describe the visible actions and scene changes in this video in chronological order. Include approximate timestamps. Distinguish what you can see from uncertainty. Do not infer facts from the title.'}]}], 'generationConfig':{'maxOutputTokens':768}}
    try:
        status,data=request(BASE+'/models/gemini-2.5-flash:generateContent',chosen,body)
        if status==200:
            candidates=data.get('candidates',[]);parts=candidates[0].get('content',{}).get('parts',[]) if candidates else []
            text='\n'.join(p.get('text','') for p in parts if p.get('text'))
            out['result']='model_response' if text else 'no_text_response';out['model_response']=text[:5000];out['model']='gemini-2.5-flash'
            out['note']='Model-generated description: not independently verified and not a frame export.'
        else:
            err=data.get('error',{});out.update(result='video_request_error',http_status=status,error_status=err.get('status'))
            out['reasons']=[d.get('reason') for d in err.get('details',[]) if isinstance(d,dict) and d.get('reason')]
    except Exception as e:out.update(result='request_failed',error_type=type(e).__name__)
else:out['result']='no_usable_configured_key' if seen else 'no_configured_api_key'
Path('audit-output').mkdir(exist_ok=True)
Path('audit-output/yt-official-video-probe.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='model_response'},indent=2))
