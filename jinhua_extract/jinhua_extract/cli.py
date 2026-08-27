from __future__ import annotations

import argparse
import json
from pathlib import Path

from jinhua_extract.detect import iter_detections, pick_device
from jinhua_extract.extract import extract_from_detections


def main() -> None:
    parser = argparse.ArgumentParser(description="从发牌视频提取 4 人炸金花 12 张牌")
    parser.add_argument("--video", required=True, help="发牌视频路径")
    parser.add_argument("--weights", required=True, help="YOLO 扑克检测权重 .pt")
    parser.add_argument("--num-cards", type=int, default=12)
    parser.add_argument("--players", type=int, default=4)
    parser.add_argument("--cards-each", type=int, default=3)
    parser.add_argument("--deal", choices=("round_robin", "stacked"), default="round_robin")
    parser.add_argument("--conf", type=float, default=0.45)
    parser.add_argument("--min-votes", type=int, default=3)
    parser.add_argument("--frame-stride", type=int, default=1)
    parser.add_argument("--device", default=None)
    parser.add_argument("--json", dest="json_path", default=None)
    parser.add_argument("--annotate", default=None, help="可选：画出检测框的视频")
    args = parser.parse_args()

    detections = iter_detections(
        args.video,
        args.weights,
        conf=args.conf,
        frame_stride=args.frame_stride,
        device=args.device or pick_device(),
        annotate_path=args.annotate,
    )
    result = extract_from_detections(
        detections,
        num_cards=args.num_cards,
        players=args.players,
        cards_each=args.cards_each,
        deal=args.deal,
        min_conf=args.conf,
        min_votes=args.min_votes,
    )
    text = json.dumps(result.to_json(), ensure_ascii=False, indent=2)
    print(text)
    if args.json_path:
        out = Path(args.json_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    if not result.complete:
        raise SystemExit(
            f"只稳定识别到 {result.found}/{result.expected} 张。"
            "请检查牌面是否入镜、降低 --conf，或增加自己的牌面微调数据。"
        )


if __name__ == "__main__":
    main()
