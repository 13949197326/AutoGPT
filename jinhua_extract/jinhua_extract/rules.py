"""Standard 炸金花 (3-card) ranking."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from jinhua_extract.cards import Card


class HandType(IntEnum):
    HIGH = 1
    PAIR = 2
    STRAIGHT = 3
    FLUSH = 4
    STRAIGHT_FLUSH = 5
    TRIPLE = 6


HAND_ZH = {
    HandType.TRIPLE: "豹子",
    HandType.STRAIGHT_FLUSH: "同花顺",
    HandType.FLUSH: "同花",
    HandType.STRAIGHT: "顺子",
    HandType.PAIR: "对子",
    HandType.HIGH: "散牌",
}


def _straight_high(ranks: list[int]) -> int | None:
    """Return straight high (A23 counts as 3). KA2 is not a straight."""
    uniq = sorted(set(ranks))
    if len(uniq) != 3:
        return None
    if set(uniq) == {14, 2, 3}:
        return 3
    if uniq[2] - uniq[0] == 2 and uniq[1] - uniq[0] == 1:
        return uniq[2]
    return None


@dataclass(frozen=True)
class EvaluatedHand:
    cards: tuple[Card, Card, Card]
    hand_type: HandType
    # Larger tuple wins. Last elements include suit tie-break.
    key: tuple[int, ...]

    @property
    def name(self) -> str:
        return HAND_ZH[self.hand_type]


def evaluate_hand(cards: list[Card]) -> EvaluatedHand:
    if len(cards) != 3:
        raise ValueError("炸金花一手必须是 3 张牌")
    ordered = tuple(sorted(cards, key=lambda c: (-c.rank_value, -c.suit_value)))
    ranks = [c.rank_value for c in ordered]
    suits = [c.suit for c in ordered]
    flush = len(set(suits)) == 1
    sh = _straight_high(ranks)

    counts: dict[int, int] = {}
    for r in ranks:
        counts[r] = counts.get(r, 0) + 1

    suit_key = tuple(c.suit_value for c in ordered)

    if 3 in counts.values():
        triple_rank = next(r for r, n in counts.items() if n == 3)
        key = (int(HandType.TRIPLE), triple_rank) + suit_key
        return EvaluatedHand(ordered, HandType.TRIPLE, key)

    if flush and sh is not None:
        key = (int(HandType.STRAIGHT_FLUSH), sh) + suit_key
        return EvaluatedHand(ordered, HandType.STRAIGHT_FLUSH, key)

    if flush:
        key = (int(HandType.FLUSH), ranks[0], ranks[1], ranks[2]) + suit_key
        return EvaluatedHand(ordered, HandType.FLUSH, key)

    if sh is not None:
        key = (int(HandType.STRAIGHT), sh) + suit_key
        return EvaluatedHand(ordered, HandType.STRAIGHT, key)

    if 2 in counts.values():
        pair_rank = next(r for r, n in counts.items() if n == 2)
        kicker = next(r for r, n in counts.items() if n == 1)
        key = (int(HandType.PAIR), pair_rank, kicker) + suit_key
        return EvaluatedHand(ordered, HandType.PAIR, key)

    key = (int(HandType.HIGH), ranks[0], ranks[1], ranks[2]) + suit_key
    return EvaluatedHand(ordered, HandType.HIGH, key)


def winner_indices(hands: list[EvaluatedHand]) -> list[int]:
    if not hands:
        return []
    best = max(h.key for h in hands)
    return [i for i, h in enumerate(hands) if h.key == best]
