"""Regression cases found during pre-publication methodological review."""

import csv
import json
import random
from datetime import date
from pathlib import Path

import pytest

from gras.aggregations.risk_rollup import build_rollups
from gras.common.normalization import load_profile, parse_float, parse_int, read_csv_records, write_csv_records
from gras.pipeline.run_all import run_pipeline
from gras.typologies import association_rules, coaward_pairs, sanction_overlap

FIXTURES = Path(__file__).parents[1] / "examples" / "synthetic"
TIMESTAMP = "2026-01-01T00:00:00Z"


def run_example(out: Path, **overrides: str) -> None:
    paths = {f"{name}_path": str(FIXTURES / f"{name}.csv") for name in ("tenders", "bids", "sanctions", "employment")}
    run_pipeline(**(paths | overrides), output_dir=str(out), run_timestamp=TIMESTAMP)


def test_association_metrics_share_award_event_semantics_and_both_directions() -> None:
    # A wins 4/10 events, B wins 2/10, and both win 2/10. Losing
    # participations must not change the marginal award probabilities.
    bids = [
        {"tender_id": f"T{i}", "bidder_id": supplier, "awarded_flag": i < wins, "awarded_value": 100}
        for i in range(10)
        for supplier, wins in (("A", 4), ("B", 2))
    ]
    profile = load_profile() | {
        "coaward_rate_medium": 0.1,
        "coaward_rate_high": 0.2,
        "association_min_confidence": 0.4,
    }
    pairs = coaward_pairs.detect(bids, profile, TIMESTAMP)
    rows = association_rules.detect(bids, pairs, profile, TIMESTAMP)
    evidence = {r["subject_id"]: json.loads(r["evidence_json"]) for r in rows}
    assert set(evidence) == {"A->B", "B->A"}
    ab, ba = evidence["A->B"], evidence["B->A"]
    assert (ab["support"], ab["support_a"], ab["support_b"]) == (0.2, 0.4, 0.2)
    assert ab["confidence"] == 0.5
    assert ab["lift"] == ba["lift"] == 2.5
    assert ab["leverage"] == pytest.approx(0.12)
    assert ab["conviction"] == 1.6
    assert ab["conviction_status"] == "finite"
    assert ba["confidence"] == 1.0
    assert ba["conviction"] is None
    assert ba["conviction_status"] == "infinite"
    assert ab["tender_ids"] == ["T0", "T1"]
    suppliers, _, _ = build_rollups(rows, [])
    assert {r["subject_id"] for r in suppliers} == {"A", "B"}
    assert all(r["indicator_count"] == 2 for r in suppliers)
    filtered = association_rules.detect(bids, pairs, profile | {"association_min_confidence": 0.7}, TIMESTAMP)
    assert [r["subject_id"] for r in filtered] == ["B->A"]
    assert association_rules.detect(bids, [], profile, TIMESTAMP) == []


def test_always_awarded_pair_has_undefined_conviction_without_numeric_sentinel() -> None:
    bids = [
        {"tender_id": f"T{i}", "bidder_id": s, "awarded_flag": True, "awarded_value": 1}
        for i in range(2)
        for s in ("A", "B")
    ]
    p = load_profile()
    rows = association_rules.detect(bids, coaward_pairs.detect(bids, p, TIMESTAMP), p, TIMESTAMP)
    assert len(rows) == 2
    for row in rows:
        evidence = json.loads(row["evidence_json"])
        assert evidence["conviction"] is None
        assert evidence["conviction_status"] == "undefined"
        assert evidence["lift"] == 1.0


def test_overlapping_sanctions_count_each_awarded_bid_once() -> None:
    bid = {
        "tender_id": "T1",
        "bidder_id": "A",
        "awarded_flag": True,
        "awarded_value": 100.0,
        "submission_date": date(2024, 6, 1),
    }
    first = {"bidder_id": "A", "sanction_start": date(2024, 1, 1), "sanction_end": date(2024, 12, 31)}
    second = first | {"sanction_start": date(2024, 5, 1), "sanction_end": date(2024, 7, 1)}
    expected = sanction_overlap.detect([bid], [first], TIMESTAMP)
    assert sanction_overlap.detect([bid], [second, first, first], TIMESTAMP) == expected
    assert expected[0]["risk_level"] == "MEDIUM"
    assert json.loads(expected[0]["evidence_json"])["overlap_value_proxy"] == 100
    # Distinct awarded rows remain additive, even within the same tender.
    two = sanction_overlap.detect([bid, bid | {"awarded_value": 40}], [first, second], TIMESTAMP)
    ev = json.loads(two[0]["evidence_json"])
    assert (ev["overlap_awards"], ev["overlap_value_proxy"]) == (2, 140)


