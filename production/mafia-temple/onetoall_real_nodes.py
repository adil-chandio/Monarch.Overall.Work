"""Minimal internal-only nodes for the private Kaggle pilot; no web upload."""
from pathlib import Path
import json, subprocess
import cv2
import numpy as np
import torch
from PIL import Image, ImageDraw
import imageio_ffmpeg

ROOT = Path('/kaggle/working')

class PrivatePilotInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'width': ('INT', {'default': 480}), 'height': ('INT', {'default': 832}), 'frames': ('INT', {'default': 49})}}
    RETURN_TYPES = ('IMAGE', 'IMAGE')
    FUNCTION = 'load'
    CATEGORY = 'private_pilot'
    def load(self, width, height, frames):
        ref = Image.open(ROOT/'reference.jpg').convert('RGB').resize((width, height), Image.Resampling.LANCZOS)
        # Downloaded stock is kept only outside Kaggle output. Mirroring maps
        # the real left-facing run to the generated right-facing reference.
        cap = cv2.VideoCapture('/tmp/monarch-real-driver.mp4')
        fps = cap.get(cv2.CAP_PROP_FPS)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if abs(fps-30.0)>0.01 or total != 467:
            raise ValueError(f'Unexpected source metadata: {fps} fps, {total} frames')
        rgb = []
        for i in range(frames):
            index = round((0.25 + i/16.0) * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES,index)
            ok, bgr = cap.read()
            if not ok: raise ValueError(f'Could not decode driver frame {index}')
            bgr = cv2.flip(bgr, 1)
            rgb.append(cv2.resize(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB), (width,height), interpolation=cv2.INTER_AREA))
        cap.release()
        a = np.stack(rgb).astype(np.float32)/255
        b = np.asarray(ref).astype(np.float32)[None]/255
        return (torch.from_numpy(a), torch.from_numpy(b))

class PrivatePoseAudit:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'images': ('IMAGE',), 'reference': ('IMAGE',)}}
    RETURN_TYPES = ('IMAGE',)
    FUNCTION = 'audit'
    CATEGORY = 'private_pilot'
    def audit(self, images, reference):
        a = (images.detach().cpu().numpy().clip(0, 1)*255).astype('uint8')
        if len(a) != 49 or not np.isfinite(images.detach().cpu().numpy()).all():
            raise ValueError('Pose batch invalid')
        counts = (a.max(axis=-1)>15).sum(axis=(1,2))
        if int(counts.min()) < 150:
            raise ValueError(f'Blank or near-empty pose; active pixels min={counts.min()}')
        chosen = [0,6,12,18,24,30,36,42,48]
        sheet = Image.new('RGB',(160*len(chosen),300),'#111')
        draw = ImageDraw.Draw(sheet)
        for j,i in enumerate(chosen):
            im = Image.fromarray(a[i]); im.thumbnail((160,278)); sheet.paste(im,(160*j,0)); draw.text((160*j+4,281),str(i),fill='white')
        sheet.save(ROOT/'pose-audit.jpg', quality=90)
        # All frames for manual scrutiny, not just sparse periodic samples.
        for start in range(0,len(a),7):
            part=a[start:start+7];canvas=Image.new('RGB',(160*len(part),300),'#111');d=ImageDraw.Draw(canvas)
            for j,frame in enumerate(part):
                im=Image.fromarray(frame);im.thumbnail((160,278));canvas.paste(im,(160*j,0));d.text((160*j+4,281),str(start+j),fill='white')
            canvas.save(ROOT/f'pose-frames-{start:03d}.jpg',quality=90)
        r=(reference[0].detach().cpu().numpy().clip(0,1)*255).astype('uint8')
        Image.fromarray(r).save(ROOT/'warped-ref-audit.jpg', quality=90)
        (ROOT/'pose-audit.json').write_text(json.dumps({'frames':len(a),'nonblack_pixels_min':int(counts.min()),'nonblack_pixels_max':int(counts.max()),'driver_warning':'Actual running motion; mirrored, portrait-resized and resampled to 16 fps. Pose detection and retargeting still require visual inspection.'},indent=2))
        return (images,)

class PrivatePilotOutput:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'images': ('IMAGE',), 'fps': ('INT',{'default':16}), 'expected_frames': ('INT',{'default':49})}}
    RETURN_TYPES = ()
    FUNCTION = 'save'
    OUTPUT_NODE = True
    CATEGORY = 'private_pilot'
    def save(self, images, fps, expected_frames):
        a=images.detach().cpu().numpy()
        if len(a)!=expected_frames or not np.isfinite(a).all(): raise ValueError(f'Bad output batch {a.shape}')
        h,w=a.shape[1:3]
        cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-vcodec','libx264','-crf','16','-pix_fmt','yuv420p',str(ROOT/'onetoall-running-pilot.mp4')]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        try:
            for frame in a: p.stdin.write((frame.clip(0,1)*255).astype('uint8').tobytes())
        finally: p.stdin.close()
        if p.wait()!=0: raise RuntimeError('Video encoding failed')
        (ROOT/'output-metadata.json').write_text(json.dumps({'frames':len(a),'fps':fps,'width':w,'height':h,'status':'research diagnostic; not final'},indent=2))
        return {}

class PrivateAuditSink:
    @classmethod
    def INPUT_TYPES(cls): return {'required': {'images': ('IMAGE',)}}
    RETURN_TYPES = ()
    FUNCTION = 'finish'
    OUTPUT_NODE = True
    CATEGORY = 'private_pilot'
    def finish(self, images):
        (ROOT/'preflight-complete.txt').write_text('Pose controls decoded; visual review required.\n')
        return {}

NODE_CLASS_MAPPINGS = {'PrivatePilotInput':PrivatePilotInput, 'PrivatePoseAudit':PrivatePoseAudit, 'PrivatePilotOutput':PrivatePilotOutput, 'PrivateAuditSink':PrivateAuditSink}
