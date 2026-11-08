"""Sample public YouTube videos via Gemini; model observations are not verified frames."""
import json,os,time,urllib.request,urllib.error
from pathlib import Path

key=os.getenv('GEMINI_API_KEY','')
if not key: raise SystemExit('GEMINI_API_KEY not configured')
model='models/gemini-3.1-flash-lite-preview'
endpoint='https://generativelanguage.googleapis.com/v1beta/'+model+':generateContent'
targets=[('aWHX5Awe_TI',16),('8wtQAI_ZZlQ',13),('GHT3RyE9wGI',22)]
prompt='''Analyze this video visually. Do not infer from the title or assume identities. Return a compact timestamped sequence at approximately one-second intervals from beginning to end: for each second describe visible subjects, action, setting, framing and any visible on-screen text. Mark uncertain details as uncertain. Note cuts, camera motion and stylistic changes if observable. At the end separately describe audible sound if available, and state limitations. Never invent details. Distinguish observations from interpretation.'''
report={'method':'Gemini YouTube URL, default static video sampling (normally 1 FPS); descriptions are model-generated and unverified, not raw frames or full-frame evidence. Seconds and identities can be inaccurate.','model':model,'videos':[]}
for video_id,duration in targets:
    payload={'contents':[{'parts':[{'file_data':{'file_uri':'https://www.youtube.com/watch?v='+video_id}},{'text':prompt}]}], 'generationConfig':{'maxOutputTokens':3000}}
    request=urllib.request.Request(endpoint,data=json.dumps(payload).encode(),headers={'x-goog-api-key':key,'Content-Type':'application/json'},method='POST')
    entry={'video_id':video_id,'metadata_duration_seconds':duration}
    try:
        with urllib.request.urlopen(request,timeout=120) as response:
            result=json.load(response);entry['http_status']=response.status
        candidates=result.get('candidates',[])
        if candidates:
            candidate=candidates[0];entry['finish_reason']=candidate.get('finishReason')
            entry['model_observation']='\n'.join(p.get('text','') for p in candidate.get('content',{}).get('parts',[]) if p.get('text') and not p.get('thought'))
        entry['usage']=result.get('usageMetadata',{})
    except urllib.error.HTTPError as exc:
        entry.update(http_status=exc.code)
        try:
            error=json.loads(exc.read()).get('error',{});entry['error_status']=error.get('status')
        except Exception:pass
    except Exception as exc:entry['error_type']=type(exc).__name__
    report['videos'].append(entry)
    print(video_id,entry.get('http_status',entry.get('error_type')),entry.get('finish_reason',''),flush=True)
    time.sleep(2)
Path('audit-output').mkdir(exist_ok=True)
Path('audit-output/gemini-youtube-forensics.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
