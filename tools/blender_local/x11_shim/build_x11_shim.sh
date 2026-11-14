#!/usr/bin/env bash
# Build the headless stub libraries and link every missing soname to the generic one.
set -euo pipefail
cd "$(dirname "$0")"
python3 ../gen_shims.py
gcc -shared -fPIC -O2 -o libx11shim.so x11_gl_stubs.c
gcc -shared -fPIC -O2 -Wl,--version-script=libxkbcommon_ver.map -o libxkbcommon.so.0 xkb_stubs.c
for lib in libX11.so.6 libXrender.so.1 libXi.so.6 libXfixes.so.3 libXrandr.so.2 \
           libXinerama.so.1 libXext.so.6 libSM.so.6 libICE.so.6 libXxf86vm.so.1 \
           libGL.so.1 libEGL.so.1 libGLX.so.0 libGLdispatch.so.0; do
  ln -sf libx11shim.so "$lib"
done
echo "built libx11shim.so ($(ls lib*.so* | wc -l) names) + libxkbcommon.so.0"
