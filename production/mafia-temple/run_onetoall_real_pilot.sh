#!/usr/bin/env bash
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
stage=${1:?preflight or render required}
case "$stage" in preflight|render);; *) exit 2;; esac
slug="monarch-real-$stage-${GITHUB_RUN_ID:-manual}"
dir="/tmp/mafia-kernel/$slug"; ref="$KAGGLE_USERNAME/$slug"
out="/tmp/onetoall-real-$stage-output"; mkdir -p "$out"
python production/mafia-temple/make_onetoall_real_pilot.py --user "$KAGGLE_USERNAME" --slug "$slug" --out "$dir" --stage "$stage"
kaggle kernels push -p "$dir"
for ((i=0;i<180;i++)); do
  if ! status=$(kaggle kernels status "$ref" 2>&1); then
    echo 'Status query failed; waiting before rechecking existing kernel.'; sleep 60; continue
  fi
  echo "$ref: $status"
  case "$status" in
    *COMPLETE*|*complete*)
      mkdir -p "$dir/out"
      kaggle kernels output "$ref" -p "$dir/out" --file-pattern '(^|/)(onetoall-running-pilot\.mp4|onetoall-receipt\.json|pose-audit\.json|pose-audit\.jpg|pose-frames-[0-9]+\.jpg|warped-ref-audit\.jpg|output-metadata\.json|preflight-complete\.txt)$'
      files=(onetoall-receipt.json pose-audit.json pose-audit.jpg warped-ref-audit.jpg)
      for i in 000 007 014 021 028 035 042; do files+=("pose-frames-$i.jpg"); done
      if [ "$stage" = preflight ]; then files+=(preflight-complete.txt); else files+=(onetoall-running-pilot.mp4 output-metadata.json); fi
      for f in "${files[@]}"; do
        found=$(find "$dir/out" -type f -name "$f" -print -quit)
        [ -n "$found" ] || { echo "Missing fresh result $f"; exit 1; }
        cp "$found" "$out/$f"
      done
      python production/mafia-temple/relay_real_output.py "$out" "$stage"
      exit 0;;
    *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*)
      export PILOT_KERNEL_SLUG="$slug"
      python production/mafia-temple/onetoall_diagnose.py || true
      if [ -f production/mafia-temple/onetoall-diagnostics.txt ]; then
        tail -60 production/mafia-temple/onetoall-diagnostics.txt
      fi
      exit 1;;
  esac
  sleep 60
done
echo 'Status timed out without launching another job'; exit 1
