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
    # Keep generated output out of the public UI and gather only the final video.
    # Classes created by the inference code need a real module name: an empty
    # exec namespace breaks its dynamic multi-GPU Gemma device subclass.
    namespace={'__name__':'monarch_ltx23_inference'}
    exec(compile(src,'reviewed-upstream-inference','exec'),namespace)
    class QuietProgress:
        def __call__(self,*a,**kw): pass
    prompt=('A cinematic live-action full body side tracking shot of the same man in the reference image running naturally across the stone temple courtyard. '
       'He moves continuously to the right with alternating strides, arms pumping, shoes planting firmly on the wet ground with believable weight and contact. '
       'Keep his face, hairstyle, clothing and body consistent with the reference. The camera tracks smoothly alongside him at running speed. '
       'Realistic anatomy, coherent legs and hands, crisp natural textures, moody evening light, rain reflections, cinematic 35mm photography, no cuts.')
    receipt.update(status='running',prompt=prompt,frames_requested=73,fps=24);save(); t=time.monotonic()
    path,message=namespace['Video_Generation'](prompt,str(reference),None,829113,'3 Seconds (73 frames)','480p','Auto (match input image)',progress=QuietProgress())
    if not path or not pathlib.Path(path).is_file(): raise RuntimeError('Generation returned no video: '+str(message))
    target=work/'ltx23-running-pilot.mp4';shutil.copyfile(path,target)
    receipt.update(status='complete_research_only',seconds=round(time.monotonic()-t,2),output_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),message=message)
    save();print('LTX23_PRIVATE_PILOT_COMPLETE',flush=True)
except Exception as exc:
    receipt.update(status='failed',error=repr(exc),traceback=traceback.format_exc());save();raise
