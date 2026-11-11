#!/usr/bin/env bash
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
slug="monarch-walk-${GITHUB_RUN_ID:-manual}"
dir="/tmp/mafia-kernel/$slug"
ref="$KAGGLE_USERNAME/$slug"
python production/mafia-temple/make_kernel.py --user "$KAGGLE_USERNAME" --slug "$slug" --only s01a,s01b --out "$dir"
kaggle kernels push -p "$dir"
for ((i=0;i<150;i++)); do
  status=$(kaggle kernels status "$ref" 2>&1) || { echo 'Kaggle status query failed'; exit 1; }
  echo "$ref: $status"
  case "$status" in
    *COMPLETE*|*complete*)
      mkdir -p "$dir/out" production/mafia-temple/clips
      kaggle kernels output "$ref" -p "$dir/out"
      find "$dir/out" -name '*.mp4' -type f -size +20k -exec cp '{}' production/mafia-temple/clips/ \;
      find "$dir/out" -name 'receipts_*.json' -type f -exec cp '{}' production/mafia-temple/clips/ \;
      [ -s production/mafia-temple/clips/s01a.mp4 ] && [ -s production/mafia-temple/clips/s01b.mp4 ]
      exit 0 ;;
    *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*) echo "Kaggle kernel failed: $ref"; exit 1 ;;
  esac
  sleep 25
done
echo 'GPU render timed out'; exit 1
