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
os.environ['HF_HOME'] = '/tmp/monarch-liveportrait-hf'

def run(args, **kwargs):
    print('+', ' '.join(map(str, args)), flush=True)
    subprocess.run(args, check=True, **kwargs)

# Install only missing essentials rather than downgrading Kaggle's torch/CUDA stack.
run([sys.executable, '-m', 'pip', 'install', '-q', 'numpy<2', 'onnxruntime==1.20.1',
     'onnx==1.16.1', 'ml_dtypes>=0.5.1', 'tyro==0.8.5', 'pykalman==0.9.7', 'rich', 'scikit-image',
     'imageio-ffmpeg', 'ffmpeg-python', 'huggingface_hub', 'pyyaml'])
import torch
if not torch.cuda.is_available():
    raise RuntimeError('No GPU allocated')
print('GPU', torch.cuda.get_device_name(0), flush=True)
run(['git', 'clone', 'https://github.com/KwaiVGI/LivePortrait.git', 'LivePortrait'])
os.chdir(work / 'LivePortrait')
run(['git', 'checkout', '9b294b3d0536135442ea73cb01e6cb3ca7029dd3'])
# Run the face detectors on CPU; keep the actual portrait model on CUDA.
p = pathlib.Path('src/utils/cropper.py')
s = p.read_text().replace('device = "cuda"', 'device = "cpu"').replace(
    '["CUDAExecutionProvider"]', '["CPUExecutionProvider"]')
p.write_text(s)
from huggingface_hub import snapshot_download
snapshot_download('KlingTeam/LivePortrait', local_dir='pretrained_weights',
                  allow_patterns=['liveportrait/*', 'liveportrait/base_models/*',
                                  'liveportrait/retargeting_models/*',
                                  'insightface/models/buffalo_l/2d106det.onnx',
                                  'insightface/models/buffalo_l/det_10g.onnx'])
for name, encoded in IMAGES.items():
    (work / (name + '.jpg')).write_bytes(base64.b64decode(encoded))
outdir = work / 'portrait-results'; outdir.mkdir(exist_ok=True)
# Official example motion videos are used as test drivers, not footage in the output.
tests = [('side', 'd0'), ('front', 'd0')]
results = []
for source, driver in tests:
    t = time.time()
    command = [sys.executable, 'inference.py', '-s', str(work / (source + '.jpg')),
               '-d', 'assets/examples/driving/' + driver + '.mp4', '-o', str(outdir)]
    try:
        run(command)
        output = outdir / f'{source}--{driver}.mp4'
        if not output.exists() or output.stat().st_size < 10000:
            raise RuntimeError('Expected rendered video missing')
        results.append({'source':source,'driver':driver,'status':'ok','seconds':round(time.time()-t,1),'file':output.name})
    except Exception as e:
        print('TEST FAILED',source,type(e).__name__,str(e)[:300],flush=True)
        results.append({'source':source,'driver':driver,'status':'failed','error':type(e).__name__})
(outdir/'liveportrait-receipts.json').write_text(json.dumps(results, indent=2))
if not any(r['status']=='ok' for r in results):
    raise RuntimeError('All portrait tests failed')
