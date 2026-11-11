#!/usr/bin/env python3
"""Original 1280x720 thumbnail + 8-moment contact sheet (own-work, no third-party asset)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
import subprocess

OUT = Path(__file__).resolve().parent
WORK = OUT.parents[0] / "work" / "replay_files_v12"  # production/monarch-cam/work/replay_files_v12
FF = imageio_ffmpeg.get_ffmpeg_exe()
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(s, bold=False, mono=False):
    return ImageFont.truetype(FM if mono else (FB if bold else FR), s)
BG=(10,16,26); TEAL=(91,214,208); AMBER=(255,192,106); RED=(255,107,107)
WHITE=(244,248,255); SUB=(159,178,204); DIM=(127,146,173); LINE=(36,52,76)

def thumb():
    im=Image.new("RGB",(1280,720),BG); d=ImageDraw.Draw(im)
    for x in range(0,1280,90): d.line((x,0,x,720),fill=(14,22,34),width=1)
    for y in range(0,720,90): d.line((0,y,1280,y),fill=(14,22,34),width=1)
    d.rectangle((0,0,1280,7),fill=TEAL)
    d.text((50,40),"REPLAY FILES  /  EP.1",font=F(26,True),fill=WHITE)
    d.text((1230,42),"MONARCH CAM",font=F(22,True),fill=TEAL,anchor="ra")
    d.text((50,140),"8 MOMENTS",font=F(104,True),fill=WHITE)
    d.text((50,255),"ONE HIDDEN RULE",font=F(78,True),fill=AMBER)
    d.rectangle((50,375,720,381),fill=TEAL)
    d.text((50,410),"WHY YOU REWATCH",font=F(48,True),fill=WHITE)
    d.text((50,478),"A forensic 10-minute breakdown",font=F(30),fill=SUB)
    # right: big 8 / 8 grid
    d.rounded_rectangle((820,150,1210,570),radius=18,fill=(19,28,43),outline=(44,63,92),width=2)
    for r in range(4):
        for c in range(2):
            x=850+c*170; y=180+r*100
            col=TEAL if (r+c)%2==0 else AMBER
            d.rounded_rectangle((x,y,x+140,y+80),radius=8,fill=(13,22,34),outline=col,width=2)
            d.text((x+70,y+40),"%d"%(r*2+c+1),font=F(40,True,True),fill=col,anchor="mm")
    d.text((50,640),"ORIGINAL COMMENTARY  /  10 ORIGINAL DIAGRAMS  /  NO ENDORSEMENT IMPLIED",font=F(20,True),fill=DIM)
    im.save(OUT/"thumbnail_v12.png")

def sheet():
    cells=[]
    # hook card + 8 clip-window composited frames + closing card
    cells.append(("HOOK / TITLE", Image.open(WORK/"card_hook.png").convert("RGB")))
    for s in range(1,9):
        card=Image.open(WORK/("card_clip_%02d.png"%s)).convert("RGB")
        # grab a frame from the loop and paste into the centre strip
        tmp=WORK/("_sheet_loop_%02d.png"%s)
        subprocess.run([FF,"-y","-ss","3","-i",str(WORK/("loop_%02d.mp4"%s)),
                        "-frames:v","1","-update","1",str(tmp)],capture_output=True)
        fr=Image.open(tmp).convert("RGB").resize((608,1080),Image.LANCZOS)
        card.paste(fr,(656,0))
        from build_video_v12 import CLIPS
        cells.append(("SLOT %02d / %s"%(s,CLIPS[s]["mech"]),card))
    cells.append(("CLOSING / LIMITS", Image.open(WORK/"card_closing.png").convert("RGB")))
    tw,th=480,270
    sheet_im=Image.new("RGB",(tw*5, (th+34)*2),BG)
    dd=ImageDraw.Draw(sheet_im)
    for i,(lab,img) in enumerate(cells):
        r=i//5; c=i%5
        tile=img.resize((tw,th),Image.LANCZOS)
        x=c*tw; y=r*(th+34)
        sheet_im.paste(tile,(x,y))
        dd.rectangle((x,y+th,x+tw,y+th+34),fill=(6,10,18))
        dd.text((x+8,y+th+9),lab,font=F(17,True),fill=TEAL if i%2==0 else AMBER)
    sheet_im.save(OUT/"CONTACT_SHEET_V12.png")

if __name__=="__main__":
    thumb(); sheet(); print("thumbnail_v12.png + CONTACT_SHEET_V12.png written")
