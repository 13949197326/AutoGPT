from jinhua_extract.extract import extract_from_detections
from jinhua_extract.timeline import Detection, detections_to_cards


def _repeat(label: str, start: int, n: int = 5, conf: float = 0.8):
    return [Detection(frame=start + i, label=label, conf=conf) for i in range(n)]


def test_timeline_orders_by_first_seen():
    dets: list[Detection] = []
    labels = [
        "Ah", "Kh", "Qh", "Jh",
        "Ad", "Kd", "Qd", "Jd",
        "Ac", "Kc", "Qc", "Jc",
    ]
    for i, lab in enumerate(labels):
        dets.extend(_repeat(lab, start=i * 10))
    events = detections_to_cards(dets, num_cards=12, min_votes=3)
    assert [e.card.code for e in events] == [_norm(x) for x in labels]


def _norm(label: str) -> str:
    from jinhua_extract.cards import parse_label

    return parse_label(label).code


def test_extract_full_table():
    labels = [
        "Ah", "Kh", "Qh", "Jh",
        "Ad", "Kd", "Qd", "Jd",
        "Ac", "Kc", "Qc", "Jc",
    ]
    dets: list[Detection] = []
    for i, lab in enumerate(labels):
        dets.extend(_repeat(lab, start=i * 8))
    result = extract_from_detections(dets)
    assert result.complete
    assert result.table["winners"] == [1]
    assert result.table["players"][0]["hand"] == "豹子"


def test_incomplete_when_missing_cards():
    dets = _repeat("Ah", 0) + _repeat("Kd", 10)
    result = extract_from_detections(dets, min_votes=3)
    assert not result.complete
    assert result.found == 2
