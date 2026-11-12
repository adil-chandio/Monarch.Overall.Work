"""Private LTX-2.3 one-shot benchmark. No original photograph or stock motion.

Adapts the inference portions of the referenced AIQUEST notebook at runtime;
its public UI and Cloudflare tunnels are deliberately excluded. Research only.
"""
import hashlib, json, os, pathlib, shutil, subprocess, sys, time, traceback, urllib.request

work=pathlib.Path('/kaggle/working'); scratch=pathlib.Path('/kaggle/tmp/monarch-ltx23')
scratch.mkdir(parents=True,exist_ok=True); os.chdir(scratch)
receipt={'status':'initializing','model':'LTX-2.3 22B distilled 1.1 Q4_K_M','original_photo_used':False,'stock_driver_used':False,'private_kernel':True,'source_notebook_commit':'0f782c3a21cba51bd7b56b2fe7345c9b383842a7','wan2gp_commit':'6479db36bdc2619a904a852bba9c2d78e1a83f82'}
def save(): (work/'ltx23-reveal-receipt.json').write_text(json.dumps(receipt,indent=2))
save()
try:
    import torch
    if torch.cuda.device_count()<2: raise RuntimeError('Two GPU devices not available')
    receipt['gpus']=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]; save()
    os.environ.update({'TOKENIZERS_PARALLELISM':'false','USE_TF':'0','USE_FLAX':'0','HF_HUB_ENABLE_HF_TRANSFER':'0','PYTORCH_CUDA_ALLOC_CONF':'expandable_segments:True,garbage_collection_threshold:0.6'})
    url='https://raw.githubusercontent.com/droiddud/Colab-notebooks/0f782c3a21cba51bd7b56b2fe7345c9b383842a7/kaggle_notebooks/ltx-2-3-22b-distilled-1-1-q4-t2v-kaggle.ipynb'
    data=urllib.request.urlopen(url,timeout=90).read()
    if hashlib.sha256(data).hexdigest()!='cfeac10f10e3765940870edcc637e14972795e0d1584c4b1d7c901b2d44a0d84': raise ValueError('Notebook checksum mismatch')
    nb=json.loads(data); cells=nb['cells']
    # Clone a fixed code revision. The upstream setup cell then applies its
    # targeted dtype fixes to this fixed checkout; no public web UI is started.
    subprocess.run(['git','clone','--quiet','https://github.com/DeepBeepMeep/Wan2GP.git','Wan2GP'],check=True)
    subprocess.run(['git','-C','Wan2GP','checkout','--quiet',receipt['wan2gp_commit']],check=True)
    setup=''.join(cells[4]['source']); exec(compile(setup,'reviewed-upstream-setup','exec'),{})
    downloads=''.join(cells[6]['source']); exec(compile(downloads,'reviewed-upstream-downloads','exec'),{})
    references={}
    items=[
        ('shot-05-side-turn-research.png','93570b5c532a9a3095c65db53ba4e513b5101fb4191c8bfd52da50d01e6d25ed','arena/6101616c-monarch-overall-work'),
        ('shot-05-red-eyes-final-research.png','d2ec676865d48f3b9a69269aaa3e96e6fa2b7482769eedc45cdd46e5e4e71e5e','arena/6101616c-monarch-overall-work')]
    for name,expected,rev in items:
        u='https://raw.githubusercontent.com/adil-chandio/Monarch.Overall.Work/'+rev+'/production/mafia-temple/keyframes/'+name
        data=urllib.request.urlopen(u,timeout=90).read()
        if hashlib.sha256(data).hexdigest()!=expected: raise ValueError('Generated reference checksum mismatch: '+name)
        p=scratch/name;p.write_bytes(data);references[name]=p
    src=''.join(cells[8]['source']); assert src.startswith('%%writefile ')
    src=src.split('\n',1)[1].split('# ==== 9. AIQUEST BRANDED GRADIO INTERFACE ====')[0]
    # Do not truncate the video to the shorter generated audio track.
    if src.count('"-shortest", final_path') != 1: raise RuntimeError('Unexpected audio mux code')
    src=src.replace('"-shortest", final_path','final_path')
    # An exact 4-second scene uses 97 frames at 24 fps.
    src=src.replace('"3 Seconds (73 frames)":  73,','"4 Seconds (97 frames)":  97,')
    # Keep generated output out of the public UI and gather only the final video.
    # Classes created by the inference code need a real module name: an empty
    # exec namespace breaks its dynamic multi-GPU Gemma device subclass.
    namespace={'__name__':'monarch_ltx23_inference'}
    exec(compile(src,'reviewed-upstream-inference','exec'),namespace)
    class QuietProgress:
        def __call__(self,*a,**kw): pass
    turn=('A single continuous realistic cinematic shot of the same man in the black suit in the temple courtyard at night. '
      'He smoothly turns his head from looking left toward the camera and holds a cold, intense direct gaze. '
      'His eyes gradually glow a deep supernatural crimson, and he slowly forms a restrained sinister closed-mouth smile. '
      'Natural blinking, skin and face anatomy, consistent identity, beard, black hair and clothing; fixed camera, no cuts, no additional people.')
    start=references['shot-05-side-turn-research.png'];end=references['shot-05-red-eyes-final-research.png']
    receipt.update(status='running',variants=[],frames_requested=97,fps=24);save();t=time.monotonic()
    path,message=namespace['Video_Generation'](turn,str(start),str(end),575,'4 Seconds (97 frames)','540p','Auto (match input image)',progress=QuietProgress())
    if not path or not pathlib.Path(path).is_file(): raise RuntimeError('Generation returned no video: '+str(message))
    target=work/'ltx23-reveal.mp4';shutil.copyfile(path,target)
    receipt['variants'].append({'name':target.name,'seed':575,'frames_requested':97,'uses_last_generated_reference':True,'prompt':turn,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'message':message});save()
    receipt.update(status='complete_research_only',seconds=round(time.monotonic()-t,2))
    save();print('LTX23_PRIVATE_PILOT_COMPLETE',flush=True)
except Exception as exc:
    receipt.update(status='failed',error=repr(exc),traceback=traceback.format_exc());save();raise
