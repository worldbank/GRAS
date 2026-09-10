import json

from gras.typologies import network_event_centric

RUN_TIMESTAMP = "2026-01-01T00:00:00Z"


def test_equal_sized_components_use_stable_content_order() -> None:
    bids = [
        {"tender_id": "T-C", "bidder_id": "W3", "awarded_flag": True},
        {"tender_id": "T-C", "bidder_id": "L3", "awarded_flag": False},
        {"tender_id": "T-A", "bidder_id": "W1", "awarded_flag": True},
        {"tender_id": "T-A", "bidder_id": "L1", "awarded_flag": False},
        {"tender_id": "T-B", "bidder_id": "W2", "awarded_flag": True},
        {"tender_id": "T-B", "bidder_id": "L2", "awarded_flag": False},
    ]
    profile = {
        "network_min_pf_count": 1,
        "network_min_pf_share": 0.5,
    }

    rows = network_event_centric.detect(
        bids,
        top_loser_ids={"L1", "L2", "L3"},
        top_loser_winner_ids={"W1", "W2", "W3"},
        profile=profile,
        run_ts=RUN_TIMESTAMP,
    )

    assert [json.loads(row["evidence_json"])["event_ids"] for row in rows] == [
        ["T-A"],
        ["T-B"],
        ["T-C"],
    ]
