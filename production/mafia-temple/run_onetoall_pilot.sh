#!/usr/bin/env bash
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
slug="monarch-onetoall-run-${GITHUB_RUN_ID:-manual}"
dir="/tmp/mafia-kernel/$slug"
ref="$KAGGLE_USERNAME/$slug"
out="production/mafia-temple/onetoall-pilot-output"
mkdir -p "$out"
python production/mafia-temple/make_onetoall_pilot.py --user "$KAGGLE_USERNAME" --slug "$slug" --out "$dir"
kaggle kernels push -p "$dir"
for ((i=0;i<270;i++)); do
  status=$(kaggle kernels status "$ref" 2>&1) || { echo 'Kaggle status query failed'; exit 1; }
  echo "$ref: $status"
  case "$status" in
    *COMPLETE*|*complete*)
      mkdir -p "$dir/out"
      kaggle kernels output "$ref" -p "$dir/out" --file-pattern '(^|/)(onetoall-running-pilot\.mp4|onetoall-receipt\.json|pose-audit\.json|pose-audit\.jpg|warped-ref-audit\.jpg|output-metadata\.json)$'
      for f in onetoall-running-pilot.mp4 onetoall-receipt.json pose-audit.json pose-audit.jpg warped-ref-audit.jpg output-metadata.json; do
        found=$(find "$dir/out" -type f -name "$f" -print -quit)
        if [ -z "$found" ]; then echo "Missing fresh result $f"; exit 1; fi
        cp "$found" "$out/$f"
      done
      test -s "$out/onetoall-running-pilot.mp4"
      exit 0;;
    *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*)
      export PILOT_KERNEL_SLUG="$slug"
      python production/mafia-temple/stableanim_diagnose.py
      cp production/mafia-temple/run-pilot-output/run-pilot-diagnostics.json "$out/failure-diagnostics.json"
      python - <<'PY'
import json
p='production/mafia-temple/onetoall-pilot-output/failure-diagnostics.json'
d=json.load(open(p))
for line in d.get('events', [])[-30:]: print('REMOTE_DIAGNOSTIC:',line[:300])
for line in d.get('tail', [])[-10:]: print('REMOTE_TAIL:',line[:300])
PY
      exit 1;;
  esac
  sleep 25
done
echo 'Research pilot status timed out';exit 1
