"""Find ffmpeg and ffprobe wherever they actually are.

The sandbox that authors this work has no apt and neither binary on PATH; it only has
the static ffmpeg that imageio bundles, and no ffprobe at all. A GitHub runner has the
opposite: both are on PATH and imageio is not installed. Hard-coding either one is how
two CI runs died on a missing file, and how a third died reporting "ffmpeg encode
failed" with the reason on a stderr nobody could download.

So every tool asks here instead, and asks for the binary it needs by name.
"""
import os
import shutil
from pathlib import Path

_BUNDLED = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries"


def _candidates(name: str):
    env = os.environ.get(name.upper())
    yield env
    yield name
    for version in ("v9.0.2", "v9.0.1", "v7.0.2"):
        yield f"{_BUNDLED}/{name}-linux-x86_64-{version}"


def find(name: str) -> str:
    """Absolute path to `name`, or a SystemExit that says what was tried."""
    tried = []
    for c in _candidates(name):
        if not c:
            continue
        tried.append(c)
        found = shutil.which(c) if os.sep not in c else (c if Path(c).is_file() and os.access(c, os.X_OK) else None)
        if found:
            return found
    # anything imageio has ever installed under that name
    for base in ("/usr/local/lib", str(Path.home() / ".local/lib")):
        for p in Path(base).rglob(f"{name}-linux-*"):
            if p.is_file() and os.access(p, os.X_OK):
                return str(p)
    if name == "ffmpeg":
        try:  # imageio's own resolver, if the package is present
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
    raise SystemExit(f"{name} not found — set {name.upper()} or install it on PATH. Tried: {', '.join(tried)}")


def ffmpeg() -> str:
    return find("ffmpeg")


def ffprobe() -> str:
    return find("ffprobe")
