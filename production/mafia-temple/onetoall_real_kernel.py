"""One-to-All private T4 research kernel, assembled by make_onetoall_pilot.py.
No original user image is included or transferred. A public stock video is used
only to derive an anonymized pose control; it is never copied to output.
"""
import base64, hashlib, json, os, pathlib, subprocess, sys, time, traceback
import urllib.request

ASSETS = __ASSETS__
NODES = __NODES__
GRAPH = __GRAPH__
STAGE = __STAGE__
work = pathlib.Path('/kaggle/working')
os.chdir(work)
# Generated reference and a public stock video, downloaded to a private runtime.
# Never save the stock source or user original to the Kaggle output directory.
with urllib.request.urlopen(ASSETS['reference']['url'], timeout=120) as response:
    data=response.read()
if hashlib.sha256(data).hexdigest()!=ASSETS['reference']['sha256']:
    raise ValueError('Pinned generated reference checksum mismatch')
(work/'reference.jpg').write_bytes(data)
expected_mount=pathlib.Path(ASSETS['driver']['mount'])
# Kaggle has used both legacy /input/<slug> and newer /input/datasets/<owner>/<slug> layouts.
choices=[expected_mount, pathlib.Path('/kaggle/input/datasets')/ASSETS['driver']['owner']/expected_mount.parent.name/'driver.mp4']
existing=[p for p in choices if p.is_file()]
if not existing:
    raise FileNotFoundError('Private driver mount missing. Input entries: '+repr([str(p) for p in pathlib.Path('/kaggle/input').glob('*/*/*')][:40]))
data=existing[0].read_bytes()
if hashlib.sha256(data).hexdigest()!=ASSETS['driver']['sha256']:
    raise ValueError('Private driver dataset checksum mismatch')
pathlib.Path('/tmp/monarch-real-driver.mp4').write_bytes(data)
del data
os.environ.update({'HF_HUB_DISABLE_XET':'1','HF_HUB_ENABLE_HF_TRANSFER':'0','TOKENIZERS_PARALLELISM':'false','USE_TF':'0','USE_FLAX':'0','PYTORCH_CUDA_ALLOC_CONF':'expandable_segments:True'})

def run(cmd, **kw):
    print('+', ' '.join(map(str, cmd)), flush=True)
    subprocess.run(cmd, check=True, **kw)

def clone(url, path, rev):
    run(['git','clone','--quiet',url,str(path)])
    run(['git','-C',str(path),'checkout','--quiet',rev])
    return subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        while True:
            chunk=f.read(8*1024*1024)
            if not chunk: break
            h.update(chunk)
    return h.hexdigest()

