#!/usr/bin/env python3
"""Serve the committed docs/ folder under /docs/chameleon-flask.

This mirrors the production layout (nginx alias at a subpath) so local preview catches
broken asset paths that a root-mounted preview would hide. Run scripts/build_docs.py first.
"""

from __future__ import annotations

import functools
import http.server
import socketserver
from pathlib import Path

PREFIX = '/docs/chameleon-flask'
PORT = 8099
ROOT = Path(__file__).resolve().parent.parent / 'docs'


class DocsRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        clean = path.split('?', 1)[0].split('#', 1)[0]
        if clean.startswith(PREFIX):
            prefix_len = len(PREFIX)
            path = clean[prefix_len:] or '/'
        return super().translate_path(path)

    def send_head(self):
        if self.path in ('/', PREFIX):
            self.send_response(302)
            self.send_header('Location', PREFIX + '/')
            self.end_headers()
            return None
        return super().send_head()


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def main():
    if not ROOT.is_dir():
        raise SystemExit(f'Run scripts/build_docs.py first; {ROOT} is missing.')

    handler = functools.partial(DocsRequestHandler, directory=str(ROOT))
    with ReusableTCPServer(('127.0.0.1', PORT), handler) as httpd:
        print(f'-> http://127.0.0.1:{PORT}{PREFIX}/  (Ctrl+C to stop)')
        httpd.serve_forever()


if __name__ == '__main__':
    main()
