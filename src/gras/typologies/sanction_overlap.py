"""Sanction overlap indicator."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from gras.common.normalization import make_indicator_record

CODE = "IND009_SANCTION_OVERLAP"
NAME = "Sanction Overlap"


def _is_overlap(submission_date: date | None, start_date: date | None, end_date: date | None) -> bool:
    if not submission_date or not start_date or not end_date:
        return False
    return start_date <= submission_date <= end_date


def detect(
    bids: list[dict[str, Any]],
    sanctions: list[dict[str, Any]],
    run_ts: str,
) -> list[dict[str, Any]]:
    sanctions_by_supplier: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in sanctions:
        sanctions_by_supplier[row["bidder_id"]].append(row)

    overlap_count: dict[str, int] = defaultdict(int)
    value_proxy: dict[str, float] = defaultdict(float)
    overlap_tenders: dict[str, set[str]] = defaultdict(set)

    for bid in bids:
        if not bid["awarded_flag"]:
            continue
        supplier = bid["bidder_id"]
        for s in sanctions_by_supplier.get(supplier, []):
            if _is_overlap(bid["submission_date"], s["sanction_start"], s["sanction_end"]):
                overlap_count[supplier] += 1
                value_proxy[supplier] += bid["awarded_value"]
                overlap_tenders[supplier].add(bid["tender_id"])
                # The unit is an awarded input row, not a matching sanction.
                break

    results: list[dict[str, Any]] = []
    for supplier, count in overlap_count.items():
        level = "HIGH" if count >= 2 else "MEDIUM"
        score = 75 + min(20, count * 8)
        evidence = {
            "overlap_awards": count,
            "overlap_value_proxy": round(value_proxy[supplier], 2),
            "tender_ids": sorted(overlap_tenders[supplier]),
        }
        results.append(
            make_indicator_record(
                code=CODE,
                name=NAME,
                subject_type="supplier",
                subject_id=supplier,
                risk_level=level,
                risk_score=score,
                evidence=evidence,
                run_timestamp=run_ts,
            )
        )

    return sorted(results, key=lambda r: (r["risk_score"], r["subject_id"]), reverse=True)
