"""Finish the user-selected B artwork with deterministic, editable typography."""
from pathlib import Path
import io,json,hashlib
from PIL import Image,ImageOps,ImageDraw,ImageFont
B=Path(__file__).resolve().parent
ROOT=B.parents[2]
FONT=ROOT/'public/showreel/fonts/Anton-Regular.ttf'
SMALL=ROOT/'public/showreel/fonts/Manrope-800.ttf'
W,H=1920,1080
src=B/'thumbnails/artwork-B.png'
im=ImageOps.fit(Image.open(src).convert('RGB'),(W,H),method=Image.Resampling.LANCZOS,centering=(.5,.5)).convert('RGBA')
# Local contrast treatment, not fabricated source scene content.
shade=Image.new('RGBA',(W,H)); px=shade.load()
for x in range(1200):
 a=int(110*max(0,1-x/1200)**1.6)
 for y in range(H): px[x,y]=(0,13,22,a)
im=Image.alpha_composite(im,shade)
draw=ImageDraw.Draw(im)
small=ImageFont.truetype(str(SMALL),30)
draw.rounded_rectangle((76,65,420,122),radius=12,fill=(4,25,33,220),outline=(160,187,184,100),width=1)
draw.text((94,76),'ILLUSTRATION',font=small,fill='#e8ede5',anchor='lt')
positions=[]
for text,y,size,color,maxwidth in [('2 MILLION',568,196,'#f7ca68',795),('YEARS',772,248,'#f8f7ee',800)]:
 font=ImageFont.truetype(str(FONT),size)
 while draw.textbbox((0,0),text,font=font)[2]>maxwidth:
  size-=1;font=ImageFont.truetype(str(FONT),size)
 draw.text((88,y+8),text,font=font,fill=(0,0,0,170),stroke_width=7,stroke_fill=(0,0,0,170),anchor='lt')
 draw.text((80,y),text,font=font,fill=color,stroke_width=2,stroke_fill='#081e26',anchor='lt')
 bounds=draw.textbbox((80,y),text,font=font,anchor='lt',stroke_width=2)
 assert bounds[0]>40 and bounds[2]<1000 and bounds[3]<1040,bounds
 positions.append({'text':text,'font_pixels_at_1920':size,'bounds_at_1920':list(bounds)})
im=im.convert('RGB')
exports=[]
for size,name in [((3840,2160),'thumbnail-B.jpg'),((1280,720),'thumbnail-B-1280.jpg'),((320,180),'preview-B-320.jpg'),((160,90),'preview-B-160.jpg')]:
 export=im.resize(size,Image.Resampling.LANCZOS)
 quality=94
 while True:
  buf=io.BytesIO();export.save(buf,format='JPEG',quality=quality,optimize=True,progressive=True)
  if len(buf.getvalue())<2_000_000:break
  quality-=3
  assert quality>=65,'Image unexpectedly exceeds size target'
 f=B/'thumbnails'/name;f.write_bytes(buf.getvalue())
 exports.append({'file':'thumbnails/'+name,'size':list(size),'bytes':f.stat().st_size,'quality':quality,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(B/'THUMBNAIL-PROVENANCE.json').write_text(json.dumps({'selected_direction':'B','selection':'User selected option 1 of 2 for artwork B; neither A option selected, no A artwork saved.','artwork_source':'AI-generated editorial illustration informed by actual film reference frames; not an encoded still or real expedition photograph.','style_limit':'Selected artwork is more detailed than the simplified film. ILLUSTRATION label and description identify reconstruction; no promise of real footage.','source_file':'thumbnails/artwork-B.png','source_dimensions':list(Image.open(src).size),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'reference_frames':['../review-v14/full-resolution/412.jpg','../review-v14/full-resolution/286.jpg'],'postproduction':'Centre-fit 3:2 source to 16:9, contrast gradient, deterministic typography, Lanczos resize and JPEG export. 3840 export is resized artwork, not a claim of native 4K generation or 4K film.','typography':positions,'exports':exports},indent=2)+'\n')
print(json.dumps(exports,indent=2))
