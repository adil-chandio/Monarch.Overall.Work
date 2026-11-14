#!/usr/bin/env bash
# Render the film in chunks and encode as we go.
#
# A full 1800-frame render at 720p is ~2 GB of PNGs and the sandbox has 1.3 GB.
# This renders 150 frames, encodes them, deletes them, and moves on, so peak disk
# is ~170 MB regardless of film length. It also means a crash costs one chunk, not
# the whole render — v1 lost 157 frames to a single IndexError.
set -euo pipefail
cd /home/user/Monarch.Overall.Work

FF=/tmp/venv-ff/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2
PY=.venv/bin/python
OUT=${OUT:-/tmp/v2}
CHUNK=${CHUNK:-150}
TOTAL=${TOTAL:-1800}
mkdir -p "$OUT/parts"

start=${START:-0}
idx=0
while [ "$start" -lt "$TOTAL" ]; do
  end=$((start + CHUNK))
  [ "$end" -gt "$TOTAL" ] && end=$TOTAL
  a=$(python3 -c "print(f'{$start/30:.4f}')")
  b=$(python3 -c "print(f'{$end/30:.4f}')")
  if [ -f "$OUT/parts/p$(printf '%03d' "$idx").mp4" ]; then
    echo "[chunk $idx] already encoded, skipping"
    start=$end; idx=$((idx + 1)); continue
  fi
  dir="$OUT/frames"
  rm -rf "$dir"; mkdir -p "$dir"
  echo "[chunk $idx] frames $start-$end  (${a}s-${b}s)"
  "$PY" scripts/orca3d-film.py --out "$dir" --from "$a" --to "$b" >/dev/null

  n=$(ls "$dir" | wc -l)
  expect=$((end - start))
  if [ "$n" -ne "$expect" ]; then
    echo "  MISSING FRAMES: got $n, expected $expect" >&2
    # find the gap and re-render the individual missing stills
    missing=$(python3 - "$dir" "$start" "$end" <<'EOF'
import os, sys
d, s, e = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
have = {int(f[2:7]) for f in os.listdir(d) if f.startswith("f_")}
print(" ".join(str(i) for i in range(s, e) if i not in have))
EOF
)
    for m in $missing; do
      t=$(python3 -c "print(f'{$m/30:.4f}')")
      "$PY" scripts/orca3d-film.py --still "$t" --out "$OUT/repair" >/dev/null
      cp "$OUT/repair/still-"*.png "$dir/$(printf 'f_%05d.png' "$m")"
    done
  fi

  # orca3d-film.py names frames by absolute index (f_00150...), but the image2
  # demuxer always starts a sequence at 0, so every chunk after the first encoded
  # nothing and ffmpeg exited 254. Renumber to a 0-based sequence for the encode.
  tmp="$OUT/enc"; rm -rf "$tmp"; mkdir -p "$tmp"
  n=0
  for f in $(ls "$dir" | sort); do
    ln -s "$dir/$f" "$tmp/$(printf 'f_%05d.png' "$n")"
    n=$((n + 1))
  done
  "$FF" -y -hide_banner -loglevel error -framerate 30 -i "$tmp/f_%05d.png" \
    -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -r 30 \
    -movflags +faststart "$OUT/parts/p$(printf '%03d' "$idx").mp4"
  echo "  -> $(du -h "$OUT/parts/p$(printf '%03d' "$idx").mp4" | cut -f1)"
  rm -rf "$dir" "$tmp" "$OUT/repair"
  start=$end; idx=$((idx + 1))
done

echo "concat..."
: > "$OUT/list.txt"
for f in $(ls "$OUT"/parts/*.mp4 | sort); do echo "file '$f'" >> "$OUT/list.txt"; done
"$FF" -y -hide_banner -loglevel error -f concat -safe 0 -i "$OUT/list.txt" -c copy "$OUT/video.mp4"
echo "video: $(du -h "$OUT/video.mp4" | cut -f1)"
"$FF" -hide_banner -i "$OUT/video.mp4" 2>&1 | grep -E "Duration|Stream"
