"""Single bidder concentration indicator."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from gras.common.normalization import make_indicator_record

CODE = "IND001_SINGLE_BIDDER"
NAME = "Single Bidder Concentration"


def detect(bids: list[dict[str, Any]], profile: dict[str, Any], run_ts: str) -> list[dict[str, Any]]:
    bidders_by_tender: dict[str, set[str]] = defaultdict(set)
    for bid in bids:
        bidders_by_tender[bid["tender_id"]].add(bid["bidder_id"])

    single_tenders = {t for t, bidders in bidders_by_tender.items() if len(bidders) == 1}

    awards_total: dict[str, set[str]] = defaultdict(set)
    awards_single: dict[str, set[str]] = defaultdict(set)
    value_single: dict[str, float] = defaultdict(float)

    for bid in bids:
        if not bid["awarded_flag"]:
            continue
        supplier = bid["bidder_id"]
        awards_total[supplier].add(bid["tender_id"])
        if bid["tender_id"] in single_tenders:
            awards_single[supplier].add(bid["tender_id"])
            value_single[supplier] += bid["awarded_value"]

    results: list[dict[str, Any]] = []
    min_awards = profile["single_bidder_min_awards"]
    medium_ratio = profile["single_bidder_ratio_medium"]
    high_ratio = profile["single_bidder_ratio_high"]

    for supplier, awarded_tenders in awards_total.items():
        total = len(awarded_tenders)
        if total < min_awards:
            continue
        single = len(awards_single.get(supplier, set()))
        ratio = (single / total) if total else 0.0
        if ratio < medium_ratio:
            continue

        if ratio >= high_ratio and single >= min_awards:
            level = "HIGH"
            score = 85 + (ratio * 10)
        else:
            level = "MEDIUM"
            score = 60 + (ratio * 20)

        evidence = {
            "awards_total": total,
            "awards_single_bidder": single,
            "single_bidder_ratio": round(ratio, 4),
            "single_bidder_awarded_value": round(value_single.get(supplier, 0.0), 2),
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

    return sorted(results, key=lambda row: (-row["risk_score"], row["subject_id"]))
