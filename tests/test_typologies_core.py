import unittest

from gras.common.normalization import now_iso_utc
from gras.typologies import coaward_pairs, single_bidder, top_loser


def _profile():
    return {
        "single_bidder_min_awards": 2,
        "single_bidder_ratio_medium": 0.5,
        "single_bidder_ratio_high": 0.75,
        "top_loser_min_participations": 3,
        "top_loser_success_medium": 0.60,
        "top_loser_success_high": 0.1,
        "coaward_min_events_together": 2,
        "coaward_rate_medium": 0.6,
        "coaward_rate_high": 0.8,
    }


def _bids():
    return [
        {"tender_id": "T1", "bidder_id": "S1", "awarded_flag": True, "awarded_value": 100, "fiscal_address": "A"},
        {"tender_id": "T2", "bidder_id": "S1", "awarded_flag": True, "awarded_value": 90, "fiscal_address": "A"},
        {"tender_id": "T2", "bidder_id": "S2", "awarded_flag": False, "awarded_value": 0, "fiscal_address": "B"},
        {"tender_id": "T3", "bidder_id": "S2", "awarded_flag": False, "awarded_value": 0, "fiscal_address": "B"},
        {"tender_id": "T3", "bidder_id": "S3", "awarded_flag": True, "awarded_value": 80, "fiscal_address": "C"},
        {"tender_id": "T4", "bidder_id": "S2", "awarded_flag": True, "awarded_value": 75, "fiscal_address": "B"},
        {"tender_id": "T4", "bidder_id": "S3", "awarded_flag": True, "awarded_value": 70, "fiscal_address": "C"},
        {"tender_id": "T5", "bidder_id": "S2", "awarded_flag": True, "awarded_value": 65, "fiscal_address": "B"},
        {"tender_id": "T5", "bidder_id": "S3", "awarded_flag": True, "awarded_value": 60, "fiscal_address": "C"},
    ]


class CoreTypologyTests(unittest.TestCase):
    def test_single_bidder_detects_concentration(self):
        rows = single_bidder.detect(_bids(), _profile(), now_iso_utc())
        self.assertTrue(any(r["subject_id"] == "S1" for r in rows))

    def test_top_loser_detects_low_success_actor(self):
        rows = top_loser.detect(_bids(), _profile(), now_iso_utc())
        self.assertTrue(any(r["subject_id"] == "S2" for r in rows))

    def test_coaward_pairs_detects_recurrence(self):
        rows = coaward_pairs.detect(_bids(), _profile(), now_iso_utc())
        self.assertTrue(any("S2|S3" in r["subject_id"] or "S3|S2" in r["subject_id"] for r in rows))

    def test_single_bidder_orders_high_risk_before_medium_risk(self):
        bids = [
            {"tender_id": "T1", "bidder_id": "S_HIGH", "awarded_flag": True, "awarded_value": 100},
            {"tender_id": "T2", "bidder_id": "S_HIGH", "awarded_flag": True, "awarded_value": 100},
            {"tender_id": "T3", "bidder_id": "S_MED", "awarded_flag": True, "awarded_value": 100},
            {"tender_id": "T4", "bidder_id": "S_MED", "awarded_flag": True, "awarded_value": 100},
            {"tender_id": "T4", "bidder_id": "OTHER", "awarded_flag": False, "awarded_value": 0},
        ]
        profile = {
            "single_bidder_min_awards": 2,
            "single_bidder_ratio_medium": 0.5,
            "single_bidder_ratio_high": 0.75,
        }

        rows = single_bidder.detect(bids, profile, "2026-01-01T00:00:00Z")

        self.assertEqual([row["subject_id"] for row in rows], ["S_HIGH", "S_MED"])

    def test_single_bidder_counts_distinct_awarded_tenders(self):
        bids = [
            {"tender_id": "T1", "bidder_id": "S1", "awarded_flag": True, "awarded_value": 100},
            {"tender_id": "T1", "bidder_id": "S1", "awarded_flag": True, "awarded_value": 100},
            {"tender_id": "T2", "bidder_id": "S1", "awarded_flag": True, "awarded_value": 100},
        ]
        profile = {
            "single_bidder_min_awards": 3,
            "single_bidder_ratio_medium": 0.5,
            "single_bidder_ratio_high": 0.75,
        }

        rows = single_bidder.detect(bids, profile, "2026-01-01T00:00:00Z")

        self.assertEqual(rows, [])

    def test_top_loser_orders_high_risk_before_medium_risk(self):
        bids = []
        for index in range(10):
            bids.append(
                {
                    "tender_id": f"H{index}",
                    "bidder_id": "S_HIGH",
                    "awarded_flag": False,
                    "awarded_value": 0,
                }
            )
            bids.append(
                {
                    "tender_id": f"M{index}",
                    "bidder_id": "S_MED",
                    "awarded_flag": index == 0,
                    "awarded_value": 100 if index == 0 else 0,
                }
            )
        profile = {
            "top_loser_min_participations": 10,
            "top_loser_success_medium": 0.2,
            "top_loser_success_high": 0.05,
        }

        rows = top_loser.detect(bids, profile, "2026-01-01T00:00:00Z")

        self.assertEqual([row["subject_id"] for row in rows], ["S_HIGH", "S_MED"])


if __name__ == "__main__":
    unittest.main()
