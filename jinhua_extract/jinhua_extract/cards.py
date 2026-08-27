"""Parse YOLO labels into rank and suit."""

from __future__ import annotations

from dataclasses import dataclass

RANK_ORDER = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANK_ORDER)}  # 2..14

SUIT_ALIASES = {
    "S": "s",
    "SPADES": "s",
    "SPADE": "s",
    "H": "h",
    "HEARTS": "h",
    "HEART": "h",
    "C": "c",
    "CLUBS": "c",
    "CLUB": "c",
    "D": "d",
    "DIAMONDS": "d",
    "DIAMOND": "d",
}
SUIT_VALUE = {"s": 4, "h": 3, "c": 2, "d": 1}  # 黑桃 > 红桃 > 梅花 > 方块
SUIT_ZH = {"s": "黑桃", "h": "红桃", "c": "梅花", "d": "方块"}


@dataclass(frozen=True, order=True)
class Card:
    rank: str
    suit: str  # s/h/c/d

    @property
    def code(self) -> str:
        return f"{self.rank}{self.suit}"

    @property
    def rank_value(self) -> int:
        return RANK_VALUE[self.rank]

    @property
    def suit_value(self) -> int:
        return SUIT_VALUE[self.suit]

    def zh(self) -> str:
        return f"{SUIT_ZH[self.suit]}{self.rank}"


def parse_label(label: str) -> Card:
    """Accept Ah, AH, aH, 10s, 10S, TSish not; also 10_of_spades-like compact."""
    raw = label.strip().replace(" ", "").replace("_", "").replace("-", "")
    raw = raw.upper()
    if raw.startswith("10"):
        rank, rest = "10", raw[2:]
    elif raw[:1] in "A23456789JQK":
        rank, rest = raw[:1], raw[1:]
        if rank == "1":
            raise ValueError(f"unrecognized card label: {label!r}")
    else:
        raise ValueError(f"unrecognized card label: {label!r}")

    suit_token = rest
    if suit_token in SUIT_ALIASES:
        suit = SUIT_ALIASES[suit_token]
    else:
        raise ValueError(f"unrecognized card label: {label!r}")
    if rank not in RANK_VALUE:
        raise ValueError(f"unrecognized rank in label: {label!r}")
    return Card(rank=rank, suit=suit)
