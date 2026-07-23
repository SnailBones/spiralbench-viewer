#!/usr/bin/env python3
"""Benchmark viewer server — thin router over per-benchmark modules.

Each benchmark lives in its own module (syco.py, spiral.py) exposing:
  load()              -> in-memory state, built once at startup
  handle(state, path) -> (json_payload, cacheable) or None for unknown paths

Routes are namespaced /api/<benchmark>/...; the frontends live in static/.
Whichever benchmark modules are present get mounted, so a repo can ship any
subset of them with this file unchanged.

Usage: python3 server.py [port]   (default 8501)
Data locations can be overridden per module (SYCO_DATA_DIR, SPIRAL_DATA_DIR).
"""
import importlib
import json
import re
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent

BENCHMARKS = {}
for name in ("syco", "spiral"):
    try:
        BENCHMARKS[name] = importlib.import_module(name)
    except ImportError:
        pass


class Handler(SimpleHTTPRequestHandler):
    states = {}
    response_cache = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "static"), **kwargs)

    def do_GET(self):
        m = re.match(r"^/api/(\w+)(/.*)$", self.path)
        if not m:
            return super().do_GET()
        name, sub_path = m.groups()
        module = BENCHMARKS.get(name)
        if module is None:
            return self.send_error(404, "unknown benchmark")
        cached = self.response_cache.get(self.path)
        if cached is not None:
            return self.send_json_bytes(cached)
        result = module.handle(self.states[name], sub_path)
        if result is None:
            return self.send_error(404, "unknown API path")
        payload, cacheable = result
        body = json.dumps(payload).encode("utf-8")
        if cacheable:
            self.response_cache[self.path] = body
        self.send_json_bytes(body)

    def send_json_bytes(self, body):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8501
    print("Loading benchmarks ...")
    for name, module in BENCHMARKS.items():
        Handler.states[name] = module.load()
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"Serving on http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
