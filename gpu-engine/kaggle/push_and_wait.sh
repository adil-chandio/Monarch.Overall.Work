#!/usr/bin/env bash
set -uo pipefail

CHUNKS="${1:-s01,s02,s03,s04;s05,s06,s07,s08}"
OUT_CLIPS="${2:-gpu-engine/clips}"
SLUG_PREFIX="${SLUG_PREFIX:-monarch-b2b-v1}"
POLL_MAX="${POLL_MAX:-90}"
POLL_SLEEP="${POLL_SLEEP:-35}"
BRANCH="${GITHUB_REF_NAME:-arena/9960286a-monarch-overall-work}"

mkdir -p "$OUT_CLIPS" /tmp/kwork

echo "::notice::Kaggle user=${KAGGLE_USERNAME} | chunks=${CHUNKS}"

IFS=';' read -ra PARTS <<< "$CHUNKS"
REFS=()
DIRS=()

IDX=0
for ONLY in "${PARTS[@]}"; do
  [ -z "$ONLY" ] && continue
  IDX=$((IDX + 1))
  SLUG="${SLUG_PREFIX}-${IDX}"
  KDIR="/tmp/kwork/${SLUG}"
  REF="${KAGGLE_USERNAME}/${SLUG}"

  python3 gpu-engine/kaggle/make_b2b_kernel.py \
    --user "$KAGGLE_USERNAME" \
    --slug "$SLUG" \
    --only "$ONLY" \
    --branch "$BRANCH" \
    --out "$KDIR"

  echo "Pushing kernel $REF ($ONLY)..."
  PUSH_OUT=$(kaggle kernels push -p "$KDIR" 2>&1)
  PUSH_RC=$?
  echo "$PUSH_OUT"
  if [ "$PUSH_RC" -ne 0 ]; then
    echo "::error::Failed pushing $REF: $PUSH_OUT"
    exit 1
  fi
  REFS+=("$REF")
  DIRS+=("$KDIR")
  sleep 12
done

# Poll all pushed kernels until complete
for i in "${!REFS[@]}"; do
  REF="${REFS[$i]}"
  KDIR="${DIRS[$i]}"
  echo "Waiting on $REF..."
  STEP=0
  while [ "$STEP" -lt "$POLL_MAX" ]; do
    ST=$(kaggle kernels status "$REF" 2>&1 | tail -n 1)
    echo "[$(date -u +%H:%M:%S)] $REF -> $ST"
    case "$ST" in
      *COMPLETE*|*complete*)
        echo "::notice::$REF completed!"
        break
        ;;
      *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*)
        echo "::error::$REF failed: $ST"
        kaggle kernels output "$REF" -p "$KDIR/out" 2>&1 || true
        cat "$KDIR/out"/*.log 2>/dev/null | tail -n 80 || true
        exit 1
        ;;
    esac
    STEP=$((STEP + 1))
    sleep "$POLL_SLEEP"
  done

  mkdir -p "$KDIR/out"
  kaggle kernels output "$REF" -p "$KDIR/out" 2>&1 | tail -n 10 || true
  find "$KDIR/out" -name "*.mp4" -size +20k -exec cp -f {} "$OUT_CLIPS"/ \;
  find "$KDIR/out" -name "receipts_*.json" -exec cp -f {} "$OUT_CLIPS"/ \;
done

COUNT=$(find "$OUT_CLIPS" -name "s*.mp4" -size +20k | wc -l | tr -d ' ')
echo "::notice::Downloaded $COUNT AI motion clips into $OUT_CLIPS"
ls -lh "$OUT_CLIPS"
if [ "$COUNT" -lt 8 ]; then
  echo "::error::Expected 8 clips, got $COUNT"
  exit 1
fi
