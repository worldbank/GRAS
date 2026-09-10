"""Generic normalization and CSV helpers."""

from __future__ import annotations

import csv
import json
import re
from datetime import date, datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any

import yaml

from gras.data_contract import validate_header

PROFILE_REQUIRED_KEYS = {
    "profile_version",
    "single_bidder_min_awards",
    "single_bidder_ratio_medium",
    "single_bidder_ratio_high",
    "top_loser_min_participations",
    "top_loser_success_medium",
    "top_loser_success_high",
    "top_loser_winner_min_links",
    "coaward_min_events_together",
    "coaward_rate_medium",
    "coaward_rate_high",
    "association_min_support",
    "association_min_confidence",
    "group_min_recurrence",
    "group_exclusivity_high",
    "group_turn_taking_cv",
    "group_dominance_share",
    "influence_baseline_max",
    "influence_conditional_min",
    "influence_gap_min",
    "network_min_pf_count",
    "network_min_pf_share",
    "repeated_address_min_suppliers",
    "repeated_address_min_events",
    "employee_bidder_min_participations",
}

PROBABILITY_PROFILE_KEYS = {
    "single_bidder_ratio_medium",
    "single_bidder_ratio_high",
    "top_loser_success_medium",
    "top_loser_success_high",
    "coaward_rate_medium",
    "coaward_rate_high",
    "association_min_support",
    "association_min_confidence",
    "group_exclusivity_high",
    "group_turn_taking_cv",
    "group_dominance_share",
    "influence_baseline_max",
    "influence_conditional_min",
    "influence_gap_min",
    "network_min_pf_share",
}

POSITIVE_INTEGER_PROFILE_KEYS = {
    "single_bidder_min_awards",
    "top_loser_min_participations",
    "top_loser_winner_min_links",
    "coaward_min_events_together",
    "group_min_recurrence",
    "network_min_pf_count",
    "repeated_address_min_suppliers",
    "repeated_address_min_events",
    "employee_bidder_min_participations",
}


def _validate_profile(profile_name: str, profile: dict[str, Any]) -> None:
    for key in sorted(PROBABILITY_PROFILE_KEYS):
        value = profile[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"Profile '{profile_name}' parameter {key} must be between 0 and 1")

    for key in sorted(POSITIVE_INTEGER_PROFILE_KEYS):
        value = profile[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"Profile '{profile_name}' parameter {key} must be a positive integer")

    if profile["single_bidder_ratio_high"] < profile["single_bidder_ratio_medium"]:
        raise ValueError(
            f"Profile '{profile_name}' parameter single_bidder_ratio_high must be greater than or equal to "
            "single_bidder_ratio_medium"
        )
    if profile["coaward_rate_high"] < profile["coaward_rate_medium"]:
        raise ValueError(
            f"Profile '{profile_name}' parameter coaward_rate_high must be greater than or equal to coaward_rate_medium"
        )
    if profile["top_loser_success_high"] > profile["top_loser_success_medium"]:
        raise ValueError(
            f"Profile '{profile_name}' parameter top_loser_success_high must be less than or equal to "
            "top_loser_success_medium"
        )


def read_csv_records(
    path: str, required_columns: list[str] | None = None, *, allow_empty: bool = True
) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if required_columns is not None:
            validate_header(reader.fieldnames or [], required_columns)
        rows = [dict(row) for row in reader]
        if not rows and not allow_empty:
            raise ValueError(f"Input table is empty: {Path(path).name}")
        return rows


def write_csv_records(path: str, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "t", "yes", "y"}


def parse_float(value: Any) -> float:
    text = "" if value is None else str(value).strip()
    if not text:
        return 0.0
    if not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", text):
        raise ValueError(
            "Invalid numeric input: use decimal point, optional exponent, and no currency/group separators"
        )
    number = float(text)
    if not isfinite(number):
        raise ValueError("Invalid numeric input: value must be finite")
    return number


def parse_int(value: Any) -> int:
    number = parse_float(value)
    if not number.is_integer():
        raise ValueError("Invalid integer input: fractional counts are not accepted")
    return int(number)


