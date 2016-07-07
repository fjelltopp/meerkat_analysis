import unittest
import pandas as pd
from datetime import datetime

from meerkat_analysis import indicators


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
        
    def test_fix_dates(self):
        start_date, end_date, freq = indicators.fix_dates("2016/4/3", "2016/4/9", 0)
        self.assertEqual(start_date, datetime(2016, 4, 3))
        self.assertEqual(end_date, datetime(2016, 4, 9))
        self.assertEqual(freq, "W-MON")

        start_date, end_date, freq = indicators.fix_dates(None, None, 3)
        self.assertEqual(start_date, datetime(datetime.now().year, 1, 1))
        now = datetime.now()
        self.assertEqual(end_date.year, now.year)
        self.assertEqual(end_date.month, now.month)
        self.assertEqual(end_date.day, now.day)
        self.assertEqual(freq, "W-THU")

        


    
    
