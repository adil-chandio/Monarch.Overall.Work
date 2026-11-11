#!/usr/bin/env bash
# One command: rebuild the whole V8 cut from the source clips, with its logs.
#
#   bash production/mafia-temple/qc/build_v8.sh
#
# Steps: measure the sources -> master the sound -> render the picture ->
# prove the deltas -> write the QC summary. Any failure stops the build and is
# printed; nothing is silently skipped. Media stays in untracked local paths.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT"

if [ -f "$HERE/.env" ]; then
  # shellcheck disable=SC1091
  source "$HERE/.env"
else
  echo "!! run qc/setup_env.sh first (creates the venv and fetches ESPCN)"; exit 1
fi

OUT="$ROOT/qc/out/v8"
mkdir -p "$OUT"

echo "== 1/5 measure every source clip"
"$PY" qc/measure_shots.py --clips clips --output qc/clip_metrics.json

echo "== 2/5 master the sound"
"$PY" qc/make_sound_v8.py --source monarch-mafia-temple-20s.mp4 \
      --out "$OUT/sound_v8.wav" --log "$OUT/sound_log.json"

echo "== 3/5 render the picture"
SR_ARGS=()
[ -s "${ESPCN:-}" ] && SR_ARGS=(--superres "$ESPCN")
"$PY" qc/render_film_v8.py --out "$OUT/monarch-temple-v8.mp4" \
      --audio "$OUT/sound_v8.wav" --log "$OUT/render_log.json" "${SR_ARGS[@]}"

echo "== 4/5 prove the deltas"
"$PY" qc/compare_cuts.py --a monarch-temple-native-review.mp4 \
      --b "$OUT/monarch-temple-v8.mp4" --json "$OUT/compare.json"

echo "== 5/5 tests"
"$PY" -m unittest qc/test_film_tools.py

echo
echo "done. Deliverables (untracked, private):"
ls -la "$OUT/monarch-temple-v8.mp4" "$OUT/sound_v8.wav"
echo "logs:          $OUT/render_log.json  $OUT/sound_log.json  $OUT/compare.json"
echo "reminder: QC numbers are engineering measurements, not creative acceptance."
