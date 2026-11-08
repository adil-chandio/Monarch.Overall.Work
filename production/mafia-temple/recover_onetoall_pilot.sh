#!/usr/bin/env bash
# Recover the already-completed private Kaggle job; never starts another run.
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
ref="$KAGGLE_USERNAME/monarch-onetoall-run-42511685428"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
out=production/mafia-temple/onetoall-pilot-output
mkdir -p "$out"
kaggle kernels output "$ref" -p "$tmp" --file-pattern '(^|/)(onetoall-running-pilot\.mp4|onetoall-receipt\.json|pose-audit\.json|pose-audit\.jpg|warped-ref-audit\.jpg|output-metadata\.json)$'
for f in onetoall-running-pilot.mp4 onetoall-receipt.json pose-audit.json pose-audit.jpg warped-ref-audit.jpg output-metadata.json; do
  found=$(find "$tmp" -type f -name "$f" -print -quit)
  if [ -z "$found" ]; then echo "Missing fresh result $f"; exit 1; fi
  test -s "$found"
  cp "$found" "$out/$f"
done
python - <<'PY'
import json
p='production/mafia-temple/onetoall-pilot-output/onetoall-receipt.json'
r=json.load(open(p))
assert r['status']=='complete_research_only' and r['original_photo_used'] is False
assert r['output']['frames']==49
print('Recovered completed research output; original photo was not used')
PY
