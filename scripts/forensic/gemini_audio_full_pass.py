"""Audio-only minute-by-minute model pass for the user-provided video.
No audio clips are committed. Model claims are unverified and can be inaccurate.
"""
import base64,concurrent.futures,json,os,subprocess,tempfile,time,urllib.request,urllib.error
from pathlib import Path
source=os.environ['SOURCE_VIDEO'];key=os.environ['GEMINI_API_KEY'];duration=4037.717914
endpoint='https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent'
prompt=('This is audio only. Analyze what you actually hear, not what you infer from the story. Use approximate clip-relative 10-second intervals, staying within the clip duration. For each interval distinguish narration/other voices, music, environmental ambience, and discrete sound effects if truly audible. If uncertain or masked by speech, say uncertain; do not invent events, instruments, music titles, timing, speaker identity, or quoted words. Then summarize voice delivery, whether music is clearly present, and whether identifiable non-speech effects are clearly present. Do not infer visuals.')

def analyze(start):
 end=min(start+60,duration);result={'start_seconds':start,'end_seconds':end}
 try:
  with tempfile.TemporaryDirectory() as d:
   clip=Path(d)/'audio.mp3'
   subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(start),'-i',source,'-t',str(end-start),'-vn','-ac','1','-ar','24000','-c:a','libmp3lame','-b:a','48k','-y',str(clip)],check=True,timeout=90)
   payload={'contents':[{'parts':[{'inlineData':{'mimeType':'audio/mpeg','data':base64.b64encode(clip.read_bytes()).decode()}},{'text':prompt}]}], 'generationConfig':{'maxOutputTokens':1500}}
   req=urllib.request.Request(endpoint,data=json.dumps(payload).encode(),headers={'x-goog-api-key':key,'Content-Type':'application/json'},method='POST')
   with urllib.request.urlopen(req,timeout=120) as r:data=json.load(r);result['http_status']=r.status
   c=(data.get('candidates') or [{}])[0];result['finish_reason']=c.get('finishReason')
   result['model_observation']='\n'.join(x.get('text','') for x in c.get('content',{}).get('parts',[]) if x.get('text') and not x.get('thought'))
   result['usage']=data.get('usageMetadata',{})
 except urllib.error.HTTPError as e:
  result['http_status']=e.code
  try:result['error_status']=json.loads(e.read()).get('error',{}).get('status')
  except Exception:pass
 except Exception as e:result['error_type']=type(e).__name__
 return result

report={'method':'Audio-only model descriptions of consecutive source clips. No video frames supplied. All event names, music claims, timing and voice characteristics are unverified. No original media is committed.','model':'gemini-3.1-flash-lite-preview','duration_seconds':duration,'segments':[]}
Path('audit-output').mkdir(exist_ok=True);output=Path('audit-output/gemini-audio-full-pass.json')
def save():output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 futures={}
 for start in range(0,4038,60):
  futures[pool.submit(analyze,start)]=start
  # Limit request creation to 12 starts/minute; in-flight calls can overlap.
  time.sleep(5)
 for future in concurrent.futures.as_completed(futures):
  item=future.result();report['segments'].append(item);report['segments'].sort(key=lambda v:v['start_seconds']);save()
  print('clip',item['start_seconds'],item.get('http_status',item.get('error_type')),item.get('finish_reason',''),flush=True)
save()
