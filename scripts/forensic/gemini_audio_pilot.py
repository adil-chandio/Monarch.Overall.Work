"""Audio-only pilot on short clips from user-supplied source, without exposing media.
Outputs are unverified model descriptions; not a substitute for listening.
"""
import base64,json,os,subprocess,tempfile,time,urllib.request,urllib.error
from pathlib import Path
source=os.environ['SOURCE_VIDEO'];key=os.environ['GEMINI_API_KEY']
endpoint='https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent'
prompt=('This is AUDIO ONLY, no visual information is provided. Listen to the clip. Distinguish narration, background music, ambience and discrete effects only if audible. Provide a chronological map in approximate 5-second bins, using times relative to this clip. Explicitly say uncertain or inaudible rather than inferring sounds from the story. Do not invent song names, instruments, effects, voices, exact quotes, or actions. At the end state whether music and discrete sound effects are actually distinguishable, and describe voice delivery without identifying the speaker.')
report={'method':'Audio-only Gemini input, 3 short clips. No visuals, so video context cannot be used directly. Interpretations are unverified and model timing can be wrong. Source audio was not stored in the repository.','model':'gemini-3.1-flash-lite-preview','segments':[]}
for start,end in [(0,30),(2003,2033),(4007,4037)]:
 result={'start_seconds':start,'end_seconds':end}
 try:
  with tempfile.TemporaryDirectory() as d:
   clip=Path(d)/'audio.mp3'
   subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(start),'-i',source,'-t',str(end-start),'-vn','-ac','1','-ar','24000','-c:a','libmp3lame','-b:a','48k','-y',str(clip)],check=True,timeout=60)
   payload={'contents':[{'parts':[{'inlineData':{'mimeType':'audio/mpeg','data':base64.b64encode(clip.read_bytes()).decode()}},{'text':prompt}]}], 'generationConfig':{'maxOutputTokens':1800}}
   req=urllib.request.Request(endpoint,data=json.dumps(payload).encode(),headers={'x-goog-api-key':key,'Content-Type':'application/json'},method='POST')
   with urllib.request.urlopen(req,timeout=120) as res:result['http_status']=res.status;data=json.load(res)
   candidate=(data.get('candidates') or [{}])[0];result['finish_reason']=candidate.get('finishReason')
   result['model_observation']='\n'.join(x.get('text','') for x in candidate.get('content',{}).get('parts',[]) if x.get('text') and not x.get('thought'))
   result['usage']=data.get('usageMetadata',{})
 except urllib.error.HTTPError as e:
  result['http_status']=e.code
  try:result['error_status']=json.loads(e.read()).get('error',{}).get('status')
  except Exception:pass
 except Exception as e:result['error_type']=type(e).__name__
 report['segments'].append(result);print(start,result.get('http_status',result.get('error_type')),result.get('finish_reason',''),flush=True);time.sleep(4)
Path('audit-output').mkdir(exist_ok=True)
Path('audit-output/gemini-audio-pilot.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
