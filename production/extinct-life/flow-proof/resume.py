"""Optional cache-only resume helper. A fresh build should use render.mjs directly.
In this review pass the unchanged first 270 frames were preserved before revising
only camera shots 4, 6 and 8. No previous full-film footage is used.
"""
from pathlib import Path
import subprocess,sys
import imageio_ffmpeg
C=Path('.cache/extinct-flow');FF=imageio_ffmpeg.get_ffmpeg_exe()
def run(args):
    subprocess.run([FF,'-hide_banner','-loglevel','warning','-y',*map(str,args)],check=True)
if sys.argv[1]=='head':
    run(['-i',C/'coverage-pass.mp4','-vf','trim=end_frame=270,setpts=N/(30*TB)','-frames:v','270','-an','-c:v','libx264','-preset','ultrafast','-qp','0','-threads','2','-pix_fmt','yuv420p','-color_range','pc','-colorspace','bt470bg',C/'head.mp4'])
elif sys.argv[1]=='join':
    run(['-i',C/'head.mp4','-i',C/'tail.mp4','-filter_complex','[0:v][1:v]concat=n=2:v=1:a=0,setpts=N/(30*TB)[v]','-map','[v]','-an','-frames:v','720','-fps_mode','passthrough','-c:v','libx264','-preset','ultrafast','-qp','0','-threads','2','-pix_fmt','yuv420p','-color_range','pc','-colorspace','bt470bg',C/'picture.mp4'])
else:raise SystemExit('Use head or join')
