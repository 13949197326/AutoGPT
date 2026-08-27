#!/usr/bin/env python3
"""Sample a dealing video and print YOLO boxes. Run from ~/jinhua_extract."""

from collections import Counter
from pathlib import Path

import cv2
from ultralytics import YOLO


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    video = Path.home() / "Desktop" / "deal.mp4"
    weights = root / "models" / "playing-cards.pt"
    print("video", video, "exists", video.exists())
    print("weights", weights, "exists", weights.exists())
    model = YOLO(str(weights))
    print("n_classes", len(model.names))
    print("names", model.names)
    cap = cv2.VideoCapture(str(video))
    print("opened", cap.isOpened(), "frames", int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0))
    counts: Counter[str] = Counter()
    n = 0
    sampled = 0
    while sampled < 40:
        ok, frame = cap.read()
        if not ok:
            break
        n += 1
        if n % 10 != 1:
            continue
        result = model.predict(frame, conf=0.15, verbose=False)[0]
        nbox = 0 if result.boxes is None else len(result.boxes)
        sampled += 1
        print(f"frame={n} boxes={nbox}")
        if result.boxes is not None:
            for box in result.boxes:
                name = result.names[int(box.cls[0])]
                counts[name] += 1
    print("label_counts", counts)
    cap.release()


if __name__ == "__main__":
    main()
