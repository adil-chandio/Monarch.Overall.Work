"""Probe whether Gemini honors a YouTube clip window and requested sampling rate.

Output is model interpretation, not extracted image frames. Token counts only
provide indirect evidence of processing, not proof of exact samples or timing.
"""
import json, os, time, urllib.request, urllib.error
from pathlib import Path

ENDPOINT='https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent'
KEY=os.environ.get('GEMINI_API_KEY')
if not KEY: raise SystemExit('GEMINI_API_KEY missing')
VIDEO='https://www.youtube.com/watch?v=aWHX5Awe_TI'
CASES=[('first_1fps',0,5,1),('first_5fps',0,5,5),('later_5fps',10,15,5)]

def request(start,end,fps):
    part={'fileData':{'fileUri':VIDEO},'videoMetadata':{'startOffset':f'{start}s','endOffset':f'{end}s','fps':fps}}
    prompt=('Describe only the visible content of the provided clip in chronological order. '
            'For each approximate second identify subjects, actions, setting, transitions and visible text. '
            'If timing or content is unclear say so. Do not guess identity, audio, or events outside the clip.')
    payload={'contents':[{'parts':[part,{'text':prompt}]}], 'generationConfig':{'maxOutputTokens':1800}}
    req=urllib.request.Request(ENDPOINT,data=json.dumps(payload).encode(),headers={'x-goog-api-key':KEY,'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=120) as r: data=json.load(r);status=r.status
        candidate=(data.get('candidates') or [{}])[0]
        return {'http_status':status,'finish_reason':candidate.get('finishReason'),
                'description':'\n'.join(p.get('text','') for p in candidate.get('content',{}).get('parts',[]) if p.get('text') and not p.get('thought')),
                'usage':data.get('usageMetadata',{})}
    except urllib.error.HTTPError as e:
        try: error=json.loads(e.read()).get('error',{})
        except Exception:error={}
        return {'http_status':e.code,'error_status':error.get('status'),'error_reasons':[x.get('reason') for x in error.get('details',[]) if x.get('reason')]}
    except Exception as e:return {'error_type':type(e).__name__}

out={'method':'Official Gemini generateContent YouTube input with requested clip offsets and fps; samples are not raw frames, and the service may reject or ignore settings. Check model output and VIDEO token usage; neither proves precise sampling.','video_id':'aWHX5Awe_TI','model':'gemini-3.1-flash-lite-preview','cases':[]}
for name,start,end,fps in CASES:
    entry={'name':name,'requested_start_seconds':start,'requested_end_seconds':end,'requested_fps':fps,**request(start,end,fps)}
    out['cases'].append(entry)
    print(name,entry.get('http_status',entry.get('error_type')),entry.get('finish_reason'),flush=True)
    time.sleep(2)
Path('audit-output').mkdir(exist_ok=True)
Path('audit-output/gemini-sampling-probe.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
