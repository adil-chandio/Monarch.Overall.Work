"""Build a pose-only research guide from CMU 35_17, never an image of a person.

The source sequence is converted to a tracking-camera side projection with root
translation removed. Coordinates are approximate, without measured face/finger
landmarks or validated foot contacts. The output is NOT a final-quality rig.
"""
import hashlib, sys
from pathlib import Path
from PIL import Image
from bvh import Bvh
import run_tall_v5_mocap_to_poses as projection

SOURCE_SHA256 = '50c6469efea1edbba0f7acd46b1fa72e0b74b78e1698aa1b441990bd2a78d730'

def main(source, output):
    data=Path(source).read_bytes()
    if hashlib.sha256(data).hexdigest()!=SOURCE_SHA256:
        raise ValueError('Unexpected CMU BVH source')
    text=data.decode('utf-8');motion=Bvh(text)
    if motion.nframes < 141 or abs(motion.frame_time-1/120)>0.0001:
        raise ValueError('Unexpected timing')
    # The original helper repeats an 88-frame window for long clips; this
    # test uses exactly 24+1 frames without a loop, from 20..140 at 120fps.
    helper=Path(projection.__file__).read_text().replace(
        '(20 + (index * 5) % 88 for index in range(frame_count))',
        '(20 + (index * 5) for index in range(frame_count))')
    if helper == Path(projection.__file__).read_text(): raise RuntimeError('Unexpected helper version')
    ns={};exec(compile(helper,'verified_projection','exec'),ns)
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        ns['make_poses'](text,tmp,frame_count=25)
        atlas=Image.new('RGB',(5*448,5*768))
        for i in range(25):
            im=Image.open(Path(tmp)/f'frame_{i}.png').convert('RGB').resize((448,768),Image.Resampling.LANCZOS)
            atlas.paste(im,((i%5)*448,(i//5)*768))
        atlas.save(output,optimize=True)
    print('wrote',output)

if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('usage: make_cmu_pose_atlas.py source.bvh output.png')
    main(sys.argv[1],sys.argv[2])
