"""Experimental pose-conditioned running take. Not production/license cleared.
Uses only pre-approved generated keyframe, never the original reference.
"""
import base64, json, os, pathlib, subprocess, sys, time
from io import BytesIO

SOURCE_JPEG = __SOURCE_JPEG__
BVH_TEXT = __BVH_TEXT__
POSE_GENERATOR = __POSE_GENERATOR__
FACE_OFFSETS = __FACE_OFFSETS__
work=pathlib.Path('/kaggle/working'); os.chdir(work)
os.environ['HF_HOME']='/tmp/monarch-stableanim-hf'
os.environ['HF_HUB_ENABLE_HF_TRANSFER']='0'
os.environ['HF_HUB_DISABLE_XET']='1'
os.environ['TOKENIZERS_PARALLELISM']='false'
os.environ['USE_TF']='0'
os.environ['USE_FLAX']='0'
os.environ['PYTORCH_CUDA_ALLOC_CONF']='expandable_segments:True'

def run(args, **kw):
    print('+', ' '.join(map(str,args)), flush=True)
    subprocess.run(args, check=True, **kw)

run([sys.executable,'-m','pip','install','-q','numpy<2','onnxruntime==1.20.1','onnx==1.18.0',
     'diffusers==0.29.2','transformers==4.49.0','accelerate==0.30.1','huggingface_hub==0.27.1',
     'einops','scikit-image','imageio-ffmpeg','bvh','safetensors'])
# The preinstalled PEFT version is incompatible with the older diffusion pipeline;
# this inference path uses custom attention processors, not PEFT adapters.
run([sys.executable, '-m', 'pip', 'uninstall', '-y', 'peft'])
import torch
if not torch.cuda.is_available(): raise RuntimeError('No GPU allocated')
print('GPU',torch.cuda.get_device_name(0),'TORCH',torch.__version__,flush=True)
run(['git','clone','https://github.com/Francis-Rings/StableAnimator.git','StableAnimator'])
os.chdir(work/'StableAnimator')
run(['git','checkout','020e7f23a768410e0183ce943397d96a609f4ec1'])
run(['git','clone','https://github.com/KwaiVGI/LivePortrait.git',str(work/'LivePortrait')])
run(['git','-C',str(work/'LivePortrait'),'checkout','9b294b3d0536135442ea73cb01e6cb3ca7029dd3'])
# Use PyTorch SDPA instead of xformers to avoid replacing Kaggle's torch build.
for f in ['animation/modules/attention_processor.py','animation/modules/attention_processor_normalized.py']:
    p=pathlib.Path(f); s=p.read_text()
    s=s.replace('if is_xformers_available():\n    import xformers\nelse:\n    print(1/0)', 'def is_xformers_available():\n    return False')
    s=s.replace('if is_xformers_available():\n    import xformers\nelse:\n    print(1 / 0)', 'def is_xformers_available():\n    return False')
    s=s.replace('attention_probs = attn.get_attention_scores(query, key, attention_mask)\n            hidden_states = torch.bmm(attention_probs, value)', 'hidden_states = F.scaled_dot_product_attention(query, key, value, attn_mask=attention_mask)')
    s=s.replace('ip_attention_probs = attn.get_attention_scores(query, ip_key, None)\n            ip_hidden_states = torch.bmm(ip_attention_probs, ip_value)', 'ip_hidden_states = F.scaled_dot_product_attention(query, ip_key, ip_value)')
    # SDPA's optimized CUDA kernels require four dimensions; the upstream
    # custom processor merges batch and heads into its leading dimension.
    s=s.replace('F.scaled_dot_product_attention(query, key, value,', '_pilot_sdpa(query, key, value,')
    s=s.replace('F.scaled_dot_product_attention(query, ip_key, ip_value,', '_pilot_sdpa(query, ip_key, ip_value,')
    s += '\ndef _pilot_sdpa(q, k, v, attn_mask=None, **kwargs):\n    if attn_mask is not None and attn_mask.ndim == 3: attn_mask = attn_mask.unsqueeze(0)\n    return F.scaled_dot_product_attention(q.unsqueeze(0), k.unsqueeze(0), v.unsqueeze(0), attn_mask=attn_mask, **kwargs).squeeze(0)\n'
    p.write_text(s)
