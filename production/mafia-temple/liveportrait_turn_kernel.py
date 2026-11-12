"""Kaggle research-only LivePortrait face-motion feasibility test.

The packaging script injects ONLY previously public AI-generated keyframes. Original
reference photos are never read. The standard InsightFace detector weights are for
non-commercial research; this output is not cleared for commercial use.
"""
import base64, json, os, pathlib, subprocess, sys, time

IMAGES = __IMAGE_DATA__
work = pathlib.Path('/kaggle/working')
os.chdir(work)
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['HF_HUB_DISABLE_XET'] = '1'
os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '0'
os.environ['USE_TF'] = '0'
os.environ['USE_FLAX'] = '0'
os.environ['HF_HOME'] = '/tmp/monarch-liveportrait-hf'

def run(args, **kwargs):
    print('+', ' '.join(map(str, args)), flush=True)
    subprocess.run(args, check=True, **kwargs)

# Install only missing essentials rather than downgrading Kaggle's torch/CUDA stack.
run([sys.executable, '-m', 'pip', 'install', '-q', 'numpy<2', 'onnxruntime==1.20.1',
     'onnx==1.18.0', 'tyro==0.8.5', 'pykalman==0.9.7', 'rich', 'scikit-image',
     'imageio-ffmpeg', 'ffmpeg-python', 'huggingface_hub', 'pyyaml'])
# Avoid loading a second PyTorch/CUDA runtime in the notebook parent while
# the actual inference child starts. A GPU check needs no torch import here.
run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'])
run(['git', 'clone', 'https://github.com/KwaiVGI/LivePortrait.git', 'LivePortrait'])
os.chdir(work / 'LivePortrait')
run(['git', 'checkout', '9b294b3d0536135442ea73cb01e6cb3ca7029dd3'])
# Run the face detectors on CPU; keep the actual portrait model on CUDA.
p = pathlib.Path('src/utils/cropper.py')
s = p.read_text().replace('device = "cuda"', 'device = "cpu"').replace(
    '["CUDAExecutionProvider"]', '["CPUExecutionProvider"]')
p.write_text(s)
# Experimental smoothly animated yaw. Render both signs because the side view's
# estimated yaw convention needs visual verification; neither is a final shot.
p = pathlib.Path('src/live_portrait_pipeline.py')
s = p.read_text()
needle = "            t_new[..., 2].fill_(0)  # zero tz\n"
if s.count(needle) != 1:
    raise RuntimeError('Unexpected LivePortrait pipeline version')
s = s.replace(needle, """            # Hold at start/end, ease through a modest 35-degree turn.
            _t = max(0., min(1., (i / max(1, n_frames - 1) - .10) / .62))
            _ease = _t * _t * (3. - 2. * _t)
            _yaw = torch.tensor([float(os.environ['MONARCH_TURN_DEG']) * _ease], device=device)
            _zero = torch.zeros_like(_yaw)
            R_new = get_rotation_matrix(_zero, _yaw, _zero) @ R_s
            delta_new = x_s_info['exp'] + .45 * (delta_new - x_s_info['exp'])
            # The example driver's sideways glances were inappropriate at the
            # end of the turn. Keep eye-region expression anchored to source;
            # this can suppress blinks and still needs visual QA.
            for _idx in [11, 13, 15, 16, 18]:
                delta_new[:, _idx, :] = x_s_info['exp'][:, _idx, :]
            t_new[..., 2].fill_(0)  # zero tz
""")
# os is used by our explicit test parameter, not supplied by the pipeline.
s = 'import os\n' + s
p.write_text(s)
from huggingface_hub import snapshot_download
snapshot_download('KlingTeam/LivePortrait', local_dir='pretrained_weights',
                  allow_patterns=['liveportrait/*', 'liveportrait/base_models/*',
                                  'liveportrait/retargeting_models/*',
                                  'insightface/models/buffalo_l/2d106det.onnx',
                                  'insightface/models/buffalo_l/det_10g.onnx'], max_workers=1)
for name, encoded in IMAGES.items():
    (work / (name + '.jpg')).write_bytes(base64.b64decode(encoded))
outdir = work / 'portrait-results'; outdir.mkdir(exist_ok=True)
# Retime the approved research driver: the first half is restrained, then
# transition gently toward a mild smile. Only its motion is used, never footage.
import cv2
capture = cv2.VideoCapture('assets/examples/driving/d0.mp4')
source_frames = []
while True:
    ok, image = capture.read()
    if not ok: break
    source_frames.append(image)
capture.release()
if len(source_frames) < 25: raise RuntimeError('Expected driver frames missing')
h, w = source_frames[0].shape[:2]
driver_path = str(work / 'turn-driver.mp4')
writer = cv2.VideoWriter(driver_path, cv2.VideoWriter_fourcc(*'mp4v'), 24, (w,h))
if not writer.isOpened(): raise RuntimeError('Unable to create test driver')
for frame in range(96):
    if frame < 48:
        pos = frame / 48 * 7
    else:
        t = (frame - 48) / 47
        pos = 7 + (24 - 7) * (t*t*(3-2*t))
    # Blend neighboring frames to avoid a stepped, slow retime.
    lo = int(pos); hi = min(lo + 1, len(source_frames)-1)
    writer.write(cv2.addWeighted(source_frames[lo],1-(pos-lo),source_frames[hi],pos-lo,0))
writer.release()
results = []
source = 'side-turn-v3'
(work / (source + '.jpg')).write_bytes((work / 'side.jpg').read_bytes())
t = time.time()
command = [sys.executable, 'inference.py', '-s', str(work / (source + '.jpg')),
           '-d', driver_path, '-o', str(outdir)]
try:
    run(command, env=dict(os.environ, MONARCH_TURN_DEG='-40'))
    output = outdir / f'{source}--turn-driver.mp4'
    if not output.exists() or output.stat().st_size < 10000:
        raise RuntimeError('Expected rendered video missing')
    results.append({'yaw_degrees':-40,'status':'ok','seconds':round(time.time()-t,1),'file':output.name,
                    'frames':96,'fps':24,'status_note':'research-only'})
except Exception as e:
    print('TEST FAILED', type(e).__name__, str(e)[:300], flush=True)
    results.append({'status':'failed','error':type(e).__name__})
(outdir/'liveportrait-turn-v3-receipt.json').write_text(json.dumps(results, indent=2))
if not any(r['status']=='ok' for r in results):
    raise RuntimeError('Portrait rotation test failed')
