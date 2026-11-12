#!/usr/bin/env bash
# Recover the existing long-gait Kaggle test, without rerunning inference.
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
slug=monarch-run-research-42419317846
ref="$KAGGLE_USERNAME/$slug"
status=$(kaggle kernels status "$ref" 2>&1)
echo "Recovery status: $status"
case "$status" in
  *COMPLETE*|*complete*)
    dir=$(mktemp -d)
    trap 'rm -rf "$dir"' EXIT
    kaggle kernels output "$ref" -p "$dir" --file-pattern '(^|/)(run-motion-pilot-v3\.mp4|run-pilot-v3-receipt\.json)$'
    video=$(find "$dir" -name 'run-motion-pilot-v3.mp4' -type f -size +10k -print -quit)
    receipt=$(find "$dir" -name 'run-pilot-v3-receipt.json' -type f -print -quit)
    test -n "$video" && test -n "$receipt"
    mkdir -p production/mafia-temple/run-pilot-output
    cp "$video" "$receipt" production/mafia-temple/run-pilot-output/
    rm -f production/mafia-temple/run-pilot-output/run-pilot-diagnostics.json
    ;;
  *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*)
    PILOT_KERNEL_SLUG="$slug" python production/mafia-temple/stableanim_diagnose.py
    ;;
  *) echo 'Kaggle pilot is not finished'; exit 1;;
esac
