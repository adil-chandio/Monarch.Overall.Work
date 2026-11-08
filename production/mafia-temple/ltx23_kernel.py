"""Private LTX-2.3 one-shot benchmark. No original photograph or stock motion.

Adapts the inference portions of the referenced AIQUEST notebook at runtime;
its public UI and Cloudflare tunnels are deliberately excluded. Research only.
"""
import hashlib, json, os, pathlib, shutil, subprocess, sys, time, traceback, urllib.request

work=pathlib.Path('/kaggle/working'); scratch=pathlib.Path('/kaggle/tmp/monarch-ltx23')
scratch.mkdir(parents=True,exist_ok=True); os.chdir(scratch)
receipt={'status':'initializing','model':'LTX-2.3 22B distilled 1.1 Q4_K_M','original_photo_used':False,'stock_driver_used':False,'private_kernel':True,'source_notebook_commit':'0f782c3a21cba51bd7b56b2fe7345c9b383842a7','wan2gp_commit':'6479db36bdc2619a904a852bba9c2d78e1a83f82'}
def save(): (work/'ltx23-receipt.json').write_text(json.dumps(receipt,indent=2))
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
    reference_url='https://raw.githubusercontent.com/adil-chandio/Monarch.Overall.Work/1479ebd0847699e32dda6fb02fbf1a12dd9d5fee/production/mafia-temple/keyframes/shot-04-identity-study-b.jpg'
    image=urllib.request.urlopen(reference_url,timeout=90).read()
    receipt['generated_reference_sha256']=hashlib.sha256(image).hexdigest()
    if receipt['generated_reference_sha256'] != 'bc540d2a40b6331d3f9c96a4f1101ac17d40586a2f9cf8b1261101fb2fc1148c': raise ValueError('Reference checksum mismatch')
    reference=scratch/'generated-reference.jpg'; reference.write_bytes(image)
    src=''.join(cells[8]['source']); assert src.startswith('%%writefile ')
    src=src.split('\n',1)[1].split('# ==== 9. AIQUEST BRANDED GRADIO INTERFACE ====')[0]
    # Do not truncate the video to the shorter generated audio track.
    if src.count('"-shortest", final_path') != 1: raise RuntimeError('Unexpected audio mux code')
    src=src.replace('"-shortest", final_path','final_path')
    # Keep generated output out of the public UI and gather only the final video.
    # Classes created by the inference code need a real module name: an empty
    # exec namespace breaks its dynamic multi-GPU Gemma device subclass.
    namespace={'__name__':'monarch_ltx23_inference'}
    exec(compile(src,'reviewed-upstream-inference','exec'),namespace)
    class QuietProgress:
        def __call__(self,*a,**kw): pass
    prompts=[
      ('ltx23-running-a.mp4',20261102, 'A live action side view of the man in the black suit running across the wet stone temple courtyard, moving right. His left foot lands and pushes off, then his right foot lands and pushes off, alternating legs and pumping opposite arms naturally, with short grounded strides and realistic weight shifts. The camera pans smoothly to follow him as the temple pillars and lanterns visibly pass behind him. Full body and both shoes stay in frame. Same face, hairstyle and black suit as the reference. Cinematic natural lighting, realistic anatomy, no cuts.'),
      ('ltx23-running-b.mp4',391467, 'Cinematic live action side-on dolly shot: the same man in the black suit runs at a moderate pace to the right through a rain-wet temple courtyard. Both legs alternate clearly in a natural jogging cycle, each shoe makes contact with the stone before lifting. His arms swing in opposition to his legs. The tracking camera follows alongside and background lanterns and pillars move across frame. Full body, visible feet, realistic proportions, same face and hair as reference, evening blue mist and warm lantern reflections, no scene cuts.')]
    receipt.update(status='running',variants=[],frames_requested=73,fps=24);save(); t=time.monotonic()
    for name,seed,prompt in prompts:
        path,message=namespace['Video_Generation'](prompt,str(reference),None,seed,'3 Seconds (73 frames)','540p','Auto (match input image)',progress=QuietProgress())
        if not path or not pathlib.Path(path).is_file(): raise RuntimeError('Generation returned no video: '+str(message))
        target=work/name;shutil.copyfile(path,target)
        receipt['variants'].append({'name':name,'seed':seed,'prompt':prompt,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'message':message});save()
    receipt.update(status='complete_research_only',seconds=round(time.monotonic()-t,2))
    save();print('LTX23_PRIVATE_PILOT_COMPLETE',flush=True)
except Exception as exc:
    receipt.update(status='failed',error=repr(exc),traceback=traceback.format_exc());save();raise
