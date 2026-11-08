#!/usr/bin/env bash
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
slug="monarch-front-turn-v4-research-${GITHUB_RUN_ID:-manual}";dir="/tmp/mafia-kernel/$slug";ref="$KAGGLE_USERNAME/$slug"
python production/mafia-temple/make_liveportrait_pilot.py --user "$KAGGLE_USERNAME" --slug "$slug" --out "$dir" --front-turn-v4
kaggle kernels push -p "$dir"
for ((i=0;i<160;i++)); do
 status=$(kaggle kernels status "$ref" 2>&1) || { echo 'Kaggle status query failed'; exit 1; }
 echo "$ref: $status"
 case "$status" in
  *COMPLETE*|*complete*)
   mkdir -p "$dir/out" production/mafia-temple/portrait-turn-output
   kaggle kernels output "$ref" -p "$dir/out" --file-pattern '(^|/)(front-turn-v4--turn-driver\.mp4|liveportrait-front-turn-v4-receipt\.json)$'
   test -n "$(find "$dir/out" -name liveportrait-front-turn-v4-receipt.json -type f -print -quit)"
   find "$dir/out" -name 'front-turn-v4--turn-driver.mp4' -type f -size +10k -exec cp '{}' production/mafia-temple/portrait-turn-output/ \;
   find "$dir/out" -name 'liveportrait-front-turn-v4-receipt.json' -type f -exec cp '{}' production/mafia-temple/portrait-turn-output/ \;
   exit 0;;
  *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*) echo "Research pilot failed: $ref"; exit 1;;
 esac
 sleep 25
done
echo 'Portrait turn pilot timed out';exit 1
