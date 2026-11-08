#!/usr/bin/env bash
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
slug="monarch-walk-research-${GITHUB_RUN_ID:-manual}";dir="/tmp/mafia-kernel/$slug";ref="$KAGGLE_USERNAME/$slug"
python production/mafia-temple/make_stableanim_walk.py --user "$KAGGLE_USERNAME" --slug "$slug" --out "$dir"
kaggle kernels push -p "$dir"
for ((i=0;i<250;i++)); do
 status=$(kaggle kernels status "$ref" 2>&1) || { echo 'Kaggle status query failed'; exit 1; }
 echo "$ref: $status"
 case "$status" in
  *COMPLETE*|*complete*)
   mkdir -p "$dir/out" production/mafia-temple/walk-pilot-output
   kaggle kernels output "$ref" -p "$dir/out" --file-pattern '(^|/)(walk-motion-pilot-v2\.mp4|walk-pilot-v2-receipt\.json)$'
   video=$(find "$dir/out" -name walk-motion-pilot-v2.mp4 -type f -size +10k -print -quit)
   receipt=$(find "$dir/out" -name walk-pilot-v2-receipt.json -type f -print -quit)
   test -n "$video" && test -n "$receipt"
   cp "$video" "$receipt" production/mafia-temple/walk-pilot-output/
   exit 0;;
  *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*)
   PILOT_KERNEL_SLUG="$slug" python production/mafia-temple/stableanim_diagnose.py
   exit 0;;
 esac
 sleep 25
done
echo 'Walking test timed out'; exit 1
