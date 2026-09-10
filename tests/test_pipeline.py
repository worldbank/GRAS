import csv
import json
from pathlib import Path

from gras.pipeline.run_all import run_pipeline

FIXTURES = Path(__file__).parents[1] / "examples" / "synthetic"
RUN_TIMESTAMP = "2026-01-01T00:00:00Z"


def test_pipeline_accepts_fixed_timestamp_for_reproducible_outputs(tmp_path: Path) -> None:
    run_pipeline(
        tenders_path=str(FIXTURES / "tenders.csv"),
        bids_path=str(FIXTURES / "bids.csv"),
        sanctions_path=str(FIXTURES / "sanctions.csv"),
        employment_path=str(FIXTURES / "employment.csv"),
        output_dir=str(tmp_path),
        profile_name="balanced",
        run_timestamp=RUN_TIMESTAMP,
    )

    with (tmp_path / "indicator_results.csv").open(newline="", encoding="utf-8") as output_file:
        rows = list(csv.DictReader(output_file))

    assert rows
    assert {row["run_timestamp"] for row in rows} == {RUN_TIMESTAMP}
    assert {row["indicator_code"] for row in rows} == {
        "IND001_SINGLE_BIDDER",
        "IND002_TOP_LOSER",
        "IND003_TOP_LOSER_WINNER_LINK",
        "IND004_COAWARD_PAIRS",
        "IND005_ASSOCIATION_RULES",
        "IND006_GROUP_PATTERNS",
        "IND007_CONDITIONAL_INFLUENCE",
        "IND008_EVENT_CENTRIC_NETWORK",
        "IND009_SANCTION_OVERLAP",
        "IND010_PUBLIC_EMPLOYEE_BIDDER",
        "IND011_REPEATED_FISCAL_ADDRESS",
    }
    assert {path.name for path in tmp_path.iterdir()} == {
        "entity_risk_summary.csv",
        "indicator_results.csv",
        "run_metadata.json",
        "supplier_risk_summary.csv",
        "tender_risk_summary.csv",
    }

    metadata = json.loads((tmp_path / "run_metadata.json").read_text(encoding="utf-8"))
    assert metadata["contract_version"] == "2.0.0"
    assert metadata["package_version"] == "0.1.0rc1"
    assert metadata["profile_name"] == "balanced"
    assert metadata["profile_version"] == "1.0.0"
    assert metadata["run_timestamp"] == RUN_TIMESTAMP
    assert metadata["inputs"]["tenders"]["file_name"] == "tenders.csv"
    assert metadata["inputs"]["tenders"]["row_count"] > 0
    assert len(metadata["inputs"]["tenders"]["sha256"]) == 64


def test_synthetic_example_matches_versioned_golden_outputs(tmp_path: Path) -> None:
    run_pipeline(
        tenders_path=str(FIXTURES / "tenders.csv"),
        bids_path=str(FIXTURES / "bids.csv"),
        sanctions_path=str(FIXTURES / "sanctions.csv"),
        employment_path=str(FIXTURES / "employment.csv"),
        output_dir=str(tmp_path),
        profile_name="balanced",
        run_timestamp=RUN_TIMESTAMP,
    )

    for expected_path in sorted((FIXTURES / "expected").iterdir()):
        if expected_path.is_file():
            actual_path = tmp_path / expected_path.name
            assert actual_path.read_bytes() == expected_path.read_bytes(), expected_path.name
