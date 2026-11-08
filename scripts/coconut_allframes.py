"""Traceable, all-decoded-frame visual sheets for a CC BY-SA 2.0 reference."""
import json,pathlib,subprocess,tempfile,urllib.request
url='https://upload.wikimedia.org/wikipedia/commons/7/7b/Coconut_Mayhem.webm'
out=pathlib.Path('docs/repo-intel/open-animation-motion/coconut/allframes');out.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'source.webm'
 req=urllib.request.Request(url,headers={'User-Agent':'MonarchMotionStudy/1.0 (research)'})
 with urllib.request.urlopen(req,timeout=40) as f:p.write_bytes(f.read())
 vf="scale=192:-2,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='%{n} %{pts\\:hms}':x=3:y=3:fontsize=12:fontcolor=white:box=1:boxcolor=black@0.7,tile=6x5"
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(p),'-vf',vf,'-vsync','vfr',str(out/'frames-%02d.jpg')],check=True)
 subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=nb_read_frames,r_frame_rate,duration','-of','json',str(p)],check=True,stdout=(out/'frame-count.json').open('w'))
 print('sheets',len(list(out.glob('frames-*.jpg'))))
