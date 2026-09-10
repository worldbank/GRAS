"""Event-centric suspicious network component indicator."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from gras.common.normalization import make_indicator_record

CODE = "IND008_EVENT_CENTRIC_NETWORK"
NAME = "Event-Centric Suspicious Network"


def detect(
    bids: list[dict[str, Any]],
    top_loser_ids: set[str],
    top_loser_winner_ids: set[str],
    profile: dict[str, Any],
    run_ts: str,
) -> list[dict[str, Any]]:
    participants_by_tender: dict[str, set[str]] = defaultdict(set)
    winners_by_tender: dict[str, set[str]] = defaultdict(set)

    for bid in bids:
        t = bid["tender_id"]
        s = bid["bidder_id"]
        participants_by_tender[t].add(s)
        if bid["awarded_flag"]:
            winners_by_tender[t].add(s)

    suspicious_events: set[str] = set()
    min_pf_count = profile["network_min_pf_count"]
    min_pf_share = profile["network_min_pf_share"]

    for t, participants in participants_by_tender.items():
        if not participants:
            continue
        pf_count = len([s for s in participants if s in top_loser_ids])
        pf_share = pf_count / len(participants)
        has_pf_winner_link = any(w in top_loser_winner_ids for w in winners_by_tender.get(t, set()))
        if pf_count >= min_pf_count and pf_share >= min_pf_share and has_pf_winner_link:
            suspicious_events.add(t)

    adjacency: dict[str, set[str]] = defaultdict(set)
    for t in sorted(suspicious_events):
        event_node = f"E:{t}"
        for s in sorted(participants_by_tender[t]):
            supplier_node = f"S:{s}"
            adjacency[event_node].add(supplier_node)
            adjacency[supplier_node].add(event_node)

    seen: set[str] = set()
    components: list[set[str]] = []
    for node in sorted(adjacency):
        if node in seen:
            continue
        comp: set[str] = set()
        queue: deque[str] = deque([node])
        seen.add(node)
        while queue:
            cur = queue.popleft()
            comp.add(cur)
            for nxt in sorted(adjacency[cur]):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        components.append(comp)

    results: list[dict[str, Any]] = []
    ordered_components = sorted(
        components,
        key=lambda comp: (
            -len(comp),
            tuple(sorted(node[2:] for node in comp if node.startswith("E:"))),
            tuple(sorted(node[2:] for node in comp if node.startswith("S:"))),
        ),
    )
    for idx, comp in enumerate(ordered_components, start=1):
        event_ids = sorted(n[2:] for n in comp if n.startswith("E:"))
        supplier_ids = sorted(n[2:] for n in comp if n.startswith("S:"))
        if not event_ids or not supplier_ids:
            continue

        edge_count = sum(len(adjacency[n]) for n in comp) // 2
        size_score = len(event_ids) + len(supplier_ids)
        level = "HIGH" if size_score >= 8 else "MEDIUM"
        score = 68 + min(28, size_score * 3)

        evidence = {
            "component_index": idx,
            "event_count": len(event_ids),
            "supplier_count": len(supplier_ids),
            "edge_count": edge_count,
            "event_ids": event_ids,
            "supplier_ids": supplier_ids,
        }

        results.append(
            make_indicator_record(
                code=CODE,
                name=NAME,
                subject_type="network_component",
                subject_id=f"component_{idx}",
                risk_level=level,
                risk_score=score,
                evidence=evidence,
                run_timestamp=run_ts,
            )
        )

    return results
