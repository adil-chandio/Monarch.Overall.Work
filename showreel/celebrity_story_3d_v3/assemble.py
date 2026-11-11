"""Combine twelve ordered five-second render shards, then add the audio mix."""
from pathlib import Path
import sys,tempfile,subprocess,imageio_ffmpeg
p=Path(__file__).resolve().parent;root=Path(sys.argv[1]);out=Path(sys.argv[2]);ff=imageio_ffmpeg.get_ffmpeg_exe()
clips=[root/f'clip-{i:02}'/f'{i:02}.mp4' for i in range(12)]
missing=[str(x) for x in clips if not x.is_file()]
if missing:raise SystemExit('Missing render shards: '+', '.join(missing))
with tempfile.TemporaryDirectory() as td:
 td=Path(td);listing=td/'inputs.txt'
 listing.write_text(''.join("file '%s'\n"%str(f.resolve()).replace("'", "'\\''") for f in clips))
 video=td/'silent.mp4'
 subprocess.run([ff,'-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(video)],check=True)
 out.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run([sys.executable,str(p/'mux.py'),str(video),str(out)],check=True)
