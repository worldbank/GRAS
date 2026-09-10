"""Offline runner for the GRAS reference implementation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from gras import __version__
from gras.aggregations.risk_rollup import build_rollups
from gras.common.normalization import (
    load_profile,
    normalize_bids,
    normalize_employment,
    normalize_sanctions,
    normalize_tenders,
    now_iso_utc,
    read_csv_records,
    write_csv_records,
)
from gras.data_contract import (
    CONTRACT_VERSION,
    INDICATOR_OUTPUT_COLUMNS,
    INPUT_CONTRACT,
    SUMMARY_OUTPUT_COLUMNS,
)
from gras.typologies import (
    association_rules,
    coaward_pairs,
    conditional_influence,
    group_patterns,
    network_event_centric,
    public_employee_bidder,
    repeated_fiscal_address,
    sanction_overlap,
    single_bidder,
    top_loser,
    top_loser_winner_links,
)


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _input_metadata(path: str, row_count: int) -> dict[str, object]:
    return {
        "file_name": Path(path).name,
        "row_count": row_count,
        "sha256": _sha256(path),
    }


def run_pipeline(
    tenders_path: str,
    bids_path: str,
    sanctions_path: str,
    employment_path: str,
    output_dir: str,
    profile_path: str | None = None,
    profile_name: str = "balanced",
    run_timestamp: str | None = None,
) -> None:
    tenders_raw = read_csv_records(tenders_path, INPUT_CONTRACT["tenders"], allow_empty=False)
    bids_raw = read_csv_records(bids_path, INPUT_CONTRACT["bids"], allow_empty=False)
    sanctions_raw = read_csv_records(sanctions_path, INPUT_CONTRACT["sanctions"])
    employment_raw = read_csv_records(employment_path, INPUT_CONTRACT["employment"])

    tenders = normalize_tenders(tenders_raw)
    bids = normalize_bids(bids_raw)
    sanctions = normalize_sanctions(sanctions_raw)
    employment = normalize_employment(employment_raw)
    # Stable summation and traversal order for equivalent input row multisets.
    for rows in (tenders, bids, sanctions, employment):
        rows.sort(key=lambda row: json.dumps(row, sort_keys=True, default=str))
    profile = load_profile(profile_path, profile_name=profile_name)
    run_ts = run_timestamp or now_iso_utc()

    all_indicators: list[dict[str, object]] = []

    r_single = single_bidder.detect(bids, profile, run_ts)
    all_indicators.extend(r_single)

    r_top_loser = top_loser.detect(bids, profile, run_ts)
    all_indicators.extend(r_top_loser)
    top_loser_ids = {r["subject_id"] for r in r_top_loser}

    r_tl_links = top_loser_winner_links.detect(bids, top_loser_ids, profile, run_ts)
    all_indicators.extend(r_tl_links)
    top_loser_winner_ids = {rec["subject_id"].split("|")[0] for rec in r_tl_links if "|" in rec["subject_id"]}

    r_pairs = coaward_pairs.detect(bids, profile, run_ts)
    all_indicators.extend(r_pairs)

    r_rules = association_rules.detect(bids, r_pairs, profile, run_ts)
    all_indicators.extend(r_rules)

    r_groups = group_patterns.detect(bids, profile, run_ts)
    all_indicators.extend(r_groups)

    r_influence = conditional_influence.detect(bids, profile, run_ts)
    all_indicators.extend(r_influence)

    r_network = network_event_centric.detect(bids, top_loser_ids, top_loser_winner_ids, profile, run_ts)
    all_indicators.extend(r_network)

    r_sanction = sanction_overlap.detect(bids, sanctions, run_ts)
    all_indicators.extend(r_sanction)

    r_employee = public_employee_bidder.detect(bids, employment, profile, run_ts)
    all_indicators.extend(r_employee)

    r_address = repeated_fiscal_address.detect(bids, profile, run_ts)
    all_indicators.extend(r_address)

    supplier_summary, tender_summary, entity_summary = build_rollups(all_indicators, tenders)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    write_csv_records(str(out / "indicator_results.csv"), INDICATOR_OUTPUT_COLUMNS, all_indicators)
    write_csv_records(str(out / "supplier_risk_summary.csv"), SUMMARY_OUTPUT_COLUMNS, supplier_summary)
    write_csv_records(str(out / "tender_risk_summary.csv"), SUMMARY_OUTPUT_COLUMNS, tender_summary)
    write_csv_records(str(out / "entity_risk_summary.csv"), SUMMARY_OUTPUT_COLUMNS, entity_summary)

    metadata = {
        "contract_version": CONTRACT_VERSION,
        "package_version": __version__,
        "profile_name": profile["profile_name"],
        "profile_version": profile["profile_version"],
        "run_timestamp": run_ts,
        "inputs": {
            "tenders": _input_metadata(tenders_path, len(tenders_raw)),
            "bids": _input_metadata(bids_path, len(bids_raw)),
            "sanctions": _input_metadata(sanctions_path, len(sanctions_raw)),
            "employment": _input_metadata(employment_path, len(employment_raw)),
        },
        "outputs": {
            "indicator_results.csv": len(all_indicators),
            "supplier_risk_summary.csv": len(supplier_summary),
            "tender_risk_summary.csv": len(tender_summary),
            "entity_risk_summary.csv": len(entity_summary),
        },
    }
    (out / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run generic GRAS method indicators on CSV files")
    parser.add_argument("--tenders", required=True)
    parser.add_argument("--bids", required=True)
    parser.add_argument("--sanctions", required=True)
    parser.add_argument("--employment", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--profile", required=False, default=None)
    parser.add_argument("--profile-name", required=False, default="balanced")
    parser.add_argument("--run-timestamp", required=False, default=None)
    args = parser.parse_args()

    run_pipeline(
        tenders_path=args.tenders,
        bids_path=args.bids,
        sanctions_path=args.sanctions,
        employment_path=args.employment,
        output_dir=args.out,
        profile_path=args.profile,
        profile_name=args.profile_name,
        run_timestamp=args.run_timestamp,
    )


if __name__ == "__main__":
    main()
