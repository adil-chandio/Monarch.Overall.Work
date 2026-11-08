#!/usr/bin/env bash
set -euo pipefail
: "${KAGGLE_USERNAME:?}" "${GH_TOKEN:?}"
slug="monarch-ltx23-${GITHUB_RUN_ID:?}"; ref="$KAGGLE_USERNAME/$slug"; dir="/tmp/$slug"; out="$dir/out"
python production/mafia-temple/make_ltx23_pilot.py --user "$KAGGLE_USERNAME" --slug "$slug" --out "$dir"
kaggle kernels push -p "$dir"
echo "::notice title=Private GPU benchmark::Kernel $ref submitted"
for ((i=0;i<100;i++)); do
  status=$(kaggle kernels status "$ref" 2>&1) || { echo 'Transient status error'; sleep 45; continue; }
  echo "$status"
  case "$status" in
    *COMPLETE*|*complete*)
      mkdir -p "$out"
      kaggle kernels output "$ref" -p "$out" --file-pattern '(^|/)(ltx23-running-[ab]\.mp4|ltx23-receipt\.json)$'
      export LTX_OUTPUT="$out"
      python production/mafia-temple/relay_ltx23_output.py
      exit 0;;
    *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*)
      PILOT_KERNEL_SLUG="$slug" python production/mafia-temple/onetoall_diagnose.py || true
      python - <<'PY'
from pathlib import Path
p=Path('production/mafia-temple/onetoall-diagnostics.txt')
if p.exists():
    text='\n'.join(p.read_text(errors='replace').splitlines()[-25:])[-3500:]
    print('::notice title=LTX23 failure tail::'+text.replace('%','%25').replace('\n','%0A'))
PY
      exit 1;;
  esac
  sleep 45
done
echo 'Timed out without submitting another kernel'; exit 1
