"""Conditional influence indicator."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from gras.common.normalization import make_indicator_record

CODE = "IND007_CONDITIONAL_INFLUENCE"
NAME = "Conditional Influence"


def detect(bids: list[dict[str, Any]], profile: dict[str, Any], run_ts: str) -> list[dict[str, Any]]:
    events: set[str] = set()
    events_by_supplier: dict[str, set[str]] = defaultdict(set)
    wins_by_supplier: dict[str, set[str]] = defaultdict(set)

    for bid in bids:
        t = bid["tender_id"]
        s = bid["bidder_id"]
        events.add(t)
        events_by_supplier[s].add(t)
        if bid["awarded_flag"]:
            wins_by_supplier[s].add(t)

    n_total = max(1, len(events))
    suppliers = sorted(events_by_supplier.keys())

    baseline_max = profile["influence_baseline_max"]
    cond_min = profile["influence_conditional_min"]
    gap_min = profile["influence_gap_min"]

    results: list[dict[str, Any]] = []
    for a in suppliers:
        baseline = len(wins_by_supplier.get(a, set())) / n_total
        for b in suppliers:
            if a == b:
                continue
            b_events = events_by_supplier.get(b, set())
            if not b_events:
                continue
            a_wins_with_b = len(wins_by_supplier.get(a, set()) & b_events)
            conditional = a_wins_with_b / len(b_events)
            gap = conditional - baseline

            if baseline > baseline_max or conditional < cond_min or gap < gap_min:
                continue

            magnitude = conditional / baseline if baseline > 0 else 999.0
            level = "HIGH" if magnitude >= 3 else "MEDIUM"
            score = 70 + min(25, gap * 100 / 4)
            evidence = {
                "target_supplier": a,
                "conditioning_supplier": b,
                "baseline_win_probability": round(baseline, 4),
                "conditional_win_probability": round(conditional, 4),
                "influence_gap": round(gap, 4),
                "influence_magnitude": round(magnitude, 4),
                "conditioning_event_count": len(b_events),
                "tender_ids": sorted(b_events),
            }
            results.append(
                make_indicator_record(
                    code=CODE,
                    name=NAME,
                    subject_type="pair",
                    subject_id=f"{a}<-{b}",
                    risk_level=level,
                    risk_score=score,
                    evidence=evidence,
                    run_timestamp=run_ts,
                )
            )

    return sorted(results, key=lambda r: (r["risk_score"], r["subject_id"]), reverse=True)
