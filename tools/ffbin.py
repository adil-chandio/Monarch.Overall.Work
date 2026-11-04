"""Find ffmpeg wherever it actually is.

The sandbox that authors this work has no apt and no ffmpeg on PATH; it only has
the static binary imageio bundles. A GitHub runner has the opposite: ffmpeg is on
PATH and imageio is not installed. Hard-coding either one is how two CI runs died
on a missing file, so every tool asks here instead.
"""
import os
import shutil
from pathlib import Path

_CANDIDATES = [
    os.environ.get("FFMPEG"),
    "ffmpeg",
    "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2",
    "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.1",
]


def ffmpeg() -> str:
    for c in _CANDIDATES:
        if not c:
            continue
        found = shutil.which(c) if os.sep not in c else (c if Path(c).is_file() else None)
        if found:
            return found
    # last resort: anything imageio has ever installed
    for p in Path("/usr/local/lib").rglob("ffmpeg-linux-*"):
        if p.is_file() and os.access(p, os.X_OK):
            return str(p)
    try:  # imageio's own resolver, if the package is present
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    raise SystemExit("ffmpeg not found — set FFMPEG or install it on PATH")
