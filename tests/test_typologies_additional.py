import json

from gras.typologies import association_rules, coaward_pairs, group_patterns, top_loser_winner_links

RUN_TIMESTAMP = "2026-01-01T00:00:00Z"


def test_top_loser_winner_link_preserves_supporting_tenders() -> None:
    bids = [
        {"tender_id": "T1", "bidder_id": "WIN", "awarded_flag": True},
        {"tender_id": "T1", "bidder_id": "TL", "awarded_flag": False},
        {"tender_id": "T2", "bidder_id": "WIN", "awarded_flag": True},
        {"tender_id": "T2", "bidder_id": "TL", "awarded_flag": False},
    ]

    rows = top_loser_winner_links.detect(
        bids,
        top_loser_ids={"TL"},
        profile={"top_loser_winner_min_links": 2},
        run_ts=RUN_TIMESTAMP,
    )

    assert [row["subject_id"] for row in rows] == ["WIN|TL"]
    assert json.loads(rows[0]["evidence_json"])["tender_ids"] == ["T1", "T2"]


def test_top_loser_winner_link_reports_winner_exposure_and_density() -> None:
    bids = [
        {"tender_id": "T1", "bidder_id": "WIN", "awarded_flag": True},
        {"tender_id": "T1", "bidder_id": "TL_A", "awarded_flag": False},
        {"tender_id": "T2", "bidder_id": "WIN", "awarded_flag": True},
        {"tender_id": "T2", "bidder_id": "TL_B", "awarded_flag": False},
    ]

    rows = top_loser_winner_links.detect(
        bids,
        top_loser_ids={"TL_A", "TL_B"},
        profile={"top_loser_winner_min_links": 1},
        run_ts=RUN_TIMESTAMP,
    )

    evidence_by_subject = {
        row["subject_id"]: json.loads(row["evidence_json"])
        for row in rows
    }
    assert evidence_by_subject["WIN|TL_A"]["winner_exposure_to_top_loser_events"] == 2
    assert evidence_by_subject["WIN|TL_A"]["link_density"] == 0.5


def test_association_rule_uses_coaward_support_and_confidence() -> None:
    bids = []
    for tender_id in ("T1", "T2", "T3"):
        bids.extend(
            [
                {
                    "tender_id": tender_id,
                    "bidder_id": "A",
                    "awarded_flag": True,
                    "awarded_value": 100,
                },
                {
                    "tender_id": tender_id,
                    "bidder_id": "B",
                    "awarded_flag": True,
                    "awarded_value": 100,
                },
            ]
        )
    bids.append({"tender_id": "T4", "bidder_id": "C", "awarded_flag": True, "awarded_value": 50})
    profile = {
        "coaward_min_events_together": 2,
        "coaward_rate_medium": 0.6,
        "coaward_rate_high": 0.8,
        "association_min_support": 0.5,
        "association_min_confidence": 0.8,
    }

    coaward_rows = coaward_pairs.detect(bids, profile, RUN_TIMESTAMP)
    rows = association_rules.detect(bids, coaward_rows, profile, RUN_TIMESTAMP)

    assert {row["subject_id"] for row in rows} == {"A->B", "B->A"}
    evidence = json.loads(rows[0]["evidence_json"])
    assert evidence["support"] == 0.75
    assert evidence["confidence"] == 1.0


def test_group_pattern_detects_recurrent_exclusive_group() -> None:
    bids = []
    for tender_id, winner in (("T1", "A"), ("T2", "B")):
        for supplier in ("A", "B", "C"):
            bids.append(
                {
                    "tender_id": tender_id,
                    "bidder_id": supplier,
                    "awarded_flag": supplier == winner,
                }
            )
    profile = {
        "group_min_recurrence": 2,
        "group_exclusivity_high": 0.8,
        "group_turn_taking_cv": 0.25,
        "group_dominance_share": 0.7,
    }

    rows = group_patterns.detect(bids, profile, RUN_TIMESTAMP)

    assert [row["subject_id"] for row in rows] == ["A|B|C"]
    assert rows[0]["risk_level"] == "HIGH"
    assert json.loads(rows[0]["evidence_json"])["pattern_type"] == "exclusivity"
