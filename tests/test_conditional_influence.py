from gras.typologies import conditional_influence

RUN_TIMESTAMP = "2026-01-01T00:00:00Z"


def test_evaluates_both_directions_for_each_supplier_pair() -> None:
    bids = [
        {"tender_id": "T1", "bidder_id": "A", "awarded_flag": False},
        {"tender_id": "T1", "bidder_id": "B", "awarded_flag": True},
        {"tender_id": "T2", "bidder_id": "A", "awarded_flag": False},
        {"tender_id": "T2", "bidder_id": "B", "awarded_flag": True},
        {"tender_id": "T3", "bidder_id": "C", "awarded_flag": True},
        {"tender_id": "T4", "bidder_id": "C", "awarded_flag": True},
    ]
    profile = {
        "influence_baseline_max": 0.60,
        "influence_conditional_min": 0.90,
        "influence_gap_min": 0.40,
    }

    rows = conditional_influence.detect(bids, profile, RUN_TIMESTAMP)

    assert [row["subject_id"] for row in rows] == ["B<-A"]
    assert rows[0]["risk_level"] == "MEDIUM"
