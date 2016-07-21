import pandas as pd
from datetime import datetime
from dateutil import parser
from statsmodels.stats import proportion
from matplotlib import pylab

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


def number_per_week_clinic(data, variable, locations,
                           start_date=None, end_date=None,
                           epi_week_start_day=None,
                           drop_duplicates=True):
    """
    Returns the number of variable per week taking start_date into account
    Args: 
        data: data in dataframe
        var_id: the variable id to count
        locations: location class
        start_date: start date
        end_date: end_date
        epi_week_start_day: what day of the week to start the timeline(Mon=0)
    Returns:
       clinic_timeline: all clinics with a timeline
    """

    
    today = datetime.now()
    locs = locations.locations
    start_date, end_date, freq = fix_dates(start_date,
                                           end_date,
                                           epi_week_start_day)
    
    # We drop duplicates so each clinic can only have one record per day
    if drop_duplicates:
        data = data.drop_duplicates(subset=["region", "district", "clinic", "date", variable])
    # We first create an index with sublevel, clinic, dates
    # Where dates are the dates after the clinic started reporting
    clinics = []
    begining = start_date
    tuples = []
    for l in locs.values():
        if l["level"] == "clinic":
            clinics.append(l["id"])
    for clinic in clinics:
        start_date_clinic = parser.parse(locs[str(clinic)]["start_date"])
        if start_date_clinic < begining:
            start_date_clinic = begining
        for d in pd.date_range(start_date_clinic, end_date, freq=freq):
            tuples.append((clinic, d))

    new_index = pd.MultiIndex.from_tuples(tuples,
                                          names=["clinic", "date"])

    completeness = data.groupby(
        ["clinic",
         pd.TimeGrouper(key="date", freq=freq, label="left")]
    ).sum().reindex(new_index)[variable].fillna(0).sort_index()
    return completeness


def clinic_to_level(data, locations, level, cutoff_per_week=None):
    """
    Transform clinic data to data on a higher level

    Args: 
       data: Data Frame with clinic data
       locations: Location class
       level: district, region or country
       cutoff_per_week: a cut off
    Returns:
       Timelines for new level
    """
    top_locations = locations.get_level(level)
    if cutoff_per_week:
        data[data > cutoff_per_week] = cutoff_per_week
    ret = data.copy()
    org = data.index.get_level_values(level=0)
    #pd.DataFrame(columns=[level, "date", "value"], index=[level, "date"])
    for tl in top_locations:
        clinics = tuple([ int(l) for l in locations.get_clinics(tl)])
        loc_data = data.loc[data.index.get_level_values(level=0).isin(clinics)].groupby(level=1).mean()
        for d in loc_data.index:
            ret.loc[(locations.name(tl), d)] = loc_data.loc[d]
    return ret[~ret.index.get_level_values(level=0).isin(org)]
        
def plot_multilevel_timeline(data):
    """
    Plots multilevel timeline

    Args: 
       data: data to plot
       smooth: if we should smooth the data
    """
    f = pylab.figure()
    for label in data.index.levels[0]:
        t = data.loc[label, :]
        if len(t) > 0:
            t.index = t.index.droplevel(level=0)
            t.plot(label=label)
    pylab.legend(loc="best")
    #return f
