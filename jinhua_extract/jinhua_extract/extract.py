from __future__ import annotations

from dataclasses import dataclass

from jinhua_extract.deal import assign_players, summarize
from jinhua_extract.timeline import CardEvent, Detection, detections_to_cards


@dataclass
class ExtractResult:
    found: int
    expected: int
    deal_order: list[str]
    events: list[CardEvent]
    table: dict | None
    complete: bool

    def to_json(self) -> dict:
        payload = {
            "found": self.found,
            "expected": self.expected,
            "complete": self.complete,
            "deal_order": self.deal_order,
            "events": [
                {
                    "code": e.card.code,
                    "zh": e.card.zh(),
                    "first_frame": e.first_frame,
                    "votes": e.votes,
                    "best_conf": e.best_conf,
                }
                for e in self.events
            ],
            "table": self.table,
        }
        return payload


def extract_from_detections(
    detections: list[Detection],
    *,
    num_cards: int = 12,
    players: int = 4,
    cards_each: int = 3,
    deal: str = "round_robin",
    min_conf: float = 0.45,
    min_votes: int = 3,
) -> ExtractResult:
    expected = players * cards_each
    if num_cards != expected:
        raise ValueError(f"num_cards 应为 {expected}（{players} 人 × {cards_each} 张）")

    events = detections_to_cards(
        detections,
        num_cards=num_cards,
        min_conf=min_conf,
        min_votes=min_votes,
    )
    cards = [e.card for e in events]
    table = None
    complete = len(cards) == expected
    if complete:
        hands = assign_players(cards, players=players, cards_each=cards_each, deal=deal)
        table = summarize(hands)
    return ExtractResult(
        found=len(cards),
        expected=expected,
        deal_order=[c.code for c in cards],
        events=events,
        table=table,
        complete=complete,
    )
