"""Group pattern detector: exclusivity, turn-taking, dominance."""

from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt
from statistics import mean
from typing import Any

from gras.common.normalization import make_indicator_record

CODE = "IND006_GROUP_PATTERNS"
NAME = "Group Patterns"


def _std(values: list[float]) -> float:
    if not values:
        return 0.0
    m = mean(values)
    if m == 0:
        return 0.0
    var = sum((v - m) ** 2 for v in values) / len(values)
    return sqrt(var)


def detect(bids: list[dict[str, Any]], profile: dict[str, Any], run_ts: str) -> list[dict[str, Any]]:
    participants_by_tender: dict[str, set[str]] = defaultdict(set)
    winners_by_tender: dict[str, set[str]] = defaultdict(set)

    for bid in bids:
        t = bid["tender_id"]
        s = bid["bidder_id"]
        participants_by_tender[t].add(s)
        if bid["awarded_flag"]:
            winners_by_tender[t].add(s)

    transactions = [tuple(sorted(v)) for v in participants_by_tender.values() if 3 <= len(v) <= 5]
    group_counter = Counter(transactions)

    min_recurrence = profile["group_min_recurrence"]
    excl_high = profile["group_exclusivity_high"]
    turn_cv = profile["group_turn_taking_cv"]
    dom_share_gate = profile["group_dominance_share"]

    results: list[dict[str, Any]] = []
    for group, recurrence in group_counter.items():
        if recurrence < min_recurrence:
            continue

        gset = set(group)
        events_any = [t for t, ps in participants_by_tender.items() if ps & gset]
        events_full = sorted(t for t, ps in participants_by_tender.items() if gset.issubset(ps))
        exclusivity = (len(events_full) / len(events_any)) if events_any else 0.0

        win_counter: Counter[str] = Counter()
        for t in events_full:
            for w in winners_by_tender.get(t, set()):
                if w in gset:
                    win_counter[w] += 1

        win_shares = []
        total_group_wins = sum(win_counter.values())
        for member in group:
            share = (win_counter.get(member, 0) / total_group_wins) if total_group_wins else 0.0
            win_shares.append(share)

        cv = (_std(win_shares) / mean(win_shares)) if win_shares and mean(win_shares) > 0 else 0.0
        dominance_share = max(win_shares) if win_shares else 0.0

        pattern_type: str | None = None
        level: str | None = None
        score: float | None = None
        if exclusivity >= excl_high:
            pattern_type = "exclusivity"
            level = "HIGH"
            score = 85 + min(10, recurrence * 2)
        elif cv <= turn_cv and total_group_wins >= len(events_full) * 0.8:
            pattern_type = "turn_taking"
            level = "MEDIUM"
            score = 70 + min(15, recurrence * 2)
        elif dominance_share >= dom_share_gate and recurrence >= min_recurrence:
            pattern_type = "dominance"
            level = "MEDIUM"
            score = 68 + (dominance_share * 20)

        if not pattern_type or level is None or score is None:
            continue

        evidence = {
            "group_size": len(group),
            "group_members": list(group),
            "recurrence": recurrence,
            "exclusivity_ratio": round(exclusivity, 4),
            "turn_taking_cv": round(cv, 4),
            "dominance_share": round(dominance_share, 4),
            "pattern_type": pattern_type,
            "tender_ids": events_full,
        }

        results.append(
            make_indicator_record(
                code=CODE,
                name=NAME,
                subject_type="group",
                subject_id="|".join(group),
                risk_level=level,
                risk_score=score,
                evidence=evidence,
                run_timestamp=run_ts,
            )
        )

    return sorted(results, key=lambda r: (r["risk_score"], r["subject_id"]), reverse=True)
