#!/usr/bin/env bash
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
slug="monarch-motion-v2-${GITHUB_RUN_ID:-manual}"
dir="/tmp/mafia-kernel/$slug"
ref="$KAGGLE_USERNAME/$slug"
scenes="v2runA,v2faceA,v2runB,v2faceB"
python production/mafia-temple/make_kernel.py --user "$KAGGLE_USERNAME" --slug "$slug" --only "$scenes" --out "$dir"
kaggle kernels push -p "$dir"
for ((i=0;i<250;i++)); do
  status=$(kaggle kernels status "$ref" 2>&1) || { echo 'Kaggle status query failed'; exit 1; }
  echo "$ref: $status"
  case "$status" in
    *COMPLETE*|*complete*)
      mkdir -p "$dir/out" production/mafia-temple/clips
      kaggle kernels output "$ref" -p "$dir/out"
      find "$dir/out" -name '*.mp4' -type f -size +20k -exec cp '{}' production/mafia-temple/clips/ \;
      find "$dir/out" -name 'receipts_*.json' -type f -exec cp '{}' production/mafia-temple/clips/ \;
      for name in v2runA v2runB v2faceA v2faceB; do [ -s "production/mafia-temple/clips/$name.mp4" ]; done
      exit 0 ;;
    *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*) echo "Kaggle kernel failed: $ref"; exit 1 ;;
  esac
  sleep 25
done
echo 'GPU render timed out'; exit 1
