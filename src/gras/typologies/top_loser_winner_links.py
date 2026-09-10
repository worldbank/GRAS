"""Top loser winner link indicator."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from gras.common.normalization import make_indicator_record

CODE = "IND003_TOP_LOSER_WINNER_LINK"
NAME = "Top Loser Winner Link"


def detect(
    bids: list[dict[str, Any]],
    top_loser_ids: set[str],
    profile: dict[str, Any],
    run_ts: str,
) -> list[dict[str, Any]]:
    participants_by_tender: dict[str, set[str]] = defaultdict(set)
    winners_by_tender: dict[str, set[str]] = defaultdict(set)

    for bid in bids:
        tender = bid["tender_id"]
        supplier = bid["bidder_id"]
        participants_by_tender[tender].add(supplier)
        if bid["awarded_flag"]:
            winners_by_tender[tender].add(supplier)

    links: dict[tuple[str, str], int] = defaultdict(int)
    tender_refs: dict[tuple[str, str], list[str]] = defaultdict(list)
    winner_exposure: dict[str, set[str]] = defaultdict(set)

    for tender, participants in participants_by_tender.items():
        tls = sorted(s for s in participants if s in top_loser_ids)
        if not tls:
            continue
        winners = sorted(winners_by_tender.get(tender, set()))
        for winner in winners:
            winner_exposure[winner].add(tender)
            for tl in tls:
                if winner == tl:
                    continue
                key = (winner, tl)
                links[key] += 1
                tender_refs[key].append(tender)

    min_links = profile["top_loser_winner_min_links"]
    results: list[dict[str, Any]] = []
    for (winner, tl), count in links.items():
        if count < min_links:
            continue
        exposure = len(winner_exposure[winner])
        link_density = count / exposure if exposure else 0.0
        level = "HIGH" if count >= (min_links + 1) else "MEDIUM"
        score = 70 + min(25, count * 8)
        evidence = {
            "winner_id": winner,
            "top_loser_id": tl,
            "recurrent_links": count,
            "winner_exposure_to_top_loser_events": exposure,
            "link_density": round(link_density, 4),
            "tender_ids": sorted(set(tender_refs[(winner, tl)])),
        }
        results.append(
            make_indicator_record(
                code=CODE,
                name=NAME,
                subject_type="pair",
                subject_id=f"{winner}|{tl}",
                risk_level=level,
                risk_score=score,
                evidence=evidence,
                run_timestamp=run_ts,
            )
        )

    return sorted(results, key=lambda r: (r["risk_score"], r["subject_id"]), reverse=True)
