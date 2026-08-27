"""Turn per-frame detections into an ordered unique-card sequence.

Assumes one deck: each rank+suit appears at most once among the 12 dealt cards.
A card is kept if it is seen often/confidently enough; order is first reliable frame.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from jinhua_extract.cards import Card, parse_label


@dataclass
class Detection:
    frame: int
    label: str
    conf: float


@dataclass
class CardEvent:
    card: Card
    first_frame: int
    votes: int
    best_conf: float
    labels: dict[str, float] = field(default_factory=dict)


def detections_to_cards(
    detections: list[Detection],
    *,
    num_cards: int = 12,
    min_conf: float = 0.45,
    min_votes: int = 3,
) -> list[CardEvent]:
    by_label: dict[str, list[Detection]] = defaultdict(list)
    for det in detections:
        if det.conf < min_conf:
            continue
        try:
            parse_label(det.label)
        except ValueError:
            continue
        by_label[det.label.upper()].append(det)

    events: list[CardEvent] = []
    for label, items in by_label.items():
        if len(items) < min_votes:
            continue
        best = max(d.conf for d in items)
        first = min(d.frame for d in items)
        events.append(
            CardEvent(
                card=parse_label(label),
                first_frame=first,
                votes=len(items),
                best_conf=best,
            )
        )

    # One physical card might flicker between two labels; keep stronger label
    # if two events share nothing else — uniqueness by card.code already.
    events.sort(key=lambda e: (e.first_frame, -e.best_conf, -e.votes))
    seen: set[str] = set()
    ordered: list[CardEvent] = []
    for ev in events:
        if ev.card.code in seen:
            continue
        seen.add(ev.card.code)
        ordered.append(ev)
        if len(ordered) >= num_cards:
            break
    return ordered
