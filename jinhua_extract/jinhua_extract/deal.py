"""Assign 12 dealt cards to 4 players (3 each)."""

from __future__ import annotations

from dataclasses import dataclass

from jinhua_extract.cards import Card
from jinhua_extract.rules import EvaluatedHand, evaluate_hand, winner_indices


@dataclass(frozen=True)
class PlayerHand:
    player: int  # 1..4
    cards: tuple[Card, Card, Card]
    evaluated: EvaluatedHand


def assign_players(
    cards: list[Card],
    *,
    players: int = 4,
    cards_each: int = 3,
    deal: str = "round_robin",
) -> list[PlayerHand]:
    expected = players * cards_each
    if len(cards) != expected:
        raise ValueError(f"需要恰好 {expected} 张牌，实际 {len(cards)}")

    grouped: list[list[Card]] = [[] for _ in range(players)]
    if deal == "round_robin":
        for i, card in enumerate(cards):
            grouped[i % players].append(card)
    elif deal == "stacked":
        for p in range(players):
            start = p * cards_each
            grouped[p] = list(cards[start : start + cards_each])
    else:
        raise ValueError("deal 必须是 round_robin 或 stacked")

    hands: list[PlayerHand] = []
    for p, group in enumerate(grouped, start=1):
        if len(group) != cards_each:
            raise ValueError(f"玩家 {p} 不是 {cards_each} 张")
        ev = evaluate_hand(group)
        hands.append(PlayerHand(player=p, cards=tuple(group), evaluated=ev))
    return hands


def summarize(hands: list[PlayerHand]) -> dict:
    winners = winner_indices([h.evaluated for h in hands])
    return {
        "players": [
            {
                "player": h.player,
                "cards": [c.code for c in h.cards],
                "cards_zh": [c.zh() for c in h.cards],
                "hand": h.evaluated.name,
            }
            for h in hands
        ],
        "winners": [hands[i].player for i in winners],
    }
