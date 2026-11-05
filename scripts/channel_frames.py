"""Attempt public video frame extraction on the GitHub runner; report failures honestly."""
import json, pathlib, subprocess, tempfile
from PIL import Image, ImageDraw
out=pathlib.Path('audit-output'); data=json.loads((out/'channel.json').read_text())
results=[]
with tempfile.TemporaryDirectory() as temp:
    root=pathlib.Path(temp)
    for v in data['videos']:
        vid=v['id']; work=root/vid;work.mkdir()
        cmd=['yt-dlp','--no-playlist','--no-warnings','--quiet','--max-filesize','80M','-f','best[height<=720]/best','-o',str(work/'source.%(ext)s'),f'https://www.youtube.com/watch?v={vid}']
        proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=120)
        files=list(work.glob('source.*'))
        if proc.returncode or not files:
            results.append({'id':vid,'status':'download_failed','detail':proc.stderr[-1000:]});continue
        proc=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(files[0]),'-vf','fps=1,scale=360:-1',str(work/'%03d.jpg')],capture_output=True,text=True,timeout=120)
        frames=sorted(work.glob('[0-9][0-9][0-9].jpg'))
        if proc.returncode or not frames:
            results.append({'id':vid,'status':'frames_failed'});continue
        paths=[]
        for start in range(0,len(frames),12):
            batch=frames[start:start+12];w,h=Image.open(batch[0]).size
            sheet=Image.new('RGB',(w*3,(h+25)*4),'black');draw=ImageDraw.Draw(sheet)
            for n,frame in enumerate(batch):
                x=n%3*w;y=n//3*(h+25);draw.text((x+5,y+5),f'{start+n}s',fill='white');sheet.paste(Image.open(frame),(x,y+25))
            name=f'{vid}-{start:03}.jpg';sheet.save(out/name,quality=80);paths.append(name)
        results.append({'id':vid,'status':'ok','frame_count':len(frames),'sheets':paths})
(out/'frames-status.json').write_text(json.dumps(results,indent=2))
print('Frame extraction:',[(x['id'],x['status']) for x in results])
