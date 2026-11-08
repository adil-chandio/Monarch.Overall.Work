"""Feasibility probe for Google's documented public YouTube URL input.
Never prints credentials or downloads audiovisual media. A model response is
second-hand sampled analysis, not proof of original-frame-by-frame inspection.
"""
import json, os, urllib.request, urllib.error
from pathlib import Path

out = {'provider':'Google Gemini API', 'video':'https://www.youtube.com/watch?v=aWHX5Awe_TI', 'source':'public YouTube URL', 'sampling':'default static sampling; typically 1 fps', 'raw_frames_received':False, 'result':'not_attempted'}
key = os.environ.get('VIDEO_API_KEY', '')
if not key:
    out['result'] = 'no_configured_api_key'
else:
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'
    body = {'contents':[{'parts':[{'file_data':{'file_uri':out['video']}},{'text':'Describe the visible actions and scene changes in this video in chronological order. Include approximate timestamps. Distinguish what you can see from uncertainty. Do not infer facts from the title.'}]}], 'generationConfig':{'maxOutputTokens':768}}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={'Content-Type':'application/json','x-goog-api-key':key}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=100) as response:
            data=json.load(response)
        candidates=data.get('candidates',[])
        parts=candidates[0].get('content',{}).get('parts',[]) if candidates else []
        text='\n'.join(p.get('text','') for p in parts if p.get('text'))
        out['result']='model_response' if text else 'no_text_response'
        out['model_response']=text[:5000]
        out['model']='gemini-2.5-flash'
        out['note']='Model-generated description: not independently verified and not a frame export.'
    except urllib.error.HTTPError as e:
        try: err=json.loads(e.read()).get('error',{})
        except Exception: err={}
        out['result']='api_error'; out['http_status']=e.code; out['error_status']=err.get('status','UNKNOWN')
        # Log only fixed classifications, never service error messages or the key.
        out['error_category']={'PERMISSION_DENIED':'key or project not authorized for this API', 'UNAUTHENTICATED':'authentication failed', 'RESOURCE_EXHAUSTED':'quota or billing limit', 'INVALID_ARGUMENT':'request or video input rejected', 'NOT_FOUND':'model or endpoint not available'}.get(out['error_status'],'see HTTP/status classification')
    except Exception as e:
        out['result']='request_failed';out['error_type']=type(e).__name__
Path('audit-output').mkdir(exist_ok=True)
Path('audit-output/yt-official-video-probe.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('model_response',)},indent=2))
