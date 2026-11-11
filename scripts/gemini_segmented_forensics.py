"""Inspect three public videos in bounded 5-second Gemini clips, at requested 5fps.

Results are unverified model interpretations, not decoded/exported frames.
"""
import json,os,time,urllib.request,urllib.error
from pathlib import Path
KEY=os.getenv('GEMINI_API_KEY')
if not KEY:raise SystemExit('GEMINI_API_KEY missing')
ENDPOINT='https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent'
TARGETS=[('aWHX5Awe_TI',16),('8wtQAI_ZZlQ',13),('GHT3RyE9wGI',22)]
FPS=5
report={'method':'Official Gemini YouTube input, clip windows requested with startOffset/endOffset, fps=5. Outputs are model-generated, not extracted frames. Clipping and sampling supported by comparative token-usage probe but precise timing and scene descriptions remain unverified. No independent audio validation.','model':'gemini-3.1-flash-lite-preview','requested_fps':FPS,'videos':[]}
for video_id,duration in TARGETS:
    video={'video_id':video_id,'metadata_duration_seconds':duration,'segments':[]};report['videos'].append(video)
    for start in range(0,duration,5):
        end=min(start+5,duration)
        prompt=('Analyze only the provided video clip. Describe visible actions in chronological order, and break it down by each second within the clip, including subjects, composition, motion, transitions, on-screen text and style when clearly visible. '
                'Label seconds relative to this clip starting at 0, not the full video. Do not infer identities or invent details. '
                'If a second or detail is uncertain say uncertain. Do not discuss audio.')
        body={'contents':[{'parts':[{'fileData':{'fileUri':'https://www.youtube.com/watch?v='+video_id},'videoMetadata':{'startOffset':f'{start}s','endOffset':f'{end}s','fps':FPS}},{'text':prompt}]}], 'generationConfig':{'maxOutputTokens':1800}}
        req=urllib.request.Request(ENDPOINT,data=json.dumps(body).encode(),headers={'x-goog-api-key':KEY,'Content-Type':'application/json'},method='POST')
        result={'requested_start_seconds':start,'requested_end_seconds':end}
        try:
            with urllib.request.urlopen(req,timeout=120) as r:data=json.load(r);result['http_status']=r.status
            candidate=(data.get('candidates') or [{}])[0];result['finish_reason']=candidate.get('finishReason')
            result['model_observation']='\n'.join(p.get('text','') for p in candidate.get('content',{}).get('parts',[]) if p.get('text') and not p.get('thought'))
            result['usage']=data.get('usageMetadata',{})
        except urllib.error.HTTPError as e:
            result['http_status']=e.code
            try:result['error_status']=json.loads(e.read()).get('error',{}).get('status')
            except Exception:pass
        except Exception as e:result['error_type']=type(e).__name__
        video['segments'].append(result)
        print(video_id,start,end,result.get('http_status',result.get('error_type')),result.get('finish_reason',''),flush=True)
        time.sleep(4)
Path('audit-output').mkdir(exist_ok=True)
Path('audit-output/gemini-segmented-forensics.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
