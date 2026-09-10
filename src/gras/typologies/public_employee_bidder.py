"""Public employee bidder overlap indicator."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from gras.common.normalization import make_indicator_record

CODE = "IND010_PUBLIC_EMPLOYEE_BIDDER"
NAME = "Public Employee Bidder Overlap"


def detect(
    bids: list[dict[str, Any]],
    employment: list[dict[str, Any]],
    profile: dict[str, Any],
    run_ts: str,
) -> list[dict[str, Any]]:
    min_part = profile["employee_bidder_min_participations"]

    employment_by_person: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in employment:
        employment_by_person[row["person_id"]].append(row)

    part_count: dict[str, set[str]] = defaultdict(set)
    winning_tenders: dict[str, set[str]] = defaultdict(set)
    value_count: dict[str, float] = defaultdict(float)

    for bid in bids:
        supplier = bid["bidder_id"]
        if supplier not in employment_by_person:
            continue
        part_count[supplier].add(bid["tender_id"])
        if bid["awarded_flag"]:
            winning_tenders[supplier].add(bid["tender_id"])
            value_count[supplier] += bid["awarded_value"]

    results: list[dict[str, Any]] = []
    for supplier, tenders in part_count.items():
        participations = len(tenders)
        if participations < min_part:
            continue
        wins = len(winning_tenders.get(supplier, set()))
        level = "HIGH" if wins >= 2 else "MEDIUM"
        score = 70 + min(25, participations * 6 + wins * 8)

        employer_context = sorted({r["employer_name"] for r in employment_by_person[supplier]})[:3]
        role_context = sorted({r["role_name"] for r in employment_by_person[supplier]})[:3]

        evidence = {
            "participations": participations,
            "wins": wins,
            "awarded_value": round(value_count.get(supplier, 0.0), 2),
            "employer_context": employer_context,
            "role_context": role_context,
            "tender_ids": sorted(tenders),
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
