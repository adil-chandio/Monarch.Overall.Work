"""Short, disposable Kaggle GPU availability probe. No user media is sent.

Creates one uniquely named private kernel, checks whether it reaches a GPU,
then deletes only that kernel. It does not touch the queued research kernel.
Outputs only coarse diagnostic states; never raw CLI errors or credentials.
"""
import json
import os
import pathlib
import re
import subprocess
import tempfile
import time
from private_wide_driver import kaggle_env


def run(argv, env, timeout=45):
    return subprocess.run(argv, env=env, capture_output=True, text=True, timeout=timeout)


def main():
    env, username = kaggle_env()
    run_id = os.environ['GITHUB_RUN_ID']
    if not re.fullmatch(r'[0-9]+', run_id):
        raise ValueError('Invalid run ID')
    slug = 'monarch-gpu-availability-' + run_id
    ref = username + '/' + slug
    submitted = False
    try:
        with tempfile.TemporaryDirectory(prefix='gpu-probe-') as tmp:
            root = pathlib.Path(tmp)
            code = ("import json,torch\n"
                    "result={'gpu_count':torch.cuda.device_count()}\n"
                    "open('/kaggle/working/gpu-probe.json','w').write(json.dumps(result))\n")
            nb = {'cells': [{'cell_type':'code', 'execution_count':None, 'metadata':{}, 'outputs':[], 'source':code.splitlines(True)}],
                  'metadata': {'kernelspec': {'display_name':'Python 3', 'language':'python', 'name':'python3'},
                               'language_info': {'name':'python'}}, 'nbformat':4, 'nbformat_minor':5}
            (root/'main.ipynb').write_text(json.dumps(nb))
            meta = {'id':ref, 'title':slug, 'code_file':'main.ipynb', 'language':'python', 'kernel_type':'notebook',
                    'is_private':True, 'enable_gpu':True, 'enable_internet':False, 'dataset_sources':[],
                    'competition_sources':[], 'kernel_sources':[], 'model_sources':[], 'machine_shape':'NvidiaTeslaT4'}
            (root/'kernel-metadata.json').write_text(json.dumps(meta))
            result = run(['kaggle','kernels','push','-p',str(root)],env,90)
            if result.returncode:
                text = (result.stdout + result.stderr).lower()
                label = 'account slot limit' if ('maximum' in text and ('session' in text or 'kernel' in text)) else 'push failed'
                print('::notice title=private-gpu-probe::' + label, flush=True)
                return
            submitted = True
            last = 'UNKNOWN'
            for _ in range(20):
                result = run(['kaggle','kernels','status',ref],env)
                text = (result.stdout + ' ' + result.stderr).upper()
                state = next((s for s in ('COMPLETE','ERROR','CANCEL','FAIL','RUNNING','QUEUED') if s in text),'UNKNOWN')
                last = state
                if state == 'COMPLETE':
                    out = root/'out'; out.mkdir()
                    r = run(['kaggle','kernels','output',ref,'-p',str(out),'--file-pattern','gpu-probe[.]json$'],env,90)
                    paths = list(out.rglob('gpu-probe.json'))
                    if r.returncode or len(paths) != 1:
                        print('::notice title=private-gpu-probe::COMPLETE, receipt unavailable', flush=True)
                    else:
                        count = json.loads(paths[0].read_text()).get('gpu_count')
                        if not isinstance(count,int) or not 0 <= count <= 8:
                            raise ValueError('Invalid GPU count')
                        print('::notice title=private-gpu-probe::COMPLETE; gpu_count=' + str(count), flush=True)
                    return
                if state in ('ERROR','CANCEL','FAIL'):
                    break
                time.sleep(15)
            print('::notice title=private-gpu-probe::' + last, flush=True)
    finally:
        if submitted:
            # This is the exact throwaway slug created above, never user data.
            result = run(['kaggle','kernels','delete',ref,'-y'],env,90)
            print('::notice title=private-gpu-probe-cleanup::' + ('deleted' if not result.returncode else 'not confirmed'), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('::notice title=private-gpu-probe::Unavailable: ' + type(exc).__name__, flush=True)
