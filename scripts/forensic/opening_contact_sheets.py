"""Decode user-supplied local video to private, labeled opening contact sheets.
Requires ffmpeg, Pillow; outputs must stay out of a public repository.
At 30fps on the inspected source, every 30th decoded frame corresponds to
one second in its first minute (verify PTS before applying to another file).
"""
import argparse,math,subprocess
from pathlib import Path
from PIL import Image,ImageDraw

p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');p.add_argument('--ffmpeg',default='ffmpeg');a=p.parse_args()
out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
for name,seconds,vf,rate,cols,rows in [('seconds',60,'select=not(mod(n\\,30)),scale=320:-1',1,4,4),('frames',5,'scale=240:-1',30,5,5)]:
 directory=out/name;directory.mkdir(exist_ok=True)
 if any(directory.iterdir()):raise SystemExit(f'Output directory is not empty: {directory}')
 subprocess.run([a.ffmpeg,'-v','error','-i',a.source,'-t',str(seconds),'-vf',vf,'-fps_mode','passthrough','-q:v','3',str(directory/'%04d.jpg')],check=True)
 files=sorted(directory.glob('*.jpg'))
 for base in range(0,len(files),cols*rows):
  group=files[base:base+cols*rows];w,h=Image.open(group[0]).size;sheet=Image.new('RGB',(cols*w,rows*(h+23)),'white');draw=ImageDraw.Draw(sheet)
  for i,path in enumerate(group):
   x=(i%cols)*w;y=(i//cols)*(h+23);sheet.paste(Image.open(path),(x,y+23));draw.text((x+3,y+3),f'{(base+i)/rate:.3f}s',fill='black')
  sheet.save(out/f'{name}-{base//(cols*rows)+1:02d}.jpg',quality=85)
 print(name,len(files),'frames')
