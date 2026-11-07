#!/usr/bin/env bash
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
slug="monarch-run-hands-research-${GITHUB_RUN_ID:-manual}";dir="/tmp/mafia-kernel/$slug";ref="$KAGGLE_USERNAME/$slug"
mkdir -p production/mafia-temple/run-pilot-output
python production/mafia-temple/make_stableanim_pilot.py --user "$KAGGLE_USERNAME" --slug "$slug" --out "$dir" --hands
kaggle kernels push -p "$dir"
for ((i=0;i<250;i++)); do
 status=$(kaggle kernels status "$ref" 2>&1) || { echo 'Kaggle status query failed'; exit 1; }
 echo "$ref: $status"
 case "$status" in
  *COMPLETE*|*complete*)
   mkdir -p "$dir/out"
   kaggle kernels output "$ref" -p "$dir/out" --file-pattern '(^|/)(run-motion-pilot-v4-hands\.mp4|run-pilot-v4-hands-receipt\.json)$'
   find "$dir/out" -name 'run-motion-pilot-v4-hands.mp4' -type f -size +10k -exec cp '{}' production/mafia-temple/run-pilot-output/ \;
   find "$dir/out" -name 'run-pilot-v4-hands-receipt.json' -type f -exec cp '{}' production/mafia-temple/run-pilot-output/ \;
   # Check the fresh download, not a possibly stale checked-in pilot.
   test -n "$(find "$dir/out" -name 'run-motion-pilot-v4-hands.mp4' -type f -size +10k -print -quit)"
   test -n "$(find "$dir/out" -name 'run-pilot-v4-hands-receipt.json' -type f -print -quit)"
   rm -f production/mafia-temple/run-pilot-output/run-pilot-diagnostics.json; exit 0;;
  *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*)
   export PILOT_KERNEL_SLUG="$slug"
   python production/mafia-temple/stableanim_diagnose.py
   exit 0;;
 esac
 sleep 25
done
echo 'Running research pilot timed out';exit 1
