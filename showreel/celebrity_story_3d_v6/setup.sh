#!/usr/bin/env bash
# Rebuild the render environment from pinned, checksummed sources.
set -e
cd /home/user
python3 -m venv .venv-production
./.venv-production/bin/pip install -q bpy==4.2.23 pillow imageio-ffmpeg numpy
mkdir -p .runtime-libs
gh api repos/adil-chandio/Monarch.Overall.Work/git/blobs/aba6d52258ba4ca90d033258dc326ee80e6f71b7 \
  -H "Accept: application/vnd.github.raw" > /tmp/runtime.tar.gz
echo "e749b6937716aa4bd1141d0cf4cab1feab37df7037faab269818bd015cd47904  /tmp/runtime.tar.gz" | sha256sum -c -
tar -xzf /tmp/runtime.tar.gz -C .runtime-libs
cd Monarch.Overall.Work
python3 showreel/celebrity_lookdev/fetch_assets.py /home/user/celebrity-lookdev-assets
python3 showreel/celebrity_story_3d_v6/fetch_extra.py
LD_LIBRARY_PATH=/home/user/.runtime-libs /home/user/.venv-production/bin/python -c "import bpy;print('bpy',bpy.app.version_string)"