p=pathlib.Path('inference_basic.py'); s=p.read_text()
s=s.replace('from diffusers.models.attention_processor import XFormersAttnProcessor', 'from diffusers.models.attention_processor import AttnProcessor2_0 as XFormersAttnProcessor')
s=s.replace('validation_image_bgr = cv2.cvtColor(validation_face, cv2.COLOR_RGB2BGR)', 'validation_image_bgr = validation_face')
start=s.index('    if validation_image_id_ante_embedding is None:')
end=s.index('    # generator = torch.Generator', start)
s=s[:start]+"    if validation_image_id_ante_embedding is None:\n        raise RuntimeError('Reference face detector did not find a face')\n\n"+s[end:]
p.write_text(s)
pathlib.Path('animation/modules/face_model.py').write_text('''from torch import nn
import sys
sys.path.insert(0, '/kaggle/working/LivePortrait')
from src.utils.dependencies.insightface.app import FaceAnalysis
class NoopHelper:
    def clean_all(self): pass
class FaceModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.app=FaceAnalysis(name='antelopev2', root='.', providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=-1, det_size=(640,640))
        self.face_helper=NoopHelper()
''')
from huggingface_hub import snapshot_download
print('Downloading selected model weights',flush=True)
patterns=['Animation/pose_net.pth','Animation/face_encoder.pth','Animation/unet.pth',
          'models/antelopev2/glintr100.onnx','models/antelopev2/scrfd_10g_bnkps.onnx',
          'stable-video-diffusion-img2vid-xt/*.json',
          'stable-video-diffusion-img2vid-xt/*/*.json',
          'stable-video-diffusion-img2vid-xt/*/*.fp16.safetensors']
snapshot_download('FrancisRing/StableAnimator', local_dir='checkpoints', allow_patterns=patterns, max_workers=1)
# from_pretrained expects unqualified safetensors paths. The stored bytes are FP16.
svd=pathlib.Path('checkpoints/stable-video-diffusion-img2vid-xt')
for p in svd.rglob('*.fp16.safetensors'):
    p.rename(p.with_name(p.name.replace('.fp16.safetensors','.safetensors')))
pathlib.Path('models').mkdir(exist_ok=True)
os.symlink((pathlib.Path.cwd()/'checkpoints/models/antelopev2'), 'models/antelopev2')
pathlib.Path('motion_pose_helper.py').write_text(POSE_GENERATOR)
from motion_pose_helper import make_poses
make_poses(BVH_TEXT,'input/poses', FACE_OFFSETS)
pathlib.Path('input/reference.jpg').write_bytes(base64.b64decode(SOURCE_JPEG))
out=work/'run-pilot-output';out.mkdir(exist_ok=True)
print('Starting pose conditioned run',flush=True)
t=time.time()
command=[sys.executable,'inference_basic.py','--pretrained_model_name_or_path',str(svd),
 '--output_dir',str(out),'--validation_control_folder','input/poses','--validation_image','input/reference.jpg',
 '--width','512','--height','512','--guidance_scale','3','--num_inference_steps','20',
 '--posenet_model_name_or_path','checkpoints/Animation/pose_net.pth',
 '--face_encoder_model_name_or_path','checkpoints/Animation/face_encoder.pth',
 '--unet_model_name_or_path','checkpoints/Animation/unet.pth','--tile_size','16','--overlap','4',
 '--noise_aug_strength','0.02','--frames_overlap','4','--decode_chunk_size','2']
run(command)
frames=out/'animated_images'
if len(list(frames.glob('frame_*.png'))) != 24: raise RuntimeError('Expected exactly 24 output frames')
run(['ffmpeg','-y','-loglevel','error','-framerate','24','-i',str(frames/'frame_%d.png'),'-c:v','libx264','-crf','16','-pix_fmt','yuv420p',str(out/'run-motion-pilot-v2.mp4')])
(out/'run-pilot-v2-receipt.json').write_text(json.dumps({'frames':24,'fps':24,'width':512,'height':512,'seconds_elapsed':round(time.time()-t,1),'status':'technical_test_only','license':'research-only until third-party weight licenses cleared'},indent=2))
print('PILOT_DONE',flush=True)
