import pandas as pd
from datetime import datetime
from dateutil import parser
from statsmodels.stats import proportion

def fix_dates(start_date, end_date, epi_week_start_day):
    """
    We parse the start and end date and remove any timezone information

    Args: 
       start_date: start date
       end_date: end_date
       epi_week_start_day: what day of the week to start the timeline(Mon=0)
    Returns:
       dates(tuple): (start_date, end_date, freq)
    """
    if end_date:
        end_date  = parser.parse(end_date).replace(tzinfo=None)
    else:
        end_date = datetime.now()
    if start_date:
        start_date = parser.parse(start_date).replace(tzinfo=None)
    else:
        start_date = end_date.replace(month=1, day=1,
                                      hour=0, second=0,
                                      minute=0,
                                      microsecond=0)
    if epi_week_start_day is None:
        epi_week_start_day = start_date.weekday()
    freqs = ["W-MON", "W-TUE", "W-WED", "W-THU", "W-FRI", "W-SAT", "W-SUN"]
    freq = freqs[epi_week_start_day]

    return start_date, end_date, freq


def count(data, var_id, start_date=None, end_date=None, epi_week_start_day=None):
    """
    We return the total count of var_id and a timeline by epi_week

    Args: 
        data: data in dataframe
        var_id: the variable id to count
        start_date: start date
        end_date: end_date
        epi_week_start_day: what day of the week to start the timeline(Mon=0)
    Returns:
       (total, timeline): a total and weekly timeline

    """
    start_date, end_date, freq = fix_dates(start_date,
                                           end_date,
                                           epi_week_start_day)
    
    dates = pd.date_range(start_date, end_date, freq=freq, closed="left")

    data = data[data["date"] >= start_date]
    data = data[data["date"] <= end_date]
    total = data[var_id].sum()
    timeline = data.groupby(
        pd.TimeGrouper(key="date", freq=freq, label="left", closed="left")).sum()[var_id]
    timeline = timeline.reindex(dates).fillna(0)
    return (total, timeline)
    
def count_over_count(data, numerator_id, denominator_id, start_date=None, end_date=None, epi_week_start_day=None):
    """
    We return the total proportion of numerator_id over denominator_id and a timeline by epi_week

    Args: 
        data: data in dataframe
        var_id: the variable id to count
        start_date: start date
        end_date: end_date
        epi_week_start_day: what day of the week to start the timeline(Mon=0)
    Returns:
       (total, timeline): a total and weekly timeline

    """
    start_date, end_date, freq = fix_dates(start_date,
                                           end_date,
                                           epi_week_start_day)
    
    dates = pd.date_range(start_date, end_date, freq=freq, closed="left")

    data = data[data["date"] >= start_date]
    data = data[data["date"] <= end_date]

    
    proportion = data[numerator_id].sum() / data[denominator_id].sum()
    #ci = proportion.proportion_confint(data[numerator_id].sum(), data[denominator_id].sum(), method="wilson")
    
    timeline = data.groupby(
        pd.TimeGrouper(key="date", freq=freq, label="left", closed="left")).sum()
    timeline = timeline.reindex(dates).fillna(0)

    proportion_timeline = timeline[numerator_id] / timeline[denominator_id]
    
    return (proportion, proportion_timeline)
