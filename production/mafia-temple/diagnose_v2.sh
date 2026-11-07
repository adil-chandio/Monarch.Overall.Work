#!/usr/bin/env bash
set -euo pipefail
ref="$KAGGLE_USERNAME/monarch-wan-pilot-42378485417"
dir=/tmp/mafia-v2-diagnostics
mkdir -p "$dir"
kaggle kernels status "$ref" > "$dir/status.txt" 2>&1 || true
kaggle kernels output "$ref" -p "$dir" > "$dir/output-command.txt" 2>&1 || true
python - <<'PY'
import pathlib,json,re
p=pathlib.Path('/tmp/mafia-v2-diagnostics')
logs=list(p.glob('*.log'))
text='\n'.join(f.read_text(errors='replace') for f in p.glob('*.log'))+'\n'+'\n'.join(f.read_text(errors='replace') for f in p.glob('worker_*.txt'))
flags={k:bool(re.search(v,text,re.I)) for k,v in {
 'cuda_out_of_memory':r'out of memory|cuda error: out of memory|OutOfMemoryError',
 'worker_failed':r'Incomplete render|WORKER EXIT CODES',
 'missing_module':r'ModuleNotFoundError|ImportError',
 'quota':r'quota|too many GPU|not enough quota',
 'kaggle_error':r'error|exception|traceback',
 'time_limit':r'timeout|timed out|time limit',
 'permission':r'permission denied|unauthorized|403 forbidden',
 'kernel_no_gpu':r'NO_GPU_ALLOCATED',
 'model_download':r'connection error|failed to download|cannot find the requested files',
}.items()}
classes=sorted(set(re.findall(r'\b(?:CUDA|[A-Za-z]+(?:Error|Exception))\b',text)))[:40]
# Only non-sensitive fixed flags and exception class names go to the public branch.
result={'log_files':len(logs),'status_returned':bool((p/'status.txt').read_text().strip()),'flags':flags,'exception_classes':classes,'completed_scenes':sorted(set(re.findall(r'Scene (v2(?:run|face)[AB]) COMPLETE',text))),'events':[m for m in ('v2runA','v2runB','v2faceA','v2faceB') if m in text], 'oom_messages': re.findall(r'(?:Tried to allocate [^\n]{0,180}|CUDA out of memory[^\n]{0,180})',text)[:4], 'status_flags': {label: bool(re.search(pattern, (p/'status.txt').read_text(errors='replace')+'\n'+(p/'output-command.txt').read_text(errors='replace'), re.I)) for label,pattern in {'not_found':'404|not found', 'forbidden':'403|forbidden', 'quota':'quota', 'bad_request':'400|bad request', 'error':'error', 'complete':'complete'}.items()},'output_files':[x.suffix for x in p.iterdir() if x.is_file()]}
pathlib.Path('production/mafia-temple/diagnostics-v2.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
PY
