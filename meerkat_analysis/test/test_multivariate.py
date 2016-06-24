import unittest
import pandas as pd

from meerkat_analysis import multivariate, util


class MultivariateTest(unittest.TestCase):
    """ Testing univariate"""

    def test_cross_table(self):
        data = pd.read_csv("meerkat_analysis/test/test_data/univariate.csv")
        variables = util.Variables.from_json_file("meerkat_analysis/test/test_data/variables.json")

        cross_table= multivariate.cross_table(variables, "age", "gender", data)
        
        self.assertEqual(cross_table["<5"]["Female"], 0)
        self.assertEqual(cross_table["<5"]["Male"], 1)

        self.assertEqual(cross_table[">60"]["Female"], 3)
        self.assertEqual(cross_table[">60"]["Male"], 0)
