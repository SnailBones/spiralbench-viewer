#!/usr/bin/env python3
"""Bake the SpiralBench viewer data into docs/ for static hosting (GitHub Pages).

Reads a spiral-bench checkout (see SPIRAL_DATA_DIR in spiral.py) and writes:
  docs/data/index.json                      compact index (~6MB)
  docs/data/transcripts/<model>--<id>.json  one file per conversation (~150KB)

docs/index.html fetches these lazily, so no server is needed — serve docs/
with any static host, or locally with:  python3 -m http.server -d docs

Usage: python3 build_static.py
"""
import json
from pathlib import Path

import spiral

DOCS = Path(__file__).resolve().parent / "docs"


def dump(path, payload):
    path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    return path.stat().st_size


def main():
    out_dir = DOCS / "data" / "transcripts"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Reading SpiralBench results from {spiral.RES_DIR} ...")
    index = spiral.load()
    total = dump(DOCS / "data" / "index.json", index)
    n_files = 1
    for path in sorted(spiral.RES_DIR.glob("*.json")):
        model = path.stem
        for sc in index["scenarios"].values():
            if model not in sc["models"]:
                continue
            transcript = spiral.load_transcript(model, sc["id"])
            if transcript is None:
                continue
            total += dump(out_dir / f"{model}--{sc['id']}.json", transcript)
            n_files += 1
    print(f"Wrote {n_files} files, {total / 1e6:.0f} MB total, to {DOCS / 'data'}")


if __name__ == "__main__":
    main()
