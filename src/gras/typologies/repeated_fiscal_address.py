"""Repeated fiscal address indicator."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from gras.common.normalization import make_indicator_record

CODE = "IND011_REPEATED_FISCAL_ADDRESS"
NAME = "Repeated Fiscal Address"


def detect(bids: list[dict[str, Any]], profile: dict[str, Any], run_ts: str) -> list[dict[str, Any]]:
    min_suppliers = profile["repeated_address_min_suppliers"]
    min_events = profile["repeated_address_min_events"]

    suppliers_by_event_address: dict[tuple[str, str], set[str]] = defaultdict(set)
    awarded_by_event_address: dict[tuple[str, str], int] = defaultdict(int)

    for bid in bids:
        addr = bid["fiscal_address"]
        if not addr:
            continue
        key = (bid["tender_id"], addr)
        suppliers_by_event_address[key].add(bid["bidder_id"])
        if bid["awarded_flag"]:
            awarded_by_event_address[key] += 1

    address_events: dict[str, set[str]] = defaultdict(set)
    address_suppliers: dict[str, set[str]] = defaultdict(set)
    address_awards: dict[str, int] = defaultdict(int)
    event_supplier_ids: dict[tuple[str, str], list[str]] = {}

    for (tender, addr), suppliers in suppliers_by_event_address.items():
        if len(suppliers) < min_suppliers:
            continue
        address_events[addr].add(tender)
        address_suppliers[addr].update(suppliers)
        address_awards[addr] += awarded_by_event_address.get((tender, addr), 0)
        event_supplier_ids[(tender, addr)] = sorted(suppliers)

    results: list[dict[str, Any]] = []
    for addr, events in address_events.items():
        if len(events) < min_events:
            continue
        sup_count = len(address_suppliers[addr])
        level = "HIGH" if (len(events) >= 3 and sup_count >= 3) else "MEDIUM"
        score = 68 + min(27, len(events) * 7 + sup_count * 4)

        for tender in sorted(events):
            evidence = {
                "normalized_fiscal_address": addr,
                "address_event_count": len(events),
                "address_supplier_count": sup_count,
                "address_award_count": address_awards[addr],
                "supplier_ids": event_supplier_ids.get((tender, addr), []),
                "tender_ids": sorted(events),
            }
            results.append(
                make_indicator_record(
                    code=CODE,
                    name=NAME,
                    subject_type="tender",
                    subject_id=tender,
                    risk_level=level,
                    risk_score=score,
                    evidence=evidence,
                    run_timestamp=run_ts,
                )
            )

    return sorted(results, key=lambda r: (r["risk_score"], r["subject_id"]), reverse=True)
