"""Render the generated 20-second 3D timing blockout, NOT a finished film.

The generic character is not the requested person's likeness, motions/lighting
are unapproved, and this silent previsualization requires substantial work.
Source must be build_20s_blockout.py's private .blend. No cloud transfer here.
"""
import os
from pathlib import Path
import bpy
out=Path(os.environ.get('PILOT_OUTPUT','/tmp/monarch-3d-probe'))
bpy.ops.wm.open_mainfile(filepath=str(out/'20s-temple-blockout.blend'))
s=bpy.context.scene;s.frame_start=1;s.frame_end=480;s.render.fps=24
s.render.resolution_x=480;s.render.resolution_y=270;s.render.resolution_percentage=100
s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.use_denoising=False
s.render.threads_mode='FIXED';s.render.threads=2
s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='MEDIUM'
s.render.filepath=str(out/'20s-blockout-silent.mp4')
bpy.ops.render.render(animation=True)
print('3D_BLOCKOUT_RENDER_COMPLETE',flush=True)
os._exit(0)
