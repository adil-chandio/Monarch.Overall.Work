#!/usr/bin/env python3
"""Extract source-native critical windows and pixel-preserving ROI sheets, NOT new film."""
import argparse,csv,json,subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image,ImageDraw
WINDOWS=[('01-hearts',360,(55,180,355,530)),('02-stomach',300,(160,400,460,750)),('03-splinter',690,(240,400,540,750)),('04-balloon',210,(120,700,420,1050)),('06-concert',90,(250,550,550,900)),('08-ai',60,(200,400,500,750)),('09-fight',780,(150,450,450,800)),('10-jerboa',660,(380,650,680,1000))]
def main():
 p=argparse.ArgumentParser();p.add_argument('--base',type=Path,default=Path('.cache/reference-forensics/zack-ten'));p.add_argument('--windows',type=Path,help='Optional JSON with windows: key,start_frame,end_frame_inclusive,roi_source_pixels');p.add_argument('--sheets',type=Path,default=Path('reports-private/reference-forensics/zack-ten/contact-windows'));a=p.parse_args();a.sheets.mkdir(parents=True,exist_ok=True)
 index=[];ff=imageio_ffmpeg.get_ffmpeg_exe()
 jobs=json.loads(a.windows.read_text())['windows'] if a.windows else [dict(key=k,start_frame=n-4,end_frame_inclusive=n+4,roi_source_pixels=r) for k,n,r in WINDOWS]
 for job in jobs:
  key=job['key'];start=job['start_frame'];stop=job['end_frame_inclusive'];roi=job['roi_source_pixels']
  if not key or Path(key).name!=key or not 0<=start<=stop:raise ValueError('Unsafe/invalid window')
  name=f'{key}-f{start}-{stop}';d=a.base/'dense-native'/name;d.mkdir(parents=True,exist_ok=True)
  subprocess.run([ff,'-y','-v','error','-i',str(a.base/'videos'/f'{key}.mp4'),'-vf',f"select='between(n,{start},{stop})'",'-fps_mode','passthrough',str(d/'%03d.png')],check=True)
  with (a.base/'analysis'/key/'every-frame.csv').open() as f:rows=list(csv.DictReader(f))
  frames=[{'frame':n,'pts_seconds':float(rows[n]['source_pts_seconds']),'file':f'{n-start+1:03d}.png'} for n in range(start,stop+1)]
  sheets=[]
  if roi is not None:
   left,top,right,bottom=roi;w,h=right-left,bottom-top
   if w<=0 or h<=0:raise ValueError('Invalid ROI')
   for block in range(0,len(frames),9):
    board=Image.new('RGB',(3*w,3*(h+30)),'#15222c');draw=ImageDraw.Draw(board)
    for j,row in enumerate(frames[block:block+9]):
     im=Image.open(d/row['file'])
     if not (0<=left<right<=im.width and 0<=top<bottom<=im.height):raise ValueError('ROI exceeds source bounds')
     x=(j%3)*w;y=(j//3)*(h+30);board.paste(im.crop(roi),(x,y));draw.text((x+3,y+h+2),f"{key} f{row['frame']} {row['pts_seconds']}s",fill='white')
    filename=f'{name}-roi-{block//9+1}.png';board.save(a.sheets/filename);sheets.append(filename)
  record={'key':key,'frames':frames,'roi_source_pixels':roi,'sheets':sheets,'display':'ROI pixels pasted at native 1:1 scale, labels outside source crop; full frames separately cached','review_status':'extracted_not_yet_attested','full_native_frame_review':False,'production_hold':True}
  (d/'index.json').write_text(json.dumps(record,indent=2)+'\n');index.append(record)
 (a.sheets/'extraction-index.json').write_text(json.dumps(index,indent=2)+'\n')
 print('Extracted',len(index),'windows /',sum(len(x['frames']) for x in index),'source frame crops; NOT auto-certified as reviewed')
if __name__=='__main__':main()
