#!/usr/bin/env python3
"""Local preview of the satellite portfolio update and shared demo media."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import sys

PUBLIC = Path(__file__).resolve().parents[1] / 'public'


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self._range = None
        super().__init__(*args, directory=str(PUBLIC), **kwargs)

    def _redirect_root(self):
        if self.path.split('?', 1)[0] != '/':
            return False
        self.send_response(302)
        self.send_header('Location', '/portfolio/')
        self.end_headers()
        return True

    def do_GET(self):
        if not self._redirect_root():
            super().do_GET()

    def do_HEAD(self):
        if not self._redirect_root():
            super().do_HEAD()

    def send_head(self):
        # Browsers can seek through the MP4s without downloading entire films.
        value = self.headers.get('Range')
        path = Path(self.translate_path(self.path))
        if not value or not path.is_file():
            return super().send_head()
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', value.strip())
        if not match or not (match[1] or match[2]):
            return super().send_head()
        size = path.stat().st_size
        if match[1]:
            start = int(match[1])
            end = min(int(match[2]) if match[2] else size - 1, size - 1)
        else:
            start = max(0, size - int(match[2]))
            end = size - 1
        if start >= size or start > end:
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.end_headers()
            return None
        file = path.open('rb')
        self._range = (start, end)
        self.send_response(206)
        self.send_header('Content-type', self.guess_type(str(path)))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.end_headers()
        file.seek(start)
        return file

    def copyfile(self, source, outputfile):
        if self._range is None:
            return super().copyfile(source, outputfile)
        remaining = self._range[1] - self._range[0] + 1
        while remaining:
            buf = source.read(min(128 * 1024, remaining))
            if not buf:
                break
            outputfile.write(buf)
            remaining -= len(buf)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4176
    print(f'Portfolio preview at http://0.0.0.0:{port}/portfolio/', flush=True)
    ThreadingHTTPServer(('0.0.0.0', port), Handler).serve_forever()