receipt={'status':'initializing','private_input':True,'original_photo_used':False,'driver':'Pexels 32740423, actual performance, pose only, source mirrored, 0.25-3.25 seconds','graph':GRAPH,'models':{},'revisions':{},'fps':16,'frames_requested':49,'resolution':[480,832]}
receipt_path=work/'onetoall-receipt.json'
def save(): receipt_path.write_text(json.dumps(receipt,indent=2))
save()
proc=None; log=None
try:
    import torch
    if not torch.cuda.is_available(): raise RuntimeError('No CUDA GPU allocated')
    receipt['gpu']=torch.cuda.get_device_name(0);receipt['torch']=torch.__version__
    receipt['compute_capability']=list(torch.cuda.get_device_capability(0))
    receipt['bf16_including_emulation']=bool(torch.cuda.is_bf16_supported())
    try:
        receipt['native_bf16']=bool(torch.cuda.is_bf16_supported(including_emulation=False))
    except TypeError:
        receipt['native_bf16']=receipt['compute_capability'][0] >= 8
    save()
    print('GPU:',receipt['gpu'],'torch:',receipt['torch'],'native bf16:',receipt['native_bf16'],flush=True)
    # Keep the full framework and downloaded models out of Kaggle's output
    # directory so that artifact listing stays small and recoverable.
    comfy=pathlib.Path('/tmp/monarch-onetoall-ComfyUI'); custom=comfy/'custom_nodes'
    receipt['revisions']['ComfyUI']=clone('https://github.com/Comfy-Org/ComfyUI.git',comfy,'6dd3c67427d65751d42f2dbc0c3db3d829c697de')
    receipt['revisions']['wrapper']=clone('https://github.com/kijai/ComfyUI-WanVideoWrapper.git',custom/'ComfyUI-WanVideoWrapper','088128b224242e110d3906c6750e9a3a348a659b')
    receipt['revisions']['preprocessor']=clone('https://github.com/kijai/ComfyUI-WanAnimatePreprocess.git',custom/'ComfyUI-WanAnimatePreprocess','0e0b6a2a555625acf4d4aefb780e27d06937132f')
    (custom/'PrivatePilot').mkdir();(custom/'PrivatePilot'/'__init__.py').write_text(NODES)
    # The wrapper already implements fp16 in its loader but omits it from the
    # ComfyUI input enum. Permit that existing dtype explicitly on the T4; this
    # is a deliberate deviation from the author's BF16-named encoder setup.
    p=custom/'ComfyUI-WanVideoWrapper'/'nodes_model_loading.py';s=p.read_text()
    start=s.index('class LoadWanVideoT5TextEncoder:');end=s.index('\nclass ',start+10)
    part=s[start:end];old='"precision": (["fp32", "bf16"],';new='"precision": (["fp32", "bf16", "fp16"],'
    if part.count(old)!=1: raise RuntimeError('Text encoder precision patch no longer matches')
    p.write_text(s[:start]+part.replace(old,new,1)+s[end:]);receipt['t5_precision_patch']='enum includes existing fp16 dtype implementation'
    # Keep existing Kaggle torch/CUDA; install only compatible runtime packages.
    run([sys.executable,'-m','pip','install','-q','-r',str(comfy/'requirements.txt'),'-r',str(custom/'ComfyUI-WanVideoWrapper'/'requirements.txt'),'numpy==1.26.4','opencv-python-headless==4.10.0.84','onnxruntime-gpu==1.20.2','imageio-ffmpeg','huggingface_hub<1'])
    from huggingface_hub import hf_hub_download
    items=[
      ('Kijai/WanVideo_comfy','8260d429d19fd7a72304cad059160b95d843913f','OneToAllAnimation/Wan21-OneToAllAnimation_1_3B_v2_fp16.safetensors','diffusion_models/Wan21-OneToAllAnimation_1_3B_v2_fp16.safetensors'),
      ('Kijai/WanVideo_comfy','8260d429d19fd7a72304cad059160b95d843913f','umt5-xxl-enc-bf16.safetensors','text_encoders/umt5-xxl-enc-bf16.safetensors'),
      ('Kijai/WanVideo_comfy','8260d429d19fd7a72304cad059160b95d843913f','Wan2_1_VAE_bf16.safetensors','vae/Wan2_1_VAE_bf16.safetensors'),
      ('Wan-AI/Wan2.2-Animate-14B','cb93a225fbaf1ca100f54e79da8f994995b689b3','process_checkpoint/det/yolov10m.onnx','detection/yolov10m.onnx'),
      ('JunkyByte/easy_ViTPose','e83805274e89428969355ec4afffcbc413e79188','onnx/wholebody/vitpose-l-wholebody.onnx','detection/vitpose-l-wholebody.onnx'),
    ]
    if STAGE == 'preflight': items=items[-2:]  # Only pose detector models.
    for repo,rev,name,dest in items:
        print('Downloading',repo,name,flush=True)
        p=pathlib.Path(hf_hub_download(repo_id=repo,filename=name,revision=rev)); target=comfy/'models'/dest
        target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to(p)
        receipt['models'][dest]={'repo':repo,'revision':rev,'sha256':sha(p),'bytes':p.stat().st_size};save()
    (work/'graph.json').write_text(json.dumps(GRAPH,indent=2))
    log=(work/'comfy.log').open('w')
    env=dict(os.environ);env['CUDA_VISIBLE_DEVICES']='0'
    proc=subprocess.Popen([sys.executable,'main.py','--listen','127.0.0.1','--port','8188','--disable-auto-launch'],cwd=comfy,stdout=log,stderr=subprocess.STDOUT,env=env)
    import requests
    base='http://127.0.0.1:8188';deadline=time.monotonic()+180
    while time.monotonic()<deadline:
        if proc.poll() is not None: raise RuntimeError('ComfyUI exited during startup')
        try:
            r=requests.get(base+'/system_stats',timeout=3)
            if r.ok: break
        except requests.RequestException: pass
        time.sleep(2)
    else: raise TimeoutError('ComfyUI did not start')
    # Confirm every graph class is installed before queueing.
    classes=requests.get(base+'/object_info',timeout=30).json()
    missing=sorted({n['class_type'] for n in GRAPH.values()}-set(classes))
    if missing: raise RuntimeError(f'Missing Comfy nodes: {missing}')
    t=time.monotonic();r=requests.post(base+'/prompt',json={'prompt':GRAPH},timeout=30)
    if not r.ok: raise RuntimeError(f'Graph rejected: {r.status_code}: {r.text[:5000]}')
    job=r.json()['prompt_id'];receipt['prompt_id']=job;receipt['status']='running';save();print('Submitted private local prompt',job,flush=True)
    while time.monotonic()-t < 3600:
        if proc.poll() is not None: raise RuntimeError('ComfyUI exited while sampling')
        hist=requests.get(base+'/history/'+job,timeout=10).json()
        if job in hist:
            status=hist[job].get('status',{})
            if status.get('status_str')=='error': raise RuntimeError('Comfy execution failed: '+json.dumps(status)[:5000])
            if status.get('completed'): break
        time.sleep(10)
    else: raise TimeoutError('Comfy prompt timed out')
    names=['pose-audit.jpg','pose-audit.json','warped-ref-audit.jpg']+[f'pose-frames-{i:03d}.jpg' for i in range(0,49,7)]
    names += ['preflight-complete.txt'] if STAGE=='preflight' else ['onetoall-running-pilot.mp4','output-metadata.json']
    for name in names:
        if not (work/name).is_file(): raise RuntimeError('Missing expected output: '+name)
    receipt.update({'status':'complete_pose_preflight' if STAGE=='preflight' else 'complete_research_only','seconds_elapsed':round(time.monotonic()-t,1),'pose_audit':json.loads((work/'pose-audit.json').read_text()),'notes':'Generated identity reference, public real driver used only for pose; FP16 on T4. No original user image. Requires visual review.'})
    if STAGE!='preflight': receipt['output']=json.loads((work/'output-metadata.json').read_text())
    save()
    print('ONETOALL_REAL_COMPLETE',flush=True)
except Exception as exc:
    receipt.update({'status':'failed','error':repr(exc),'traceback':traceback.format_exc()});save()
    raise
finally:
    pathlib.Path('/tmp/monarch-real-driver.mp4').unlink(missing_ok=True)
    if proc is not None:
        proc.terminate()
        try: proc.wait(timeout=15)
        except subprocess.TimeoutExpired: proc.kill();proc.wait()
    if log is not None: log.close()
    logfile=work/'comfy.log'
    if logfile.exists(): print('COMFY LOG TAIL\n'+'\n'.join(logfile.read_text(errors='replace').splitlines()[-100:]),flush=True)