@pytest.mark.parametrize(
    "text,expected", [("1234.56", 1234.56), ("1e3", 1000), ("-1.5E-2", -0.015), (" 0 ", 0), ("", 0), (None, 0)]
)
def test_numeric_input_preserves_canonical_values(text: str | None, expected: float) -> None:
    assert parse_float(text) == expected


@pytest.mark.parametrize("text", ["1.234,56", "1,234.56", "$1234", "garbage", "NaN", "Infinity", "1e999", True])
def test_numeric_input_rejects_ambiguous_invalid_or_nonfinite_values(text: object) -> None:
    with pytest.raises(ValueError, match="numeric"):
        parse_float(text)


def test_integer_field_does_not_round_fractional_counts() -> None:
    with pytest.raises(ValueError, match="integer"):
        parse_int("1.6")
    assert parse_int("2.0") == 2


def test_empty_auxiliary_tables_are_valid_but_still_need_headers(tmp_path: Path) -> None:
    overrides = {}
    for name in ("sanctions", "employment"):
        with (FIXTURES / f"{name}.csv").open() as f:
            fields = next(csv.reader(f))
        path = tmp_path / f"{name}.csv"
        write_csv_records(str(path), fields, [])
        overrides[f"{name}_path"] = str(path)
    out = tmp_path / "empty-aux"
    run_example(out, **overrides)
    rows = read_csv_records(str(out / "indicator_results.csv"))
    assert rows
    assert not {"IND009_SANCTION_OVERLAP", "IND010_PUBLIC_EMPLOYEE_BIDDER"} & {r["indicator_code"] for r in rows}
    metadata = json.loads((out / "run_metadata.json").read_text())
    assert metadata["inputs"]["sanctions"]["row_count"] == 0
    assert metadata["inputs"]["employment"]["row_count"] == 0
    bad = tmp_path / "bad.csv"
    bad.write_text("wrong_header\n")
    with pytest.raises(ValueError, match="Missing required columns"):
        run_example(tmp_path / "bad-out", sanctions_path=str(bad))
    bad.write_text("")
    with pytest.raises(ValueError, match="Missing required columns"):
        run_example(tmp_path / "no-header", sanctions_path=str(bad))


def test_empty_core_input_still_fails(tmp_path: Path) -> None:
    path = tmp_path / "bids.csv"
    with (FIXTURES / "bids.csv").open() as f:
        fields = next(csv.reader(f))
    write_csv_records(str(path), fields, [])
    with pytest.raises(ValueError, match="empty"):
        run_example(tmp_path / "out", bids_path=str(path))


def test_bad_numeric_field_fails_before_writing_outputs(tmp_path: Path) -> None:
    rows = read_csv_records(str(FIXTURES / "bids.csv"))
    rows[0]["awarded_value"] = "1.234,56"
    path = tmp_path / "bids.csv"
    write_csv_records(str(path), list(rows[0]), rows)
    with pytest.raises(ValueError, match="numeric"):
        run_example(tmp_path / "out", bids_path=str(path))
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_analytical_outputs_are_independent_of_input_row_order(tmp_path: Path, seed: int) -> None:
    original = tmp_path / "original"
    run_example(original)
    overrides = {}
    for name in ("tenders", "bids", "sanctions", "employment"):
        rows = read_csv_records(str(FIXTURES / f"{name}.csv"))
        random.Random(seed).shuffle(rows)
        path = tmp_path / f"{name}.csv"
        write_csv_records(str(path), list(rows[0]), rows)
        overrides[f"{name}_path"] = str(path)
    shuffled = tmp_path / "shuffled"
    run_example(shuffled, **overrides)
    for expected in original.glob("*.csv"):
        assert expected.read_bytes() == (shuffled / expected.name).read_bytes(), expected.name
    # Raw input hashes intentionally differ after file reordering.
