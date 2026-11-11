#!/usr/bin/env python3
"""Tiny file server for handing out the review reel.

Usage (from the repo root):
    .venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/serve_review_reel.py 8123


`python -m http.server` answers a Range request with the whole 95 MB body and a 200,
which breaks seeking in the browser player. This one does it properly: 206 Partial
Content, correct Content-Range, and a HEAD that reports the real length.

One file, no dependencies, no directory listing.
"""
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# The reel lives in .cache (never committed). Resolve it from the repo root so this
# script can live in the repository and still serve the build output.
# production/extinct-life/longform-mammoth/cinematic-rebuild/edit -> repo root is five
# levels up. Counted, not guessed: the earlier version was one level short and silently
# pointed at a directory that does not exist.
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(_HERE, *[os.pardir] * 5))
assert os.path.isdir(os.path.join(REPO, "production", "extinct-life")), (
    "cannot find the repository root from %s; run this from a checkout" % _HERE)
ROOT = os.path.join(REPO, ".cache", "mammoth-edit")
CHUNK = 256 * 1024

# Only these may be served. No traversal, no listing.
ALLOWED = {
    "review-reel-continuous.mp4": "video/mp4",
}


class Handler(BaseHTTPRequestHandler):
    server_version = "mammoth-download"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    def _path(self):
        return self.path.split("?", 1)[0].lstrip("/")

    def _inline(self):
        # ?inline=1 plays in the browser; without it the response is an attachment,
        # which is what a "download link" should do.
        return "inline=1" in self.path

    def _headers_common(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")

    def do_HEAD(self):
        name = self._path()
        if name not in ALLOWED:
            self.send_error(404)
            return
        size = os.path.getsize(os.path.join(ROOT, name))
        self.send_response(200)
        self.send_header("Content-Type", ALLOWED[name])
        self.send_header("Content-Length", str(size))
        self.send_header("Content-Disposition", self._disposition(name))
        self._headers_common()
        self.end_headers()

    def _disposition(self, name):
        kind = "inline" if self._inline() else "attachment"
        return '%s; filename="%s"' % (kind, name)

    def do_GET(self):
        name = self._path()
        if name not in ALLOWED:
            self.send_error(404)
            return
        path = os.path.join(ROOT, name)
        size = os.path.getsize(path)

        start, end = 0, size - 1
        partial = False
        rng = self.headers.get("Range")
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)$", rng.strip())
            if m and (m.group(1) or m.group(2)):
                if m.group(1):
                    start = int(m.group(1))
                    if m.group(2):
                        end = int(m.group(2))
                else:  # suffix range: last N bytes
                    start = max(0, size - int(m.group(2)))
                end = min(end, size - 1)
                if start > end or start >= size:
                    self.send_response(416)
                    self.send_header("Content-Range", "bytes */%d" % size)
                    self.end_headers()
                    return
                partial = True

        length = end - start + 1
        self.send_response(206 if partial else 200)
        self.send_header("Content-Type", ALLOWED[name])
        self.send_header("Content-Length", str(length))
        if partial:
            self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("Content-Disposition", self._disposition(name))
        self._headers_common()
        self.end_headers()

        with open(path, "rb") as f:
            f.seek(start)
            remaining = length
            while remaining > 0:
                chunk = f.read(min(CHUNK, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                remaining -= len(chunk)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8123
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    sys.stderr.write("serving %s on 0.0.0.0:%d\n" % (ROOT, port))
    srv.serve_forever()
