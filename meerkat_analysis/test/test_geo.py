import unittest
import pandas as pd
from statsmodels.stats import proportion

from meerkat_analysis import util
from meerkat_analysis import geo

class GeoTest(unittest.TestCase):
    """ Testing geo methods"""

    def test_incidence_rate_by_location(self):
        data = pd.read_csv("meerkat_analysis/test/test_data/univariate.csv")
        locations = util.Locations.from_json_file(
            "meerkat_analysis/test/test_data/locations.json")
        rates = geo.incidence_rate_by_location(data,
                                               locations,
                                               "gen_1",
                                               level="clinic").fillna(0)
        
        self.assertEqual(rates.loc["Clinic 1"]["incidence_rate"], 1 / 1500)
        self.assertEqual(rates.loc["Clinic 2"]["incidence_rate"], 1 / 1000)
        self.assertEqual(rates.loc["Clinic 4"]["incidence_rate"], 0)
        self.assertEqual(rates.loc["Clinic 5"]["incidence_rate"], 2 / 2000)

        ci = (rates.loc["Clinic 1"]["incidence_rate"] - rates.loc["Clinic 1"]["ci_lower"],
              rates.loc["Clinic 1"]["incidence_rate"] + rates.loc["Clinic 1"]["ci_upper"])
        
        self.assertEqual(ci,
                         proportion.proportion_confint(1, 1500, method="wilson"))
        rates = geo.incidence_rate_by_location(data,
                                               locations,
                                               "gen_1",
                                               level="district").fillna(0)
        self.assertEqual(rates.loc["District 1"]["incidence_rate"], 2 / 2500)
        self.assertEqual(rates.loc["District 2"]["incidence_rate"], 0 )
        self.assertEqual(rates.loc["District 3"]["incidence_rate"], 2 / 2000)

        rates = geo.incidence_rate_by_location(data,
                                               locations,
                                               "gen_1",
                                               level="region").fillna(0)
        self.assertEqual(rates.loc["Region 1"]["incidence_rate"], 2 / 6500)
        self.assertEqual(rates.loc["Region 2"]["incidence_rate"], 2 / 2000 )
