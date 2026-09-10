import json
import unittest

from gras.aggregations.risk_rollup import build_rollups


class RollupTests(unittest.TestCase):
    def test_rollups_generate_subject_summaries(self):
        indicators = [
            {
                "indicator_code": "IND001_SINGLE_BIDDER",
                "indicator_name": "Single Bidder Concentration",
                "subject_type": "supplier",
                "subject_id": "S1",
                "risk_level": "HIGH",
                "risk_score": 90,
                "evidence_json": '{"tender_ids": ["T1"]}',
                "run_timestamp": "2026-01-01T00:00:00Z",
            },
            {
                "indicator_code": "IND011_REPEATED_FISCAL_ADDRESS",
                "indicator_name": "Repeated Fiscal Address",
                "subject_type": "tender",
                "subject_id": "T1",
                "risk_level": "MEDIUM",
                "risk_score": 70,
                "evidence_json": '{"tender_ids": ["T1"]}',
                "run_timestamp": "2026-01-01T00:00:00Z",
            },
        ]
        tenders = [{"tender_id": "T1", "entity_id": "E1"}]

        supplier, tender, entity = build_rollups(indicators, tenders)

        self.assertTrue(any(row["subject_id"] == "S1" for row in supplier))
        self.assertTrue(any(row["subject_id"] == "T1" for row in tender))
        self.assertTrue(any(row["subject_id"] == "E1" for row in entity))

    def test_network_component_contributes_to_linked_subjects_once(self):
        indicators = [
            {
                "indicator_code": "IND008_EVENT_CENTRIC_NETWORK",
                "indicator_name": "Event-Centric Suspicious Network",
                "subject_type": "network_component",
                "subject_id": "component_1",
                "risk_level": "HIGH",
                "risk_score": 90,
                "evidence_json": json.dumps(
                    {
                        "event_ids": ["T1", "T2"],
                        "supplier_ids": ["S1", "S2"],
                    }
                ),
                "run_timestamp": "2026-01-01T00:00:00Z",
            }
        ]
        tenders = [
            {"tender_id": "T1", "entity_id": "E1"},
            {"tender_id": "T2", "entity_id": "E1"},
        ]

        supplier, tender, entity = build_rollups(indicators, tenders)

        self.assertEqual([row["subject_id"] for row in supplier], ["S1", "S2"])
        self.assertEqual([row["subject_id"] for row in tender], ["T1", "T2"])
        self.assertEqual(entity[0]["subject_id"], "E1")
        self.assertEqual(entity[0]["indicator_count"], 1)

    def test_summaries_are_sorted_by_weighted_score_descending(self):
        indicators = [
            {
                "indicator_code": "IND001_SINGLE_BIDDER",
                "indicator_name": "Single Bidder Concentration",
                "subject_type": "supplier",
                "subject_id": "S1",
                "risk_level": "LOW",
                "risk_score": 10,
                "evidence_json": "{}",
                "run_timestamp": "2026-01-01T00:00:00Z",
            },
            {
                "indicator_code": "IND002_TOP_LOSER",
                "indicator_name": "Top Loser",
                "subject_type": "supplier",
                "subject_id": "S2",
                "risk_level": "HIGH",
                "risk_score": 90,
                "evidence_json": "{}",
                "run_timestamp": "2026-01-01T00:00:00Z",
            },
        ]

        supplier, _, _ = build_rollups(indicators, [])

        self.assertEqual([row["subject_id"] for row in supplier], ["S2", "S1"])


if __name__ == "__main__":
    unittest.main()
