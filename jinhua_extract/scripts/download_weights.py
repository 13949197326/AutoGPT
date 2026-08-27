#!/usr/bin/env python3
"""Download public YOLO weights. No Ultralytics account or API key is required."""

from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"

# COCO base (for your own fine-tune). Ultralytics GitHub release assets.
YOLOV8N = (
    "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt",
    "yolov8n.pt",
)

# 52-class playing-card detector (YOLOv8l, ~88MB). Public Hugging Face file, MIT.
CARDS = (
    "https://huggingface.co/koolguy06/playing-cards/resolve/main/playing-cards.pt",
    "playing-cards.pt",
)


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1_000_000:
        print(f"already exists: {dest} ({dest.stat().st_size} bytes)")
        return
    print(f"downloading {url}\n  -> {dest}")
    urllib.request.urlretrieve(url, dest)
    print(f"saved {dest.stat().st_size} bytes")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--which",
        choices=("cards", "yolov8n", "both"),
        default="cards",
        help="cards = ready-made poker detector; yolov8n = base for fine-tune",
    )
    args = parser.parse_args()
    jobs = []
    if args.which in ("cards", "both"):
        jobs.append(CARDS)
    if args.which in ("yolov8n", "both"):
        jobs.append(YOLOV8N)
    for url, name in jobs:
        download(url, MODELS / name)
    print("done. Use --weights models/playing-cards.pt for a first video test.")


if __name__ == "__main__":
    main()
