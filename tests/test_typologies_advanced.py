import json
import unittest
from datetime import date

from gras.common.normalization import now_iso_utc
from gras.typologies import (
    conditional_influence,
    public_employee_bidder,
    repeated_fiscal_address,
    sanction_overlap,
)


def _profile():
    return {
        "influence_baseline_max": 0.5,
        "influence_conditional_min": 0.5,
        "influence_gap_min": 0.1,
        "employee_bidder_min_participations": 1,
        "repeated_address_min_suppliers": 2,
        "repeated_address_min_events": 1,
    }


def _bids():
    return [
        {
            "tender_id": "T1",
            "bidder_id": "A",
            "awarded_flag": True,
            "awarded_value": 100,
            "submission_date": date(2024, 1, 10),
            "fiscal_address": "ADDR X",
        },
        {
            "tender_id": "T1",
            "bidder_id": "B",
            "awarded_flag": False,
            "awarded_value": 0,
            "submission_date": date(2024, 1, 10),
            "fiscal_address": "ADDR Y",
        },
        {
            "tender_id": "T2",
            "bidder_id": "A",
            "awarded_flag": True,
            "awarded_value": 110,
            "submission_date": date(2024, 1, 11),
            "fiscal_address": "ADDR Z",
        },
        {
            "tender_id": "T2",
            "bidder_id": "B",
            "awarded_flag": False,
            "awarded_value": 0,
            "submission_date": date(2024, 1, 11),
            "fiscal_address": "ADDR Y",
        },
        {
            "tender_id": "T3",
            "bidder_id": "C",
            "awarded_flag": True,
            "awarded_value": 150,
            "submission_date": date(2024, 1, 12),
            "fiscal_address": "ADDR SHARED",
        },
        {
            "tender_id": "T3",
            "bidder_id": "D",
            "awarded_flag": False,
            "awarded_value": 0,
            "submission_date": date(2024, 1, 12),
            "fiscal_address": "ADDR SHARED",
        },
    ]


class AdvancedTypologyTests(unittest.TestCase):
    def test_conditional_influence_generates_records(self):
        rows = conditional_influence.detect(_bids(), _profile(), now_iso_utc())
        self.assertIsInstance(rows, list)

    def test_sanction_overlap_detects_overlap(self):
        sanctions = [
            {
                "bidder_id": "A",
                "sanction_start": date(2024, 1, 1),
                "sanction_end": date(2024, 1, 31),
                "sanction_type": "type",
            }
        ]
        rows = sanction_overlap.detect(_bids(), sanctions, now_iso_utc())
        self.assertTrue(any(r["subject_id"] == "A" for r in rows))

    def test_employee_bidder_detects_overlap(self):
        employment = [
            {
                "person_id": "A",
                "employer_name": "Org",
                "role_name": "Role",
                "entry_date": date(2020, 1, 1),
                "salary": 1000.0,
            }
        ]
        rows = public_employee_bidder.detect(_bids(), employment, _profile(), now_iso_utc())
        self.assertTrue(any(r["subject_id"] == "A" for r in rows))

    def test_employee_bidder_counts_distinct_winning_tenders(self):
        bids = [
            {
                "tender_id": "T1",
                "bidder_id": "A",
                "awarded_flag": True,
                "awarded_value": 50,
            },
            {
                "tender_id": "T1",
                "bidder_id": "A",
                "awarded_flag": True,
                "awarded_value": 50,
            },
        ]
        employment = [
            {
                "person_id": "A",
                "employer_name": "Org",
                "role_name": "Role",
            }
        ]

        rows = public_employee_bidder.detect(bids, employment, _profile(), now_iso_utc())

        evidence = json.loads(rows[0]["evidence_json"])
        self.assertEqual(evidence["wins"], 1)
        self.assertEqual(rows[0]["risk_level"], "MEDIUM")

    def test_repeated_address_detects_event(self):
        rows = repeated_fiscal_address.detect(_bids(), _profile(), now_iso_utc())
        self.assertTrue(any(r["subject_id"] == "T3" for r in rows))


if __name__ == "__main__":
    unittest.main()
