"""Input and output schema contract utilities."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

CONTRACT_VERSION = "2.0.0"

INPUT_CONTRACT = {
    "tenders": [
        "tender_id",
        "entity_id",
        "modality",
        "publication_date",
        "participant_count",
    ],
    "bids": [
        "bid_id",
        "tender_id",
        "bidder_id",
        "bidder_name",
        "awarded_flag",
        "awarded_value",
        "submission_date",
        "fiscal_address",
    ],
    "sanctions": [
        "bidder_id",
        "sanction_start",
        "sanction_end",
        "sanction_type",
    ],
    "employment": [
        "person_id",
        "employer_name",
        "role_name",
        "entry_date",
        "salary",
    ],
}

INDICATOR_OUTPUT_COLUMNS = [
    "indicator_code",
    "indicator_name",
    "subject_type",
    "subject_id",
    "risk_level",
    "risk_score",
    "evidence_json",
    "run_timestamp",
]

SUMMARY_OUTPUT_COLUMNS = [
    "subject_id",
    "indicator_count",
    "max_risk_level",
    "weighted_score",
    "indicator_codes",
]


def validate_header(columns: Iterable[str], required_columns: list[str]) -> None:
    """Validate column names even when a CSV has no data rows."""
    available = set(columns)
    missing = [col for col in required_columns if col not in available]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def validate_columns(rows: Iterable[Mapping[str, object]], required_columns: list[str]) -> None:
    """Raise ValueError if required columns are missing in row dicts."""
    rows = list(rows)
    if not rows:
        raise ValueError("Input table is empty.")
    validate_header(rows[0].keys(), required_columns)
