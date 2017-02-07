import unittest
import pandas as pd
from datetime import datetime, timedelta

from meerkat_analysis import indicators, util


class IndicatorTest(unittest.TestCase):
    """ Testing Indicator Calculations"""

    def test_count(self):
        data = pd.read_csv("meerkat_analysis/test/test_data/univariate.csv", parse_dates=["date"]).fillna(0)

        total, timeline = indicators.count(data, "gen_2",
                                           epi_week_start_day=0,
                                           start_date="2016/1/1",
                                           end_date="2016/12/31")
        self.assertEqual(total, 6)
        self.assertEqual(timeline["2016/06/20"], 5)
        self.assertTrue(
            timeline.index.equals(
                pd.date_range("2016/1/1", "2016/12/31", freq="W-MON")))
    def test_count_over_count(self):
        data = pd.read_csv("meerkat_analysis/test/test_data/univariate.csv", parse_dates=["date"]).fillna(0)

        proportion, timeline = indicators.count_over_count(data, "gen_2", "tot_1",
                                           epi_week_start_day=0,
                                           start_date="2016/1/1",
                                           end_date="2016/12/31")
        self.assertEqual(proportion, 0.6)
        self.assertEqual(timeline["2016/06/13"], 0.2)
        self.assertEqual(timeline["2016/06/20"], 1)
        self.assertTrue(
            timeline.index.equals(
                pd.date_range("2016/1/1", "2016/12/31", freq="W-MON")))

    def test_number_per_week_clinic(self):
        data = pd.read_csv("meerkat_analysis/test/test_data/univariate.csv", parse_dates=["date"]).fillna(0)
        locations = util.Locations.from_json_file("meerkat_analysis/test/test_data/locations.json")
        clinics = indicators.number_per_week_clinic(data, "tot_1", locations, 
                                                    epi_week_start_day=0,
                                                    start_date="2016/1/1",
                                                    end_date="2016/12/31")

        self.assertEqual(list(clinics.index.get_level_values(0).unique()),
                         [7, 8, 10, 11])

        self.assertEqual(clinics.loc[7, "2016/06/13"], 1)
        self.assertEqual(clinics.loc[7, "2016/06/20"], 1)
        self.assertEqual(clinics.loc[7, "2016/06/27"], 0)
        self.assertEqual(clinics.loc[8, "2016/06/13"], 1)
        self.assertEqual(clinics.loc[8, "2016/06/20"], 1)
        self.assertEqual(clinics.loc[8, "2016/06/27"], 0)
        self.assertEqual(clinics.loc[10, "2016/06/13"], 1)
        self.assertEqual(clinics.loc[10, "2016/06/20"], 0)
        self.assertEqual(clinics.loc[10, "2016/06/27"], 0)
        self.assertEqual(clinics.loc[11, "2016/06/13"], 3)
        self.assertEqual(clinics.loc[11, "2016/06/20"], 2)
        self.assertEqual(clinics.loc[11, "2016/06/27"], 0)
        
    def test_clinic_to_level(self):
        data = pd.read_csv("meerkat_analysis/test/test_data/univariate.csv", parse_dates=["date"]).fillna(0)
        locations = util.Locations.from_json_file("meerkat_analysis/test/test_data/locations.json")
        clinics = indicators.number_per_week_clinic(data, "tot_1", locations, 
                                                    epi_week_start_day=0,
                                                    start_date="2016/1/1",
                                                    end_date="2016/12/31")

        regions = indicators.clinic_to_level(clinics, locations, "region", 2)

        self.assertEqual(sorted(list(regions.index.get_level_values(0).unique())),
                         ["Region 1", "Region 2"])
        self.assertEqual(regions.loc["Region 1", "2016/06/13"], 1)
        self.assertEqual(regions.loc["Region 1", "2016/06/20"], 2/3)
        self.assertEqual(regions.loc["Region 1", "2016/06/6"], 0)
        self.assertEqual(regions.loc["Region 2", "2016/06/13"], 2)
        self.assertEqual(regions.loc["Region 2", "2016/06/20"], 2)
        self.assertEqual(regions.loc["Region 2", "2016/06/6"], 0)
    def test_number_of_sites(self):
        data = pd.read_csv("meerkat_analysis/test/test_data/univariate.csv", parse_dates=["date"]).fillna(0)

        total, timeline = indicators.number_of_sites(data, "clinic",
                                           epi_week_start_day=0,
                                           start_date="2016/1/1",
                                           end_date="2016/12/31")
        self.assertEqual(total, 4)
        self.assertEqual(timeline["2016/06/20"], 3)
        self.assertTrue(
            timeline.index.equals(
                pd.date_range("2016/1/1", "2016/12/31", freq="W-MON")))  
    
    def test_fix_dates(self):
        start_date, end_date, freq = indicators.fix_dates("2016/4/3", "2016/5/9", 0)
        self.assertEqual(start_date, datetime(2016, 4, 3))
        self.assertEqual(end_date, datetime(2016, 5, 9))
        self.assertEqual(freq, "W-MON")

        start_date, end_date, freq = indicators.fix_dates(None, None, 3)
        self.assertEqual(start_date, datetime(datetime.now().year, 1, 1))
        now = datetime.now()
        wd = now.weekday()

        offset = wd - 2

        if offset < 0:
            offset = 7 + offset

        expected_end_date = now - timedelta(days=offset)
        
        self.assertEqual(end_date.year, expected_end_date.year)
        self.assertEqual(end_date.month, expected_end_date.month)
        self.assertEqual(end_date.day, expected_end_date.day)
        self.assertEqual(freq, "W-THU")

        


    
    
