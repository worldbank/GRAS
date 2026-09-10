from gras.common.normalization import (
    normalize_bids,
    normalize_employment,
    normalize_sanctions,
    normalize_tenders,
)


def test_normalization_excludes_rows_without_required_identifiers() -> None:
    tenders = normalize_tenders(
        [
            {"tender_id": "", "entity_id": "E1"},
            {"tender_id": "T1", "entity_id": ""},
            {"tender_id": "T2", "entity_id": "E2"},
        ]
    )
    bids = normalize_bids(
        [
            {"bid_id": "B1", "tender_id": "", "bidder_id": "S1"},
            {"bid_id": "B2", "tender_id": "T2", "bidder_id": ""},
            {"bid_id": "B3", "tender_id": "T2", "bidder_id": "S2"},
        ]
    )
    employment = normalize_employment(
        [
            {"person_id": "", "employer_name": "Public body"},
            {"person_id": "S2", "employer_name": "Public body"},
        ]
    )

    assert [row["tender_id"] for row in tenders] == ["T2"]
    assert [row["bid_id"] for row in bids] == ["B3"]
    assert [row["person_id"] for row in employment] == ["S2"]


def test_normalization_excludes_invalid_sanction_windows() -> None:
    sanctions = normalize_sanctions(
        [
            {
                "bidder_id": "S1",
                "sanction_start": "2024-02-01",
                "sanction_end": "2024-01-01",
                "sanction_type": "invalid-order",
            },
            {
                "bidder_id": "S2",
                "sanction_start": "not-a-date",
                "sanction_end": "2024-03-01",
                "sanction_type": "invalid-date",
            },
            {
                "bidder_id": "S3",
                "sanction_start": "2024-01-01",
                "sanction_end": "2024-03-01",
                "sanction_type": "valid",
            },
        ]
    )

    assert [row["bidder_id"] for row in sanctions] == ["S3"]
