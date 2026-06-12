#!/usr/bin/env python3
"""
The Night Library server — static files + a same-origin illustrator proxy.

Why a proxy: the browser page (this origin) cannot call the Bonsai image
studio on :8800 directly — its FastAPI backend sends no CORS headers, so the
preflight dies in the browser. Server-to-server HTTP has no such rule. The
page therefore POSTs to /illustrate here, and this process forwards to the
studio's /generate and streams the PNG straight back. One origin, zero CORS,
nothing to configure.

Stdlib only. No dependencies, no build step — same covenant as the web app.

Usage:
    python3 scripts/serve.py            # http://127.0.0.1:8400/web/
Env:
    PORT        library port   (default 8400)
    STUDIO_URL  image studio   (default http://127.0.0.1:8800)
"""
import json
import os
import pathlib
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[1]
PORT = int(os.environ.get("PORT", "8400"))
STUDIO_URL = os.environ.get("STUDIO_URL", "http://127.0.0.1:8800").rstrip("/")
GENERATE_TIMEOUT_S = 120  # cold first render compiles kernels; warm is ~6s


class LibraryHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if self.path != "/illustrate":
            self.send_error(404, "POST is only for /illustrate")
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            # Validate it's JSON before forwarding; the studio 422s cryptically.
            json.loads(body)
        except ValueError:
            self.send_error(400, "request body must be JSON")
            return
        req = urllib.request.Request(
            STUDIO_URL + "/generate", data=body,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=GENERATE_TIMEOUT_S) as r:
                png = r.read()
        except urllib.error.HTTPError as e:
            self.send_error(e.code, f"image studio: {e.reason}")
            return
        except (urllib.error.URLError, TimeoutError):
            # Studio not running / not ready: the page falls back to the
            # dream canvas. 503 = "try again later", which is the truth.
            self.send_error(503, "image studio unreachable on " + STUDIO_URL)
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(png)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(png)

    def log_message(self, fmt, *args):  # quieter logs; errors still surface
        if "/illustrate" in (args[0] if args else ""):
            super().log_message(fmt, *args)


def main() -> None:
    print(f"The Night Library  →  http://127.0.0.1:{PORT}/web/")
    print(f"  writer:       llama-server on :8080 (required)")
    print(f"  illustrator:  {STUDIO_URL} (optional — dream canvas otherwise)")
    ThreadingHTTPServer(("127.0.0.1", PORT), LibraryHandler).serve_forever()


if __name__ == "__main__":
    main()
