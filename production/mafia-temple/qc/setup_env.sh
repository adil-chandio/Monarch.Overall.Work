#!/usr/bin/env bash
# Reproducible local toolchain for the Monarch night-temple V8 build.
#
# Why this exists: the free CPU sandbox is rebuilt between turns, so a one-off
# `pip install` disappears. This script recreates exactly what the render needs,
# from public sources only, and never downloads user media.
#
#   bash production/mafia-temple/qc/setup_env.sh
#   source production/mafia-temple/qc/.env
#
# The super-resolution model is ESPCN x2 (a small learned network). It is
# fetched from the public EDSR_Tensorflow repository export folder, pinned by the
# repository's own filename convention; verify the licence before commercial use.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${VENV:-/home/user/.venv}"
MODELS="$HERE/models"

echo "== python venv at $VENV"
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
fi

echo "== packages"
"$VENV/bin/pip" install -q --upgrade pip >/dev/null
"$VENV/bin/pip" install -q \
  "numpy>=1.26,<3" "pillow>=10" imageio-ffmpeg \
  "opencv-contrib-python-headless==4.10.0.84"

echo "== ESPCN x2 model"
mkdir -p "$MODELS"
if [ ! -s "$MODELS/ESPCN_x2.pb" ]; then
  tmp="$(mktemp -d)"
  # public mirror that ships the ESPCN .pb alongside the EDSR models
  if curl -fsSL "https://codeload.github.com/fannymonori/TF-ESPCN/tar.gz/refs/heads/master" \
      -o "$tmp/espcn.tar.gz"; then
    tar xzf "$tmp/espcn.tar.gz" -C "$tmp"
    found="$(find "$tmp" -name 'ESPCN_x2.pb' -print -quit || true)"
    [ -n "$found" ] && cp "$found" "$MODELS/ESPCN_x2.pb"
  fi
  rm -rf "$tmp"
fi
if [ ! -s "$MODELS/ESPCN_x2.pb" ]; then
  echo "   ESPCN model unavailable; the render will fall back to bicubic (logged, not hidden)"
fi

cat > "$HERE/.env" <<EOF
export VENV="$VENV"
export PY="$VENV/bin/python"
export FF="$("$VENV/bin/python" -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
export ESPCN="$MODELS/ESPCN_x2.pb"
EOF

echo "== done"
"$VENV/bin/python" - <<'PY'
import cv2, numpy, imageio_ffmpeg
print('   cv2', cv2.__version__, '| numpy', numpy.__version__,
      '| ffmpeg', imageio_ffmpeg.get_ffmpeg_exe().split('/')[-1])
PY
echo "   now run:  source $HERE/.env"
