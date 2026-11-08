"""Test Google's documented direct-public-YouTube video-understanding route.
Research only. No video generation, no downloader/auth-bypass, no credential output.
A model response is secondary machine interpretation, NOT decoded-frame ground truth.
"""
import datetime, json, os, urllib.error, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/research/zack-original-access'; OUT.mkdir(parents=True,exist_ok=True)
KEYS=[]
for name in ['GEMINI_API_KEY','GOOGLE_API_KEY','GOOGLE_GENERATIVE_AI_API_KEY','YOUTUBE_API_KEY','YTAP1','YTAPI1','YT_KEY','YT_API_KEY']:
    value=os.environ.get(name)
    if value and value not in [v for _,v in KEYS]: KEYS.append((name,value))

def request(path,key,body=None):
    req=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/'+path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'x-goog-api-key':key,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=150) as r: return r.status,json.load(r)
    except urllib.error.HTTPError as e:
        data=json.load(e)
        error=data.get('error',{})
        # Never return arbitrary provider messages (may reflect a key or URL).
        details=error.get('details',[])
        return e.code,{'error_status':error.get('status'),'error_reasons':[d.get('reason') for d in details if d.get('reason')]}
    except Exception as e: return None,{'exception_type':type(e).__name__}

report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'route':'Official Gemini API public YouTube fileData video input',
    'documentation':'https://ai.google.dev/gemini-api/docs/generate-content/video-understanding',
    'production_hold':True,'credential_probes':[], 'video_analysis_status':'not_attempted',
    'claims_limit':'API-mediated sampled audiovisual interpretation; not local source acquisition, not proof of every-frame review or accurate source settings'}
for name,key in KEYS:
    code,data=request('models',key)
    report['credential_probes'].append({'configured_secret_name':name,'http_status':code,
        'result':'models_listed' if code==200 else data})
    if code!=200: continue
    models=[m for m in data.get('models',[]) if 'generateContent' in m.get('supportedGenerationMethods',[]) and 'gemini' in m.get('name','') and 'flash' in m.get('name','') and not any(x in m['name'] for x in ['image','audio','tts','live','thinking','8b'])]
    preferred=['models/gemini-3.8-flash','models/gemini-3-flash-preview','models/gemini-2.5-flash','models/gemini-2.0-flash']
    models.sort(key=lambda m: preferred.index(m['name']) if m['name'] in preferred else 99)
    report['video_candidate_models']=[m['name'] for m in models]
    if not models:
        report['video_analysis_status']='no_compatible_flash_model_listed'; break
    model=models[0]['name'];report['pilot_model']=model
    body={'contents':[{'role':'user','parts':[
        {'fileData':{'fileUri':'https://www.youtube.com/watch?v=-GyaX8xWy58','mimeType':'video/mp4'},
         'videoMetadata':{'startOffset':'0s','endOffset':'4s','fps':5}},
        {'text':'Inspect ONLY the provided first four seconds of the actual video and audio. Do not use search, title or a remembered summary. Give a timestamped account of visible objects, setting colors, hand/prop interaction, character clothing and the order of visible actions. Report any clearly audible non-speech sound separately and mark uncertainty. Do not reproduce the narration. If the media cannot be accessed say so explicitly; do not invent observations. Do not claim exact focal length, renderer, assets or frame-perfect boundaries.'}]}],
        'generationConfig':{'maxOutputTokens':1600,'temperature':0.1}}
    code,data=request(model+':generateContent',key,body)
    report['pilot_http_status']=code
    report['pilot_requested_window_seconds']=[0,4];report['pilot_requested_fps']=5
    if code==200:
        report['video_analysis_status']='api_response_requires_independent_validation'
        report['pilot_response']=data
    else:
        report['video_analysis_status']='video_api_request_failed'; report['pilot_error']=data
    break
(OUT/'video-api-probe.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['video_analysis_status'])
