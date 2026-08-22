import unittest

from fund_ranking import Fund, RankingConfig, percentile_score, rank_universe


def fund(name, category="Flexi Cap", **overrides):
    values = {
        "name": name,
        "category": category,
        "plan_type": "Direct Growth",
        "geography": "India",
        "fund_house_aum_crore": 50_000,
        "track_record_years": 8,
        "rolling_return": 12,
        "sharpe_ratio": 0.8,
    }
    values.update(overrides)
    return Fund(**values)


class RankingTests(unittest.TestCase):
    def test_percentile_scores_use_midrank_for_ties(self):
        self.assertEqual(percentile_score(10, [10, 10, 20]), 25)
        self.assertEqual(percentile_score(20, [10, 10, 20]), 100)

    def test_ineligible_funds_are_excluded_with_all_reasons(self):
        candidate = fund(
            "Short History",
            fund_house_aum_crore=20_000,
            track_record_years=2,
            rolling_return=None,
        )
        ranked, exclusions = rank_universe([candidate])
        self.assertEqual(ranked, [])
        self.assertEqual(
            exclusions[candidate.name],
            (
                "fund-house AUM below minimum",
                "track record below minimum",
                "missing rolling return",
            ),
        )

    def test_categories_are_normalized_independently(self):
        funds = [
            fund("Flexi Leader", rolling_return=12, sharpe_ratio=0.8),
            fund("Midcap Leader", category="Mid Cap", rolling_return=20, sharpe_ratio=1.0),
        ]
        ranked, _ = rank_universe(funds)
        self.assertEqual([item.final_score for item in ranked], [100, 100])
        self.assertEqual([item.rank for item in ranked], [1, 1])

    def test_weighted_score_controls_ranking(self):
        funds = [
            fund("Return Leader", rolling_return=20, sharpe_ratio=0.5),
            fund("Risk Leader", rolling_return=10, sharpe_ratio=1.0),
        ]
        ranked, _ = rank_universe(funds)
        self.assertEqual(ranked[0].fund.name, "Return Leader")
        self.assertEqual(ranked[0].final_score, 80)
        self.assertEqual(ranked[1].final_score, 20)

    def test_invalid_weights_fail_fast(self):
        with self.assertRaises(ValueError):
            RankingConfig(rolling_weight=0.7, sharpe_weight=0.2)


if __name__ == "__main__":
    unittest.main()
