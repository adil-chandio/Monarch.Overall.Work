#!/usr/bin/env bash
set -uo pipefail

OUT_CLIPS="${2:-gpu-engine/clips}"
SLUG_PREFIX="${SLUG_PREFIX:-monarch-b2b-v5}"
POLL_MAX="${POLL_MAX:-110}"
POLL_SLEEP="${POLL_SLEEP:-30}"
BRANCH="${GITHUB_REF_NAME:-arena/9960286a-monarch-overall-work}"

mkdir -p "$OUT_CLIPS" /tmp/kwork

echo "::notice::Kaggle user=${KAGGLE_USERNAME} | harvesting any completed prior kernels first..."

# Harvest any clips already completed on v4-1 / v4-2 so zero GPU work is wasted!
for PREV_SLUG in monarch-b2b-v4-2 monarch-b2b-v4-1; do
  PREV_REF="${KAGGLE_USERNAME}/${PREV_SLUG}"
  PREV_ST=$(kaggle kernels status "$PREV_REF" 2>&1 | tail -n 1 || true)
  echo "Prior kernel $PREV_REF -> $PREV_ST"
  # If v4-2 is still finishing right now, wait up to 4 minutes for it!
  if echo "$PREV_ST" | grep -qi "running"; then
    for w in $(seq 1 8); do
      sleep 30
      PREV_ST=$(kaggle kernels status "$PREV_REF" 2>&1 | tail -n 1 || true)
      echo "  waiting $PREV_REF -> $PREV_ST"
      echo "$PREV_ST" | grep -qi "running" || break
    done
  fi
  if echo "$PREV_ST" | grep -qi "complete"; then
    mkdir -p "/tmp/kwork/${PREV_SLUG}_out"
    kaggle kernels output "$PREV_REF" -p "/tmp/kwork/${PREV_SLUG}_out" 2>&1 || true
    find "/tmp/kwork/${PREV_SLUG}_out" -name "*.mp4" -size +20k -exec cp -f {} "$OUT_CLIPS"/ \;
    find "/tmp/kwork/${PREV_SLUG}_out" -name "receipts_*.json" -exec cp -f {} "$OUT_CLIPS"/ \;
  fi
done

HARVESTED=$(find "$OUT_CLIPS" -name "s*.mp4" -size +20k | sort | tr '\n' ' ')
echo "::notice::Harvested prior clips: ${HARVESTED:-none}"

# Compute exact missing scenes out of s01..s08
MISSING=()
for SID in s01 s02 s03 s04 s05 s06 s07 s08; do
  if [ ! -s "${OUT_CLIPS}/${SID}.mp4" ]; then
    MISSING+=("$SID")
  fi
done

echo "Missing scenes (${#MISSING[@]}): ${MISSING[*]:-none}"

if [ "${#MISSING[@]}" -gt 0 ]; then
  # Split missing scenes across up to 3 parallel Dual-T4 kernels (max 6 T4 GPUs!) so each GPU renders ~1 scene (~6 min total!)
  N_MISS="${#MISSING[@]}"
  if [ "$N_MISS" -le 2 ]; then
    PARTS=("$(IFS=,; echo "${MISSING[*]}")")
  elif [ "$N_MISS" -le 4 ]; then
    P1=("${MISSING[@]:0:2}")
    P2=("${MISSING[@]:2:2}")
    PARTS=("$(IFS=,; echo "${P1[*]}")" "$(IFS=,; echo "${P2[*]}")")
  else
    P1=("${MISSING[@]:0:3}")
    P2=("${MISSING[@]:3:3}")
    P3=("${MISSING[@]:6:2}")
    PARTS=("$(IFS=,; echo "${P1[*]}")" "$(IFS=,; echo "${P2[*]}")")
    [ "${#P3[@]}" -gt 0 ] && PARTS+=("$(IFS=,; echo "${P3[*]}")")
  fi

  echo "::notice::Dispatching ${#PARTS[@]} Dual-T4 kernels for missing scenes: ${PARTS[*]}"

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
    echo "::notice::Pushed Kaggle Dual-T4 kernel $REF ($ONLY) -> $PUSH_OUT"
    REFS+=("$REF")
    DIRS+=("$KDIR")
    sleep 10
  done

  # Poll all kernels concurrently in a single unified loop so finished kernels harvest immediately!
  DONE_FLAGS=()
  for i in "${!REFS[@]}"; do DONE_FLAGS[$i]=0; done

  STEP=0
  while [ "$STEP" -lt "$POLL_MAX" ]; do
    ALL_DONE=1
    for i in "${!REFS[@]}"; do
      [ "${DONE_FLAGS[$i]}" -eq 1 ] && continue
      ALL_DONE=0
      REF="${REFS[$i]}"
      KDIR="${DIRS[$i]}"
      ST=$(kaggle kernels status "$REF" 2>&1 | tail -n 1)
      echo "[$(date -u +%H:%M:%S)] $REF -> $ST"
      case "$ST" in
        *COMPLETE*|*complete*)
          echo "::notice::$REF completed!"
          mkdir -p "$KDIR/out"
          kaggle kernels output "$REF" -p "$KDIR/out" 2>&1 | tail -n 10 || true
          find "$KDIR/out" -name "*.mp4" -size +20k -exec cp -f {} "$OUT_CLIPS"/ \;
          find "$KDIR/out" -name "receipts_*.json" -exec cp -f {} "$OUT_CLIPS"/ \;
          DONE_FLAGS[$i]=1
          ;;
        *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*)
          mkdir -p "$KDIR/out"
          kaggle kernels output "$REF" -p "$KDIR/out" 2>&1 || true
          KOUT_DIR="$KDIR/out" REF_NAME="$REF" ST_MSG="$ST" python3 - <<'PY'
import glob, json, os
kout = os.environ["KOUT_DIR"]
joined = ""
for p in glob.glob(f"{kout}/*.log"):
    try:
        items = json.loads(open(p).read())
        lines = [x.get("data", "") for x in items if "NbConvertApp" not in x.get("data", "") and "SyntaxWarning" not in x.get("data", "")]
        joined += "".join(lines)
    except Exception:
        joined += open(p, errors="ignore").read()
for p in glob.glob(f"{kout}/*.txt"):
    joined += "\n" + open(p, errors="ignore").read()[-1200:]
clean = joined.replace("\r", " ").replace("\n", " | ")
print(f"::error::{os.environ['REF_NAME']} failed ({os.environ['ST_MSG']}): {clean[-1800:]}", flush=True)
PY
          DONE_FLAGS[$i]=1
          ;;
      esac
    done
    [ "$ALL_DONE" -eq 1 ] && break
    STEP=$((STEP + 1))
    sleep "$POLL_SLEEP"
  done
fi

COUNT=$(find "$OUT_CLIPS" -name "s*.mp4" -size +20k | wc -l | tr -d ' ')
FOUND_LIST=$(find "$OUT_CLIPS" -name "s*.mp4" -size +20k | sort | tr '\n' ' ')
echo "::notice::Final AI motion clips ($COUNT/8): $FOUND_LIST"
ls -lh "$OUT_CLIPS"
if [ "$COUNT" -lt 8 ]; then
  echo "::error::Expected 8 clips, got $COUNT ($FOUND_LIST)"
  exit 1
fi
