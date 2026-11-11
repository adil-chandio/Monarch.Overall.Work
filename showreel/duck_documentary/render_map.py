"""Create a conceptual animated North Pacific map from Natural Earth geography."""
import json, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

W,H,FPS=720,1280,30
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
data=json.loads((Path(__file__).parent/'natural_earth_110m_land.geojson').read_text())

def project(lon,lat):
 if lon<0:lon+=360
 return ((lon-100)/175*W, 1050-(lat-8)/75*900)

def base():
 im=Image.new('RGB',(W,H),(9,29,41));d=ImageDraw.Draw(im)
 for lat in range(10,80,10):
  y=project(180,lat)[1];d.line((0,y,W,y),fill=(24,63,71),width=1)
 for lon in range(100,280,20):
  x=project(lon,30)[0];d.line((x,90,x,1100),fill=(24,63,71),width=1)
 for f in data['features']:
  g=f['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
  for poly in polys:
   if not poly:continue
   for ring in [poly[0]]:
    pts=[project(*p[:2]) for p in ring]
    if any(abs(pts[i][0]-pts[i-1][0])>W*.7 for i in range(1,len(pts))):continue
    if len(pts)>2:d.polygon(pts,fill=(49,83,87),outline=(113,147,145),width=2)
 d.text((55,75),'THE INVISIBLE THREAD',font=ImageFont.truetype(FONT,20),fill=(184,202,197))
 d.text((55,185),'NORTH PACIFIC',font=ImageFont.truetype(FONT,36),fill=(242,241,225))
 d.text((55,235),'ILLUSTRATIVE OCEAN FLOW',font=ImageFont.truetype(REG,20),fill=(178,200,194))
 x,y=project(-150,64);d.text((x-40,y-45),'ALASKA',font=ImageFont.truetype(FONT,18),fill=(245,211,133))
 d.text((55,1080),'CONCEPTUAL FLOW  /  NOT TOY ROUTES',font=ImageFont.truetype(REG,17),fill=(187,205,200))
 return im

def render(t):
 im=base();d=ImageDraw.Draw(im)
 for j in range(5):
  pts=[]
  for k in range(65):
   x=105+k*7;y=620+j*55+28*math.sin(k*.07+j*.8+t*.5)
   pts.append((x,y))
  d.line(pts,fill=(32,104+j*5,111+j*5),width=2)
  phase=(t*.11+j*.19)%1;x,y=pts[int(phase*64)]
  d.ellipse((x-5,y-5,x+5,y+5),fill=(248,194,81))
 return im

def main():
 ff=imageio_ffmpeg.get_ffmpeg_exe();p=subprocess.Popen([ff,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-t','6','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',sys.argv[1]],stdin=subprocess.PIPE)
 for f in range(180):p.stdin.write(render(f/FPS).tobytes())
 p.stdin.close()
 if p.wait():raise RuntimeError('encode failure')
if __name__=='__main__':main()
