"""Private LTX-2.3 one-shot benchmark. No original photograph or stock motion.

Adapts the inference portions of the referenced AIQUEST notebook at runtime;
its public UI and Cloudflare tunnels are deliberately excluded. Research only.
"""
import hashlib, json, os, pathlib, shutil, subprocess, sys, time, traceback, urllib.request

work=pathlib.Path('/kaggle/working'); scratch=pathlib.Path('/kaggle/tmp/monarch-ltx23')
scratch.mkdir(parents=True,exist_ok=True); os.chdir(scratch)
receipt={'status':'initializing','model':'LTX-2.3 22B distilled 1.1 Q4_K_M','original_photo_used':False,'stock_driver_used':False,'private_kernel':True,'source_notebook_commit':'0f782c3a21cba51bd7b56b2fe7345c9b383842a7','wan2gp_commit':'6479db36bdc2619a904a852bba9c2d78e1a83f82'}
def save(): (work/'ltx23-scene-receipt.json').write_text(json.dumps(receipt,indent=2))
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
    references=[]
    for shot,expected in [('shot-02.jpg','4c185705784c30ef6e147b9ba4c9a51f2a2c5c3987ee8a0b7894bfb5f1af278c'),('shot-03.jpg','be6844028a745f9ca2828fbee0b77b6c388b7205699f5e130fb6cb7c967d5103')]:
        u='https://raw.githubusercontent.com/adil-chandio/Monarch.Overall.Work/1479ebd0847699e32dda6fb02fbf1a12dd9d5fee/production/mafia-temple/keyframes/'+shot
        data=urllib.request.urlopen(u,timeout=90).read()
        if hashlib.sha256(data).hexdigest()!=expected: raise ValueError('Generated reference checksum mismatch')
        p=scratch/shot; p.write_bytes(data);references.append(p)
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
    shots=[
        ('ltx23-gate.mp4',references[0],236,'5 Seconds (121 frames)',121,
         'A cinematic photorealistic locked-off symmetrical wide shot of the ancient Japanese temple gate at night. The carved wooden building, roof tiles, trees, lanterns and stone walkway remain fixed and unchanged. Thin mist gently drifts across the ground, and warm lantern light flickers subtly. No people, no camera movement, no scene cuts.'),
        ('ltx23-aerial.mp4',references[1],349,'4 Seconds (97 frames)',97,
         'A cinematic photorealistic aerial drone view of the Japanese temple compound at night. The camera descends slowly and continuously toward the courtyard, maintaining the same orientation. A single small man in a black suit stands on the stone path, no other people. Mist drifts between the trees, warm lanterns glow. Roofs and architecture remain stable and coherent. No cuts.')]
    receipt.update(status='running',variants=[],fps=24);save(); t=time.monotonic()
    for name,reference,seed,duration,frames,prompt in shots:
        path,message=namespace['Video_Generation'](prompt,str(reference),None,seed,duration,'480p','Auto (match input image)',progress=QuietProgress())
        if not path or not pathlib.Path(path).is_file(): raise RuntimeError('Generation returned no video: '+str(message))
        target=work/name;shutil.copyfile(path,target)
        receipt['variants'].append({'name':name,'seed':seed,'frames_requested':frames,'prompt':prompt,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'message':message});save()
    receipt.update(status='complete_research_only',seconds=round(time.monotonic()-t,2))
    save();print('LTX23_PRIVATE_PILOT_COMPLETE',flush=True)
except Exception as exc:
    receipt.update(status='failed',error=repr(exc),traceback=traceback.format_exc());save();raise
