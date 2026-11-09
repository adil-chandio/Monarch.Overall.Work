"""Private LTX-2.3 one-shot benchmark. No original photograph or stock motion.

Adapts the inference portions of the referenced AIQUEST notebook at runtime;
its public UI and Cloudflare tunnels are deliberately excluded. Research only.
"""
import hashlib, json, os, pathlib, shutil, subprocess, sys, time, traceback, urllib.request

work=pathlib.Path('/kaggle/working'); scratch=pathlib.Path('/kaggle/tmp/monarch-ltx23')
scratch.mkdir(parents=True,exist_ok=True); os.chdir(scratch)
receipt={'status':'initializing','model':'LTX-2.3 22B distilled 1.1 Q4_K_M','original_photo_used':False,'stock_driver_used':'previously extracted pose-only guide; no stock pixels or audio','private_kernel':True,'source_notebook_commit':'0f782c3a21cba51bd7b56b2fe7345c9b383842a7','wan2gp_commit':'6479db36bdc2619a904a852bba9c2d78e1a83f82'}
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
    # Use mmgp's documented quantized-LoRA integration, not prompt-only motion.
    old='    quantizeTransformer=False,\n    convertWeightsFloatTo=torch.float16,'
    if src.count(old)!=1: raise RuntimeError('Unexpected mmgp profile')
    src=src.replace(old,'    quantizeTransformer=False,\n    loras="transformer",\n    convertWeightsFloatTo=torch.float16,')
    src=src.replace('"480p": 480','"480p": 512')  # 512x896 is divisible by 64 for ref0.5
    old='        t_start = time.time()\n        result = ltx2_model.generate(**gen_kwargs)'
    if src.count(old)!=1: raise RuntimeError('Unexpected generation call')
    src=src.replace(old,'        gen_kwargs.update(input_frames=POSE_GUIDE, video_prompt_type="VG", denoising_strength=0.8, masking_strength=0.0, input_video_strength=0.85, loras_selected=[LORA_PATH])\n        t_start = time.time()\n        result = ltx2_model.generate(**gen_kwargs)')
    # Keep generated output out of the public UI and gather only the final video.
    # Classes created by the inference code need a real module name: an empty
    # exec namespace breaks its dynamic multi-GPU Gemma device subclass.
    namespace={'__name__':'monarch_ltx23_inference'}
    exec(compile(src,'reviewed-upstream-inference','exec'),namespace)
    class QuietProgress:
        def __call__(self,*a,**kw): pass
    # Restore only previously published pose skeleton audit images, never stock pixels.
    from PIL import Image
    import numpy as np
    from io import BytesIO
    sheets=[]
    for start in range(0,49,7):
        u=f'https://raw.githubusercontent.com/adil-chandio/Monarch.Overall.Work/1479ebd0847699e32dda6fb02fbf1a12dd9d5fee/production/mafia-temple/onetoall-real-pilot-output/pose-frames-{start:03d}.jpg'
        sheet=Image.open(BytesIO(urllib.request.urlopen(u,timeout=90).read())).convert('RGB')
        for j in range(7):
            # exclude the label row and retain the exact pose-only picture area
            sheets.append(sheet.crop((j*160,0,(j+1)*160,277)).resize((512,896),Image.Resampling.BILINEAR))
    if len(sheets)!=49: raise ValueError('Incomplete guide')
    idx=[round(i*16/24) for i in range(73)]
    pose=torch.from_numpy(np.stack([np.array(sheets[i]) for i in idx])).permute(3,0,1,2).contiguous()
    from huggingface_hub import hf_hub_download
    lora_name='ltx-2.3-22b-ic-lora-union-control-ref0.5.safetensors'
    lora=hf_hub_download(repo_id='Lightricks/LTX-2.3-22b-IC-LoRA-Union-Control',filename=lora_name,local_dir=str(scratch/'lora'))
    h=hashlib.sha256()
    with open(lora,'rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''): h.update(chunk)
    if h.hexdigest()!='a1b888a87f661d27f08b394ae559e8e1050be33900bcc36a5cdf659e48f88d18': raise ValueError('Unexpected union LoRA checksum')
    namespace['POSE_GUIDE']=pose; namespace['LORA_PATH']=lora
    trans,_=namespace['ltx2_model'].get_trans_lora()
    prep=getattr(trans,'preprocess_loras',None)
    preprocessor=(lambda sd: prep('ltx2_22B',sd)) if prep is not None else None
    namespace['offload'].load_loras_into_model(trans,[lora],[1.0],preprocess_sd=preprocessor,split_linear_modules_map=getattr(trans,'split_linear_modules_map',None))
    if getattr(trans,'_loras_errors',[]): raise RuntimeError('LoRA load errors: '+str(trans._loras_errors))
    prompt=('Cinematic live action side-view shot of the same man in a black suit in a wet stone temple courtyard. '
      'Keep his face, hairstyle and clothing consistent with the first image. Evening lanterns, blue mist, realistic photography, no scene cuts.')
    receipt.update(status='running',guide='49 pose-only frames from previous approved private preflight; repeated to 24fps',lora_sha256=h.hexdigest(),frames_requested=73,fps=24);save(); t=time.monotonic()
    path,message=namespace['Video_Generation'](prompt,str(reference),None,20261102,'3 Seconds (73 frames)','480p','Auto (match input image)',progress=QuietProgress())
    if not path or not pathlib.Path(path).is_file(): raise RuntimeError('Generation returned no video: '+str(message))
    target=work/'ltx23-pose-control.mp4';shutil.copyfile(path,target)
    receipt.update(status='complete_research_only',seconds=round(time.monotonic()-t,2),output_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),message=message)
    save();print('LTX23_PRIVATE_PILOT_COMPLETE',flush=True)
except Exception as exc:
    receipt.update(status='failed',error=repr(exc),traceback=traceback.format_exc());save();raise
