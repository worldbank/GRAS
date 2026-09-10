"""Risk roll-up aggregations."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from gras.common.normalization import level_to_weight

CODE = "IND012_RISK_ROLLUP"


def _max_level(levels: list[str]) -> str:
    if not levels:
        return "LOW"
    if "HIGH" in levels:
        return "HIGH"
    if "MEDIUM" in levels:
        return "MEDIUM"
    return "LOW"


def _supplier_ids_from_record(record: dict[str, Any]) -> list[str]:
    stype = record["subject_type"]
    sid = record["subject_id"]
    if stype == "supplier":
        return [sid]
    if stype in {"pair", "group"}:
        if "<-" in sid:
            a, b = sid.split("<-", 1)
            return [a, b]
        if "->" in sid:
            a, b = sid.split("->", 1)
            return [a, b]
        return [x for x in sid.split("|") if x]
    if stype == "network_component":
        try:
            evidence = json.loads(record["evidence_json"])
        except (KeyError, TypeError, json.JSONDecodeError):
            return []
        return sorted({str(value) for value in evidence.get("supplier_ids", []) if value})
    return []


def _tender_ids_from_record(record: dict[str, Any]) -> list[str]:
    stype = record["subject_type"]
    if stype == "tender":
        return [record["subject_id"]]
    try:
        evidence = json.loads(record["evidence_json"])
    except (KeyError, TypeError, json.JSONDecodeError):
        return []
    ids = evidence.get("tender_ids", evidence.get("event_ids", []))
    return sorted({str(value) for value in ids if value})


def _summarize(bucket: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for subject_id, records in sorted(bucket.items()):
        levels = [r["risk_level"] for r in records]
        indicator_codes = sorted({r["indicator_code"] for r in records})
        weighted_score = round(
            sum(level_to_weight(r["risk_level"]) * float(r["risk_score"]) for r in records) / max(1, len(records)),
            2,
        )
        output.append(
            {
                "subject_id": subject_id,
                "indicator_count": len(records),
                "max_risk_level": _max_level(levels),
                "weighted_score": weighted_score,
                "indicator_codes": "|".join(indicator_codes),
            }
        )
    return sorted(output, key=lambda row: (-row["weighted_score"], row["subject_id"]))


def build_rollups(
    indicator_results: list[dict[str, Any]],
    tenders: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    supplier_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    tender_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for rec in indicator_results:
        for supplier_id in _supplier_ids_from_record(rec):
            supplier_bucket[supplier_id].append(rec)
        for tender_id in _tender_ids_from_record(rec):
            tender_bucket[tender_id].append(rec)

    supplier_summary = _summarize(supplier_bucket)
    tender_summary = _summarize(tender_bucket)

    tender_to_entity = {row["tender_id"]: row["entity_id"] for row in tenders}
    entity_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec in indicator_results:
        entity_ids = {
            tender_to_entity[tender_id] for tender_id in _tender_ids_from_record(rec) if tender_to_entity.get(tender_id)
        }
        for entity_id in entity_ids:
            entity_bucket[entity_id].append(rec)

    entity_summary = _summarize(entity_bucket)
    return supplier_summary, tender_summary, entity_summary
