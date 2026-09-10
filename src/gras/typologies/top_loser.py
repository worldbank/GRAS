"""Top loser indicator."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from gras.common.normalization import make_indicator_record

CODE = "IND002_TOP_LOSER"
NAME = "Top Loser"


def detect(bids: list[dict[str, Any]], profile: dict[str, Any], run_ts: str) -> list[dict[str, Any]]:
    participations: dict[str, set[str]] = defaultdict(set)
    wins: dict[str, set[str]] = defaultdict(set)
    value_total: dict[str, float] = defaultdict(float)

    for bid in bids:
        supplier = bid["bidder_id"]
        tender = bid["tender_id"]
        participations[supplier].add(tender)
        if bid["awarded_flag"]:
            wins[supplier].add(tender)
            value_total[supplier] += bid["awarded_value"]

    min_part = profile["top_loser_min_participations"]
    medium_success = profile["top_loser_success_medium"]
    high_success = profile["top_loser_success_high"]

    results: list[dict[str, Any]] = []
    for supplier, event_set in participations.items():
        total_p = len(event_set)
        if total_p < min_part:
            continue
        total_w = len(wins.get(supplier, set()))
        success = total_w / total_p if total_p else 0.0

        if success > medium_success:
            continue

        if success <= high_success:
            level = "HIGH"
            score = 85 + min(10, total_p / max(min_part, 1))
        else:
            level = "MEDIUM"
            score = 65 + (1.0 - success) * 20

        evidence = {
            "participations": total_p,
            "wins": total_w,
            "success_rate": round(success, 4),
            "awarded_value": round(value_total.get(supplier, 0.0), 2),
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
