#!/usr/bin/env bash
set -euo pipefail
python - <<'PY'
import json,os,pathlib,re
from kaggle.api.kaggle_api_extended import KaggleApi,ApiListKernelSessionOutputRequest
out={'log_received':False,'exception_classes':[],'flags':{},'last_diagnostic_lines':[]}
try:
 api=KaggleApi();api.authenticate()
 with api.build_kaggle_client() as k:
  req=ApiListKernelSessionOutputRequest();req.user_name=os.environ['KAGGLE_USERNAME'];req.kernel_slug='monarch-face-research-42405072811';req.page_size=1
  result=k.kernels.kernels_api_client.list_kernel_session_output(req)
  text=result.log or ''
  out['log_received']=bool(text);out['log_chars']=len(text)
  out['exception_classes']=sorted(set(re.findall(r'\b[A-Za-z]+(?:Error|Exception)\b',text)))[:40]
  checks={'out_of_memory':r'out of memory|OutOfMemoryError','disk_full':r'no space left|disk quota','missing_module':r'ImportError|ModuleNotFoundError','dtype':r'BFloat16|Half precision|float16|dtype','network':r'ConnectionError|timed out|connection reset','invalid_model':r'not found|does not appear to have a file named|is not a valid model','gpu':r'NO_GPU_ALLOCATED','model_loaded':r'Loading pipeline components|Loading checkpoint shards','inference_started':r'PILOT COMPLETE|num_inference_steps','killed':r'SIGKILL|Killed|exit code 137'}
  out['flags']={k:bool(re.search(v,text,re.I)) for k,v in checks.items()}
  out['completed_stages']=[x for x in ['STAGE 1 text embeddings only','STAGE 2 transformer and VAE','STAGE 3 video generation','PILOT COMPLETE'] if x in text]
  out['nonfinite_embeddings']='Non-finite prompt embeddings' in text
  # Restrict disclosure to known, non-sensitive diagnostic expressions.
  allowed=r'(?:CUDA out of memory|Tried to allocate [0-9.]+ [GM]iB|No space left on device|ModuleNotFoundError|ImportError|OutOfMemoryError|[A-Za-z]+Error|SIGKILL|Killed|HTTP [0-9]+)'
  out['last_diagnostic_lines']=list(dict.fromkeys(re.findall(allowed,text,re.I)))[-25:]
  out['safe_failure_messages'] = [re.sub(r'(?:/[^ :]+)+', '<path>', x)[:200] for x in text.splitlines() if re.search(r'(?:ImportError|ModuleNotFoundError|RuntimeError|ValueError|AttributeError|CalledProcessError|Exception|HTTPError|PermissionError|OSError)', x) and not re.search(r'(?i)token|secret|password|KGAT|authorization', x)][-12:]
  out['pip_errors'] = [re.sub(r'(?:/[^ :]+)+', '<path>', x)[:240] for x in text.splitlines() if re.search(r'ERROR:|Could not|ResolutionImpossible|No matching|No space|Requires-Python|Conflicting|Failed building|depends on|user requested|conflict is caused|requires numpy', x, re.I) and not re.search(r'(?i)token|secret|password|KGAT|authorization', x)][-20:]
  text=re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', text)
  out['runtime_error_messages']=[re.sub(r'(?:/[^ :]+)+', '<path>', x)[:240] for x in re.findall(r'RuntimeError[^\n]{0,240}', text)[-4:] if not re.search(r'(?i)token|secret|password|KGAT', x)]
  out['frame_sources']=re.findall(r'([A-Za-z_0-9]+\.py):([0-9]+)',text)[-30:]
  out['traceback_functions']=re.findall(r'File [^\n]{0,300}, line [0-9]+, in ([A-Za-z0-9_<>.]+)',text)[-30:]
  out['known_stages']={k:bool(re.search(v,text,re.I)) for k,v in {'vae_decode':'vae.decode|decode\(', 'vae_encode':'vae.encode|encode\(', 'attention':'scaled_dot_product_attention|attention', 'text_encoder':'text_encoder|UMT5', 'pipeline_loading':'from_pretrained|load_checkpoint', 'denoise':'transformer\(|denois|scheduler.step', 'tiling':'tiled_decode|tiled_encode'}.items()}
except Exception as e:
 out['api_failure_class']=type(e).__name__
 out['api_failure_flags']={x:bool(re.search(y,str(e),re.I)) for x,y in {'404':r'404|not found','403':r'403|forbidden','timeout':r'timeout|timed out','quota':r'quota'}.items()}
pathlib.Path('production/mafia-temple/diagnostics-liveportrait.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
PY
