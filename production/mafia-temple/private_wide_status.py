"""Report only a coarse private Kaggle kernel state; never download its output."""
import subprocess
from private_wide_driver import kaggle_env

env, user = kaggle_env()
ref = user + '/monarch-private-wide-42648167419'
try:
    result = subprocess.run(['kaggle', 'kernels', 'status', ref], env=env,
                            capture_output=True, text=True, timeout=45)
    text = (result.stdout + ' ' + result.stderr).upper()
    state = next((s for s in ('COMPLETE', 'ERROR', 'CANCEL', 'FAIL', 'RUNNING', 'QUEUED') if s in text), 'UNKNOWN')
    print('::notice title=private-kaggle-state::' + state, flush=True)
    if result.returncode:
        raise RuntimeError('Status check failed')
except Exception as exc:
    print('::error title=private-kaggle-status-error::' + type(exc).__name__, flush=True)
    raise SystemExit(1)
