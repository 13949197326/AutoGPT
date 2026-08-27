"""Run YOLO on a dealing video and collect labeled detections."""

from __future__ import annotations

from pathlib import Path

import cv2

from jinhua_extract.timeline import Detection


def pick_device() -> str:
    try:
        import torch

        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
    except Exception:
        pass
    return "cpu"


def iter_detections(
    video_path: str | Path,
    weights: str | Path,
    *,
    conf: float = 0.45,
    frame_stride: int = 1,
    device: str | None = None,
    annotate_path: str | Path | None = None,
) -> list[Detection]:
    from ultralytics import YOLO

    device = device or pick_device()
    model = YOLO(str(weights))
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FileNotFoundError(f"无法打开视频: {video_path}")

    writer = None
    if annotate_path:
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        Path(annotate_path).parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(annotate_path), fourcc, fps / max(frame_stride, 1), (w, h))

    print(f"[detect] device={device} weights={weights}", flush=True)
    print(f"[detect] classes={list(model.names.values())[:8]}... total={len(model.names)}", flush=True)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    print(f"[detect] video={video_path} frames={total} stride={frame_stride}", flush=True)

    detections: list[Detection] = []
    frame_idx = 0
    infer_frames = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_idx % frame_stride != 0:
            frame_idx += 1
            continue
        results = model.predict(frame, conf=conf, device=device, verbose=False)
        infer_frames += 1
        if infer_frames == 1 or infer_frames % 20 == 0:
            nbox = 0 if results[0].boxes is None else len(results[0].boxes)
            print(f"[detect] inferred {infer_frames} frames, last_boxes={nbox}", flush=True)
        result = results[0]
        names = result.names
        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                score = float(box.conf[0])
                label = names[cls_id] if isinstance(names, dict) else names[cls_id]
                detections.append(Detection(frame=frame_idx, label=str(label), conf=score))
        if writer is not None:
            plotted = result.plot()
            writer.write(plotted)
        frame_idx += 1

    cap.release()
    if writer is not None:
        writer.release()
    print(f"[detect] done frames={frame_idx} detections={len(detections)}", flush=True)
    return detections
