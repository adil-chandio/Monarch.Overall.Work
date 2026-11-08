#!/usr/bin/env bash
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
slug="monarch-depth-research-${GITHUB_RUN_ID:-manual}";dir="/tmp/mafia-kernel/$slug";ref="$KAGGLE_USERNAME/$slug"
python production/mafia-temple/make_depth_pilot.py --user "$KAGGLE_USERNAME" --slug "$slug" --out "$dir"
kaggle kernels push -p "$dir"
for ((i=0;i<100;i++)); do
 status=$(kaggle kernels status "$ref" 2>&1) || { echo 'Kaggle status query failed'; exit 1; }
 echo "$ref: $status"
 case "$status" in
  *COMPLETE*|*complete*)
   mkdir -p "$dir/out" production/mafia-temple/depth-pilot-output
   kaggle kernels output "$ref" -p "$dir/out" --file-pattern '(^|/)(aerial-relative-depth\.png|courtyard-relative-depth\.png|street-relative-depth\.png|depth-receipt\.json)$'
   for f in aerial-relative-depth.png courtyard-relative-depth.png street-relative-depth.png depth-receipt.json; do
    path=$(find "$dir/out" -name "$f" -type f -size +100c -print -quit);test -n "$path";cp "$path" production/mafia-temple/depth-pilot-output/
   done
   exit 0;;
  *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*) echo "Depth research failed: $ref";exit 1;;
 esac
 sleep 25
done
echo 'Depth pilot timed out';exit 1
