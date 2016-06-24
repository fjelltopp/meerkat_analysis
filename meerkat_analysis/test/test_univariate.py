import unittest
import pandas as pd

from meerkat_analysis import univariate, util


class UnivariateTest(unittest.TestCase):
    """ Testing univariate"""

    def test_breakdown_by_cateogry(self):
        data = pd.read_csv("meerkat_analysis/test/test_data/univariate.csv")
        variables = util.Variables.from_json_file("meerkat_analysis/test/test_data/variables.json")

        breakdown = univariate.breakdown_by_category(variables, "gender", data)

        self.assertEqual(breakdown.loc["Male"]["value"], 4)
        self.assertEqual(breakdown.loc["Female"]["value"], 6)

        breakdown = univariate.breakdown_by_category(variables, "age",
                                                     data, use_names=False)
        self.assertEqual(breakdown.loc["age_1"]["value"], 1)
        self.assertEqual(breakdown.loc["age_6"]["value"], 3)
