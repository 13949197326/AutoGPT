from jinhua_extract.cards import parse_label
from jinhua_extract.deal import assign_players, summarize
from jinhua_extract.rules import HandType, evaluate_hand, winner_indices


def C(code: str):
    return parse_label(code)


def test_parse_labels():
    assert C("Ah").code == "Ah"
    assert C("10S").code == "10s"
    assert C("kd").rank == "K"


def test_triple_beats_straight_flush():
    triple = evaluate_hand([C("2s"), C("2h"), C("2d")])
    sf = evaluate_hand([C("As"), C("Ks"), C("Qs")])
    assert triple.hand_type == HandType.TRIPLE
    assert sf.hand_type == HandType.STRAIGHT_FLUSH
    assert triple.key > sf.key


def test_a23_is_smallest_straight():
    a23 = evaluate_hand([C("Ah"), C("2c"), C("3d")])
    qka = evaluate_hand([C("Qh"), C("Kc"), C("Ad")])
    two34 = evaluate_hand([C("2h"), C("3c"), C("4d")])
    assert a23.hand_type == HandType.STRAIGHT
    assert qka.hand_type == HandType.STRAIGHT
    assert qka.key > two34.key > a23.key


def test_ka2_is_not_straight():
    hand = evaluate_hand([C("Kh"), C("Ac"), C("2d")])
    assert hand.hand_type == HandType.HIGH


def test_suit_tiebreak_spades_over_hearts():
    a = evaluate_hand([C("As"), C("7s"), C("3s")])
    b = evaluate_hand([C("Ah"), C("7h"), C("3h")])
    assert a.hand_type == b.hand_type == HandType.FLUSH
    assert winner_indices([a, b]) == [0]


def test_round_robin_four_players():
    # deal order: p1,p2,p3,p4,p1,...
    codes = [
        "Ah", "Kh", "Qh", "Jh",
        "Ad", "Kd", "Qd", "Jd",
        "Ac", "Kc", "Qc", "Jc",
    ]
    cards = [C(x) for x in codes]
    hands = assign_players(cards, deal="round_robin")
    assert [c.code for c in hands[0].cards] == ["Ah", "Ad", "Ac"]
    assert hands[0].evaluated.hand_type == HandType.TRIPLE
    summary = summarize(hands)
    assert summary["winners"] == [1]


def test_stacked_deal():
    codes = [
        "2s", "2h", "2d",
        "As", "Ks", "Qs",
        "Ah", "Kh", "Qh",
        "3c", "5d", "7s",
    ]
    hands = assign_players([C(x) for x in codes], deal="stacked")
    assert hands[0].evaluated.hand_type == HandType.TRIPLE
    assert summarize(hands)["winners"] == [1]
