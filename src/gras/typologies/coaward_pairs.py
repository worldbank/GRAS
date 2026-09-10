"""Co-award pairs indicator."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Any

from gras.common.normalization import make_indicator_record

CODE = "IND004_COAWARD_PAIRS"
NAME = "Co-Award Pairs"


def detect(bids: list[dict[str, Any]], profile: dict[str, Any], run_ts: str) -> list[dict[str, Any]]:
    participants_by_tender: dict[str, set[str]] = defaultdict(set)
    winners_by_tender: dict[str, set[str]] = defaultdict(set)
    value_by_tender: dict[str, float] = defaultdict(float)

    for bid in bids:
        tender = bid["tender_id"]
        supplier = bid["bidder_id"]
        participants_by_tender[tender].add(supplier)
        if bid["awarded_flag"]:
            winners_by_tender[tender].add(supplier)
            value_by_tender[tender] += bid["awarded_value"]

    events_together: dict[tuple[str, str], int] = defaultdict(int)
    co_awards: dict[tuple[str, str], int] = defaultdict(int)
    value_proxy: dict[tuple[str, str], float] = defaultdict(float)
    tender_refs: dict[tuple[str, str], list[str]] = defaultdict(list)

    for tender, participants in participants_by_tender.items():
        sorted_participants = sorted(participants)
        for a, b in combinations(sorted_participants, 2):
            key = (a, b)
            events_together[key] += 1
        winners = sorted(winners_by_tender.get(tender, set()))
        for a, b in combinations(winners, 2):
            key = (a, b)
            co_awards[key] += 1
            value_proxy[key] += value_by_tender.get(tender, 0.0)
            tender_refs[key].append(tender)

    min_events = profile["coaward_min_events_together"]
    medium_rate = profile["coaward_rate_medium"]
    high_rate = profile["coaward_rate_high"]

    results: list[dict[str, Any]] = []
    for key, together in events_together.items():
        if together < min_events:
            continue
        co = co_awards.get(key, 0)
        if co == 0:
            continue
        rate = co / together
        if rate < medium_rate:
            continue

        score: float
        if rate >= high_rate and co >= min_events:
            level = "HIGH"
            score = 80 + min(15, co * 3)
        else:
            level = "MEDIUM"
            score = 65 + (rate * 20)

        evidence = {
            "supplier_a": key[0],
            "supplier_b": key[1],
            "events_together": together,
            "co_awards": co,
            "co_award_rate": round(rate, 4),
            "value_proxy": round(value_proxy.get(key, 0.0), 2),
            "tender_ids": sorted(set(tender_refs.get(key, []))),
        }
        results.append(
            make_indicator_record(
                code=CODE,
                name=NAME,
                subject_type="pair",
                subject_id=f"{key[0]}|{key[1]}",
                risk_level=level,
                risk_score=score,
                evidence=evidence,
                run_timestamp=run_ts,
            )
        )

    return sorted(results, key=lambda r: (r["risk_score"], r["subject_id"]), reverse=True)
