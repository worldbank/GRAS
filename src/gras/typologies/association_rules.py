"""Association metrics over co-award pairs."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from gras.common.normalization import make_indicator_record

CODE = "IND005_ASSOCIATION_RULES"
NAME = "Association Rules"


def detect(
    bids: list[dict[str, Any]],
    coaward_records: list[dict[str, Any]],
    profile: dict[str, Any],
    run_ts: str,
) -> list[dict[str, Any]]:
    award_events: dict[str, set[str]] = defaultdict(set)
    all_events: set[str] = set()
    for bid in bids:
        all_events.add(bid["tender_id"])
        if bid["awarded_flag"]:
            award_events[bid["bidder_id"]].add(bid["tender_id"])

    n_total = max(1, len(all_events))
    min_support = profile["association_min_support"]
    min_conf = profile["association_min_confidence"]

    results: list[dict[str, Any]] = []
    # IND004 selects candidate pairs; count all probabilities on the same
    # award-event universe. Each direction is an independent association rule.
    candidate_pairs = {tuple(sorted(rec["subject_id"].split("|"))) for rec in coaward_records}
    for pair in sorted(candidate_pairs):
        if len(pair) != 2 or pair[0] == pair[1]:
            continue
        a, b = pair
        joint_events = award_events[a] & award_events[b]
        support_xy = len(joint_events) / n_total
        if not joint_events or support_xy < min_support:
            continue
        for antecedent, consequent in ((a, b), (b, a)):
            support_a = len(award_events[antecedent]) / n_total
            support_b = len(award_events[consequent]) / n_total
            confidence = len(joint_events) / len(award_events[antecedent])
            if confidence < min_conf:
                continue
            lift = support_xy / (support_a * support_b)
            leverage = support_xy - (support_a * support_b)
            conviction: float | None = None
            conviction_status = "undefined" if support_b == 1 else "infinite"
            if confidence < 1:
                conviction = round((1 - support_b) / (1 - confidence), 6)
                conviction_status = "finite"

            level = "HIGH" if (confidence >= 0.8 and lift >= 1.5) else "MEDIUM"
            score = 65 + min(30, confidence * 20 + max(0.0, lift - 1) * 10)
            evidence = {
                "supplier_a": antecedent,
                "supplier_b": consequent,
                "event_basis": "award",
                "support": round(support_xy, 6),
                "support_a": round(support_a, 6),
                "support_b": round(support_b, 6),
                "confidence": round(confidence, 6),
                "lift": round(lift, 6),
                "leverage": round(leverage, 6),
                "conviction": conviction,
                "conviction_status": conviction_status,
                "tender_ids": sorted(joint_events),
            }
            results.append(
                make_indicator_record(
                    code=CODE,
                    name=NAME,
                    subject_type="pair",
                    subject_id=f"{antecedent}->{consequent}",
                    risk_level=level,
                    risk_score=score,
                    evidence=evidence,
                    run_timestamp=run_ts,
                )
            )

    return sorted(results, key=lambda r: (r["risk_score"], r["subject_id"]), reverse=True)
