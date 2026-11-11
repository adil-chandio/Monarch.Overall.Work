"""Analyze consecutive segments of a user-provided Drive video without persisting media.
Run only after the source has been explicitly shared for analysis.
"""
import base64,json,os,subprocess,tempfile,time,urllib.request,urllib.error
from pathlib import Path

source=os.environ['SOURCE_VIDEO']; key=os.environ['GEMINI_API_KEY']
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels','-of','json',source]))
duration=float(probe['format']['duration'])
# Cover the video in non-overlapping one-minute segments.
starts=[3000,3060]
report={'scope':'Two retried one-minute video clips sent to Gemini, normally sampled at 1 FPS; outputs are unverified model interpretations, not frame-by-frame inspection or a manual audio audit. Check each clip for actual coverage and errors. No original media is committed.','duration_seconds':duration,'streams':probe['streams'],'requested_samples':[]}
url='https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent'
for index,start in enumerate(starts):
    entry={'start_seconds':start,'end_seconds':min(start+60,duration)}
    with tempfile.TemporaryDirectory() as directory:
        clip=Path(directory)/'sample.mp4'
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-ss',str(start),'-i',source,'-t','60','-map','0:v:0','-map','0:a:0?','-vf','scale=640:-2','-c:v','libx264','-preset','ultrafast','-crf','30','-c:a','aac','-b:a','64k','-movflags','+faststart','-y',str(clip)]
        try:
            subprocess.run(cmd,check=True,timeout=180)
            raw=clip.read_bytes();entry['clip_size_bytes']=len(raw)
            if len(raw)>12_000_000: raise ValueError('clip_too_large')
            prompt=('Analyze the supplied one-minute video clip. Map events in chronological order in 5-second blocks using approximate local timestamps from 0:00 up to at most 1:00; summarize the narration/story, visible visual composition and animation, on-screen text, editing/cuts, sound effects and music if audible. Separate direct observations from interpretation, mark uncertainty, and do not invent dialogue, tools, sound or events. Do not assert events outside the clip.')
            payload={'contents':[{'parts':[{'inlineData':{'mimeType':'video/mp4','data':base64.b64encode(raw).decode()}},{'text':prompt}]}], 'generationConfig':{'maxOutputTokens':2200}}
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
    report['requested_samples'].append(entry);print('sample',index+1,entry.get('http_status',entry.get('error_type')),flush=True);time.sleep(6)
    if entry.get('http_status') in (429,403):
        print('Stopping on quota or permission error; remaining clips were not processed.',flush=True)
        break
Path('audit-output').mkdir(exist_ok=True)
Path('audit-output/drive-video-gap-retry.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
