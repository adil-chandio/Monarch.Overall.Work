#!/usr/bin/env bash
# Push the v3 voice-alignment kernel to Kaggle (GPU T4 x2), wait for it, pull the
# word timings back. Every number this prints is Kaggle's, not ours.
set -uo pipefail

SLUG_PREFIX="${SLUG_PREFIX:-monarch-v3-voice}"
OUT_DIR="${OUT_DIR:-public/demo/gpu}"
POLL_MAX="${POLL_MAX:-90}"
POLL_SLEEP="${POLL_SLEEP:-20}"

python3 -m pip install --disable-pip-version-check -q -U kaggle six requests 2>/dev/null || true

mkdir -p "$OUT_DIR" /tmp/vkwork
STAMP=$(date -u +%H%M%S)
SLUG="${SLUG_PREFIX}-${STAMP}"
REF="${KAGGLE_USERNAME}/${SLUG}"
KDIR="/tmp/vkwork/${SLUG}"

echo "::notice::packaging kernel ${REF} for ${KAGGLE_USERNAME}"
python3 tools/kaggle/make_voice_kernel.py --user "${KAGGLE_USERNAME}" --slug "${SLUG}" --out "${KDIR}" || exit 1

echo "::notice::pushing ${REF}"
PUSH_OUT=$(kaggle kernels push -p "${KDIR}" 2>&1)
PUSH_RC=$?
echo "${PUSH_OUT}"
if [ "${PUSH_RC}" -ne 0 ] || echo "${PUSH_OUT}" | grep -qi "error"; then
  echo "::error::kaggle push failed: ${PUSH_OUT}"
  exit 1
fi

STEP=0
STATUS=""
while [ "${STEP}" -lt "${POLL_MAX}" ]; do
  STEP=$((STEP + 1))
  STATUS=$(kaggle kernels status "${REF}" 2>&1 | tail -n 1)
  echo "[$(date -u +%H:%M:%S)] ${REF} -> ${STATUS}"
  case "${STATUS}" in
    *COMPLETE*|*complete*) break ;;
    *ERROR*|*error*|*CANCEL*|*cancel*|*FAIL*) break ;;
  esac
  sleep "${POLL_SLEEP}"
done

mkdir -p "${KDIR}/out"
kaggle kernels output "${REF}" -p "${KDIR}/out" 2>&1 | tail -n 20 || true
ls -lR "${KDIR}/out" | head -40

# Kaggle returns the output tree as-is; the kernel writes into monarch_out/, so
# search rather than assuming a depth.
find "${KDIR}/out" -name words.json -exec cp -f {} "${OUT_DIR}/words.json" \; 2>/dev/null || true
find "${KDIR}/out" -name receipts_gpu.json -exec cp -f {} "${OUT_DIR}/receipts_gpu.json" \; 2>/dev/null || true

if [ ! -s "${OUT_DIR}/words.json" ]; then
  echo "::error::kernel ${REF} produced no words.json (status: ${STATUS})"
  # Surface the kernel's own failure text, not just the status string: Kaggle
  # stores the log as a JSON array of stream items.
  python3 - "${KDIR}" <<'KLOG'
import glob, json, sys
kdir = sys.argv[1]
blob = ""
for p in glob.glob(f"{kdir}/out/*.log"):
    try:
        items = json.loads(open(p, errors="ignore").read())
        blob += "".join(str(i.get("data", "")) for i in items if isinstance(i, dict))
    except Exception:
        blob += open(p, errors="ignore").read()
lines = [l for l in blob.splitlines()
         if l.strip() and "NbConvertApp" not in l and "SyntaxWarning" not in l]
print("\n".join(lines[-60:]))
KLOG
  exit 1
fi

echo "::notice::GPU receipt"
python3 - <<'PY'
import json, pathlib
r = json.loads(pathlib.Path("public/demo/gpu/receipts_gpu.json").read_text())
w = json.loads(pathlib.Path("public/demo/gpu/words.json").read_text())
print(json.dumps({k: r.get(k) for k in ("gpu_count", "devices", "nvidia_smi", "model",
                                        "words", "mean_word_prob", "wall_s", "audio_total_s")}, indent=1))
print("beats:", [(b["file"], b["duration"], len(b["words"])) for b in w["beats"]])
PY
