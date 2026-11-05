"""Lightweight 43.6s duck re-edit: CC BY motion footage + existing graphic cut.

Requires imageio-ffmpeg. The second input is the credited MGA wave excerpt.
No representation is made that this is footage of the 1992 spill or Alaska.
"""
import argparse, subprocess
import imageio_ffmpeg

p=argparse.ArgumentParser()
p.add_argument('--cut',default='deliverables/monarch-invisible-thread-animated.mp4')
p.add_argument('--waves',default='showreel/duck_cinema/assets/mga-waves-excerpt.mp4')
p.add_argument('--output',default='deliverables/monarch-ducks-reedit.mp4')
a=p.parse_args()
ff=imageio_ffmpeg.get_ffmpeg_exe()
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
regular='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
windows=[(0,3.0,'A SHIPPING','ACCIDENT'),(6.3,9.9,'SOMETHING','WE CANNOT SEE'),(33.05,36.3,'ONE TINY TOY','A VAST OCEAN'),(39.4,43.6,'A NEW WAY','TO SEE OUR WORLD')]
expr='+'.join(f'between(t,{a},{b})' for a,b,_,_ in windows)
# Wave footage is illustrative Australian shoreline, not footage of the incident.
chain=(f"[1:v]fps=30,scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
       "eq=contrast=1.08:saturation=0.83:brightness=-0.09,setsar=1[sea];"
       f"[0:v][sea]overlay=0:0:enable='{expr}':shortest=1,")
chain+=f"drawbox=x=0:y=0:w=iw:h=350:color=black@0.40:t=fill:enable='{expr}',"
chain+=f"drawbox=x=0:y=1000:w=iw:h=280:color=black@0.35:t=fill:enable='{expr}',"
chain+=(f"drawtext=fontfile='{font}':text='MONARCHS EDIT  /  THE INVISIBLE THREAD':"
        f"fontsize=17:fontcolor=white@0.85:x=48:y=57:enable='{expr}',")
chain+=(f"drawtext=fontfile='{regular}':text='ILLUSTRATIVE OCEAN FOOTAGE':"
        f"fontsize=18:fontcolor=white@0.8:x=48:y=999:enable='{expr}',")
for start,end,line1,line2 in windows:
 for y,line,color in [(160,line1,'white'),(226,line2,'0xffd178')]:
  chain+=(f"drawtext=fontfile='{font}':text='{line}':fontsize=48:fontcolor={color}:"
          f"x='48-25*exp(-5*(t-{start}))':y={y}:enable='between(t,{start},{end})',")
# End credit visible while a complete attribution is supplied in the accompanying credits file.
chain+=(f"drawtext=fontfile='{regular}':text='Waves - MGA Photography / CC BY 3.0':"
        "fontsize=16:fontcolor=white@0.85:x=48:y=1040:enable='between(t,39.4,43.6)',")
chain+='format=yuv420p[v];[0:a]highpass=f=35,loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000[a]'
cmd=[ff,'-y','-loglevel','error','-i',a.cut,'-stream_loop','-1','-i',a.waves,
     '-filter_complex',chain,'-map','[v]','-map','[a]','-t','43.6',
     '-c:v','libx264','-preset','fast','-crf','19','-c:a','aac','-b:a','192k',
     '-movflags','+faststart',a.output]
subprocess.run(cmd,check=True)
