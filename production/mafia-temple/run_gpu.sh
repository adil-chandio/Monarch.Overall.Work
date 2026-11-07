#!/usr/bin/env bash
# Private Kaggle kernels, only for this project's six distinct keyframes.
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
mkdir -p production/mafia-temple/clips /tmp/mafia-kernel
run_id="${GITHUB_RUN_ID:-manual}"
refs=()
for i in 1 2; do
  case "$i" in 1) scenes='s01,s02,s03';; 2) scenes='s04,s05a,s05b';; esac
  slug="monarch-mafia-${run_id}-${i}"
  dir="/tmp/mafia-kernel/$slug"
  python production/mafia-temple/make_kernel.py --user "$KAGGLE_USERNAME" --slug "$slug" --only "$scenes" --out "$dir"
  kaggle kernels push -p "$dir"
  refs+=("$KAGGLE_USERNAME/$slug")
  sleep 8
done
finished=(0 0)
for ((attempt=0;attempt<150;attempt++)); do
  all_done=1
  for i in 0 1; do
    if [ "${finished[$i]}" = 1 ]; then continue; fi
    all_done=0
    ref="${refs[$i]}"
    status=$(kaggle kernels status "$ref" 2>&1) || { echo "Kaggle status query failed for $ref"; exit 1; }
    echo "$ref: $status"
    case "$status" in
      *COMPLETE*|*complete*)
        out="/tmp/mafia-kernel/out-$i"; mkdir -p "$out"
        kaggle kernels output "$ref" -p "$out"
        find "$out" -name '*.mp4' -type f -size +20k -exec cp '{}' production/mafia-temple/clips/ \;
        find "$out" -name 'receipts_*.json' -type f -exec cp '{}' production/mafia-temple/clips/ \;
        finished[$i]=1 ;;
      *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*)
        echo "Kaggle kernel failed: $ref"; exit 1 ;;
    esac
  done
  if [ "$all_done" = 1 ]; then break; fi
  sleep 25
done
for id in s01 s02 s03 s04 s05a s05b; do
  [ -s "production/mafia-temple/clips/$id.mp4" ] || { echo "Missing clip $id"; exit 1; }
done
echo 'All six AI-motion clips are present.'
