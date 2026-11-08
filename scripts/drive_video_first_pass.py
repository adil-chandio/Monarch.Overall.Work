"""Analyze three short samples of a user-provided Drive video without persisting media.
Run only after the source has been explicitly shared for analysis.
"""
import base64,json,os,subprocess,tempfile,time,urllib.request,urllib.error
from pathlib import Path

source=os.environ['SOURCE_VIDEO']; key=os.environ['GEMINI_API_KEY']
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels','-of','json',source]))
duration=float(probe['format']['duration'])
# Samples only, not full coverage. Keep request sizes/costs bounded.
starts=[0,max(0,int(duration/2)-15),max(0,int(duration)-30)]
report={'scope':'Three non-contiguous 30-second samples from the user-shared long video. Gemini output is unverified model interpretation, not a frame-by-frame inspection. The full video and original audio have not been manually inspected. No original media is committed.','duration_seconds':duration,'streams':probe['streams'],'requested_samples':[]}
url='https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent'
for index,start in enumerate(starts):
    entry={'start_seconds':start,'end_seconds':min(start+30,duration)}
    with tempfile.TemporaryDirectory() as directory:
        clip=Path(directory)/'sample.mp4'
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-ss',str(start),'-i',source,'-t','30','-map','0:v:0','-map','0:a:0?','-vf','scale=640:-2','-c:v','libx264','-preset','ultrafast','-crf','30','-c:a','aac','-b:a','64k','-movflags','+faststart','-y',str(clip)]
        try:
            subprocess.run(cmd,check=True,timeout=180)
            raw=clip.read_bytes();entry['clip_size_bytes']=len(raw)
            if len(raw)>12_000_000: raise ValueError('clip_too_large')
            prompt=('Analyze the supplied clip and separately describe observed visual style, character movement and animation, shot composition/editing, story or dialogue, sound effects, music and pacing. Give approximate timestamps relative to the start of this clip. Mark uncertainties and say if audio is missing; do not infer channel identity, production tools, exact music or sound sources, or events not present.')
            payload={'contents':[{'parts':[{'inlineData':{'mimeType':'video/mp4','data':base64.b64encode(raw).decode()}},{'text':prompt}]}], 'generationConfig':{'maxOutputTokens':1800}}
            req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'x-goog-api-key':key,'Content-Type':'application/json'},method='POST')
            with urllib.request.urlopen(req,timeout=180) as r: response=json.load(r);entry['http_status']=r.status
            candidate=(response.get('candidates') or [{}])[0]
            entry['finish_reason']=candidate.get('finishReason')
            entry['observation']='\n'.join(p.get('text','') for p in candidate.get('content',{}).get('parts',[]) if p.get('text') and not p.get('thought'))
            entry['usage']=response.get('usageMetadata',{})
        except urllib.error.HTTPError as e:
            entry['http_status']=e.code
            try:entry['error_status']=json.loads(e.read()).get('error',{}).get('status')
            except Exception:pass
        except Exception as e:entry['error_type']=type(e).__name__
    report['requested_samples'].append(entry);print('sample',index+1,entry.get('http_status',entry.get('error_type')),flush=True);time.sleep(3)
Path('audit-output').mkdir(exist_ok=True)
Path('audit-output/drive-video-first-pass.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
