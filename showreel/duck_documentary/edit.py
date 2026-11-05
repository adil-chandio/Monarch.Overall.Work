"""Build the duck-story rough cut with moving CC BY footage and animated map.
See CREDITS.md before publishing; illustrative footage is not the incident.
"""
from pathlib import Path
import subprocess, tempfile
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[2]
A=ROOT/'showreel/duck_cinema/assets';OUT=ROOT/'deliverables/monarch-ducks-documentary-cut.mp4'
ff=imageio_ffmpeg.get_ffmpeg_exe(); font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; reg='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
# duration, source, start offset, headline, attribution label
shots=[
 (3.0,'ship-dashcam.mp4',6,'A SHIPPING ACCIDENT','ILLUSTRATIVE SHIP FOOTAGE / 2018'),
 (3.3,'ducks-event.mp4',38,'THOUSANDS OF TOYS','ILLUSTRATIVE DUCK RACE / 2022'),
 (3.6,'mga-waves-excerpt.mp4',5,'SOMETHING INVISIBLE','ILLUSTRATIVE COAST / AUSTRALIA'),
 (3.2,'ship-dashcam.mp4',15,'ONE CONTAINER / 1992','ILLUSTRATIVE SHIP FOOTAGE / 2018'),
 (4.1,'ducks-event.mp4',14,'NEARLY 29,000 TOYS','ILLUSTRATIVE DUCK RACE / 2022'),
 (5.3667,'map',0,'',''),
 (3.7,'noaa-highseas-2021.mp4',4,'RECOVERY CLUES','ILLUSTRATIVE RESEARCH VESSEL / 2021'),
 (3.0333,'mga-waves-excerpt.mp4',10,'OCEAN CURRENTS','ILLUSTRATIVE COAST / AUSTRALIA'),
 (3.7667,'map',1,'',''),
 (3.2333,'ducks-event.mp4',38,'ONE SMALL TOY','ILLUSTRATIVE DUCK RACE / 2022'),
 (3.1,'mga-waves-excerpt.mp4',1,'A VAST SYSTEM','ILLUSTRATIVE COAST / AUSTRALIA'),
 (4.2,'ship-dashcam.mp4',19,'THE INVISIBLE THREAD','ILLUSTRATIVE SHIP FOOTAGE / 2018'),
]

def run(cmd):subprocess.run(cmd,check=True)
with tempfile.TemporaryDirectory() as temp:
 temp=Path(temp);map_path=temp/'map.mp4'
 run(['python3',str(ROOT/'showreel/duck_documentary/render_map.py'),str(map_path)])
 outputs=[]
 for i,(dur,name,offset,title,label) in enumerate(shots):
  src=map_path if name=='map' else A/name; out=temp/f'shot{i:02}.mp4';outputs.append(out)
  vf='fps=30,scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1'
  if name!='map':
   vf+=',eq=contrast=1.08:saturation=0.8:brightness=-0.025'
   vf+=",drawbox=x=0:y=0:w=iw:h=125:color=black@0.45:t=fill,drawbox=x=0:y=820:w=iw:h=260:color=black@0.52:t=fill"
   vf+=f",drawtext=fontfile='{reg}':text='{label}':fontcolor=white@0.9:fontsize=18:x=48:y=62"
   size=43 if len(title)>22 else 48
   vf+=f",drawtext=fontfile='{font}':text='{title}':fontcolor=white:fontsize={size}:x='48-20*exp(-5*t)':y=895"
   vf+=",drawbox=x=48:y=974:w=80:h=4:color=0xffc960:t=fill"
  run([ff,'-y','-loglevel','error','-ss',str(offset),'-i',str(src),'-t',str(dur),'-vf',vf,'-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(out)])
 concat=temp/'list.txt';concat.write_text(''.join("file '"+str(x)+"'\n" for x in outputs))
 audio=ROOT/'deliverables/monarch-invisible-thread-animated.mp4'
 run([ff,'-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-i',str(audio),'-map','0:v','-map','1:a','-t','43.6','-c:v','copy','-af','highpass=f=35,loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000','-c:a','aac','-b:a','192k','-movflags','+faststart',str(OUT)])
print(OUT)