def parse_date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    candidates = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in candidates:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def normalize_id(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "").strip())


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def normalize_address(value: Any) -> str:
    text = normalize_text(value).upper()
    text = re.sub(r"[^A-Z0-9 ]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def now_iso_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def json_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=True)


def level_to_weight(level: str) -> int:
    mapping = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    return mapping.get(level, 0)


def normalize_tenders(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        tender_id = normalize_id(row.get("tender_id"))
        entity_id = normalize_id(row.get("entity_id"))
        if not tender_id or not entity_id:
            continue
        normalized.append(
            {
                "tender_id": tender_id,
                "entity_id": entity_id,
                "modality": normalize_text(row.get("modality")),
                "publication_date": parse_date(row.get("publication_date")),
                "participant_count": parse_int(row.get("participant_count")),
            }
        )
    return normalized


def normalize_bids(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        tender_id = normalize_id(row.get("tender_id"))
        bidder_id = normalize_id(row.get("bidder_id"))
        if not tender_id or not bidder_id:
            continue
        normalized.append(
            {
                "bid_id": normalize_id(row.get("bid_id")),
                "tender_id": tender_id,
                "bidder_id": bidder_id,
                "bidder_name": normalize_text(row.get("bidder_name")),
                "awarded_flag": parse_bool(row.get("awarded_flag")),
                "awarded_value": parse_float(row.get("awarded_value")),
                "submission_date": parse_date(row.get("submission_date")),
                "fiscal_address": normalize_address(row.get("fiscal_address")),
            }
        )
    return normalized


def normalize_sanctions(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        bidder_id = normalize_id(row.get("bidder_id"))
        start = parse_date(row.get("sanction_start"))
        end = parse_date(row.get("sanction_end"))
        if not bidder_id or start is None or end is None or start > end:
            continue
        normalized.append(
            {
                "bidder_id": bidder_id,
                "sanction_start": start,
                "sanction_end": end,
                "sanction_type": normalize_text(row.get("sanction_type")),
            }
        )
    return normalized


def normalize_employment(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        person_id = normalize_id(row.get("person_id"))
        if not person_id:
            continue
        normalized.append(
            {
                "person_id": person_id,
                "employer_name": normalize_text(row.get("employer_name")),
                "role_name": normalize_text(row.get("role_name")),
                "entry_date": parse_date(row.get("entry_date")),
                "salary": parse_float(row.get("salary")),
            }
        )
    return normalized


def load_profile(path: str | None = None, profile_name: str = "balanced") -> dict[str, Any]:
    profile_path = Path(path) if path else Path(__file__).parents[1] / "config" / "parameter_profiles.yaml"
    if not profile_path.is_file():
        raise FileNotFoundError(f"Profile file not found: {profile_path}")

    try:
        with profile_path.open(encoding="utf-8") as profile_file:
            parsed = yaml.safe_load(profile_file) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in profile file: {profile_path}") from exc

    if not isinstance(parsed, dict):
        raise ValueError(f"Profile file must contain a mapping: {profile_path}")
    if profile_name not in parsed:
        available = ", ".join(sorted(str(name) for name in parsed)) or "none"
        raise ValueError(f"Unknown profile '{profile_name}'. Available profiles: {available}")

    raw_profile = parsed[profile_name]
    if not isinstance(raw_profile, dict):
        raise ValueError(f"Profile '{profile_name}' must contain a mapping")

    missing = sorted(PROFILE_REQUIRED_KEYS - raw_profile.keys())
    if missing:
        raise ValueError(f"Profile '{profile_name}' is missing required parameters: {', '.join(missing)}")

    profile = dict(raw_profile)
    _validate_profile(profile_name, profile)
    profile["profile_name"] = profile_name
    return profile


def make_indicator_record(
    *,
    code: str,
    name: str,
    subject_type: str,
    subject_id: str,
    risk_level: str,
    risk_score: float,
    evidence: dict[str, Any],
    run_timestamp: str,
) -> dict[str, Any]:
    return {
        "indicator_code": code,
        "indicator_name": name,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "risk_level": risk_level,
        "risk_score": round(risk_score, 2),
        "evidence_json": json_dumps(evidence),
        "run_timestamp": run_timestamp,
    }
