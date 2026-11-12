#!/usr/bin/env bash
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
slug="monarch-face-research-${GITHUB_RUN_ID:-manual}";dir="/tmp/mafia-kernel/$slug";ref="$KAGGLE_USERNAME/$slug"
python production/mafia-temple/make_liveportrait_pilot.py --user "$KAGGLE_USERNAME" --slug "$slug" --out "$dir"
kaggle kernels push -p "$dir"
for ((i=0;i<160;i++)); do
 status=$(kaggle kernels status "$ref" 2>&1) || { echo 'Kaggle status query failed'; exit 1; }
 echo "$ref: $status"
 case "$status" in
  *COMPLETE*|*complete*)
   mkdir -p "$dir/out" production/mafia-temple/portrait-pilot-output
   kaggle kernels output "$ref" -p "$dir/out" --file-pattern '(^|/)(side--d0\.mp4|front--d0\.mp4|liveportrait-receipts\.json)$'
   find "$dir/out" -name '*--d0.mp4' -type f -size +10k -exec cp '{}' production/mafia-temple/portrait-pilot-output/ \;
   find "$dir/out" -name 'liveportrait-receipts.json' -type f -exec cp '{}' production/mafia-temple/portrait-pilot-output/ \;
   [ -s production/mafia-temple/portrait-pilot-output/liveportrait-receipts.json ]; exit 0;;
  *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*) echo "Research pilot failed: $ref"; exit 1;;
 esac
 sleep 25
done
echo 'Portrait pilot timed out';exit 1
