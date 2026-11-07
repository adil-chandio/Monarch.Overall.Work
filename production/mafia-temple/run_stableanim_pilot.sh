#!/usr/bin/env bash
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
slug="monarch-run-research-${GITHUB_RUN_ID:-manual}";dir="/tmp/mafia-kernel/$slug";ref="$KAGGLE_USERNAME/$slug"
mkdir -p production/mafia-temple/run-pilot-output
python production/mafia-temple/make_stableanim_pilot.py --user "$KAGGLE_USERNAME" --slug "$slug" --out "$dir"
kaggle kernels push -p "$dir"
for ((i=0;i<250;i++)); do
 status=$(kaggle kernels status "$ref" 2>&1) || { echo 'Kaggle status query failed'; exit 1; }
 echo "$ref: $status"
 case "$status" in
  *COMPLETE*|*complete*)
   mkdir -p "$dir/out"
   kaggle kernels output "$ref" -p "$dir/out" --file-pattern '(^|/)(run-motion-pilot\.mp4|run-pilot-receipt\.json)$'
   find "$dir/out" -name 'run-motion-pilot.mp4' -type f -size +10k -exec cp '{}' production/mafia-temple/run-pilot-output/ \;
   find "$dir/out" -name 'run-pilot-receipt.json' -type f -exec cp '{}' production/mafia-temple/run-pilot-output/ \;
   test -s production/mafia-temple/run-pilot-output/run-motion-pilot.mp4; exit 0;;
  *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*)
   export PILOT_KERNEL_SLUG="$slug"
   python production/mafia-temple/stableanim_diagnose.py
   exit 0;;
 esac
 sleep 25
done
echo 'Running research pilot timed out';exit 1
