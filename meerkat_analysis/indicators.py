import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil import parser
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

    if start_date:
        start_date = parser.parse(start_date).replace(tzinfo=None)
    else:
        start_date = datetime.now().replace(month=1, day=1,
                                      hour=0, second=0,
                                      minute=0,
                                      microsecond=0)

    if epi_week_start_day is None:
        epi_week_start_day = start_date.weekday()
    if end_date:
        end_date  = parser.parse(end_date).replace(tzinfo=None)
    else:
        end_date = datetime.now()
        offset = end_date.weekday() - epi_week_start_day
        if offset < 0:
            offset = 7 + offset
        end_date = end_date - timedelta(days=offset + 1)

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
    #rowtotal=data.shape[0]
    #mean=total/rowtotal
    #mean=data[var_id].mean().mean()
    #mean=data[var_id].values.std(ddof=1)
    mean=data[var_id].mean()
    std_dev=data[var_id].std()
    timeline = data.groupby(
        pd.TimeGrouper(key="date", freq=freq, label="left", closed="left")).sum()[var_id]
    timeline = timeline.reindex(dates).fillna(0)
    return (total, timeline,mean,std_dev)

def count_over_count(data, numerator_id, denominator_id, start_date=None, end_date=None, epi_week_start_day=None, restrict=False):
    """
    We return the total proportion of numerator_id over denominator_id and a timeline by epi_week

    Args:
        data: data in dataframe
        denominator: the denominator id
        numerator: the numerator_id
        start_date: start date
        end_date: end_date
        epi_week_start_day: what day of the week to start the timeline(Mon=0)
        restrict: if true only data rows with denominator counts for numerator
    Returns:
       (total, timeline): a total and weekly timeline

    """

    if restrict:
        data = data[data[restrict] == 1]
    data = data[["date", numerator_id, denominator_id]]
    data = data[data[denominator_id] == 1]
    if data[denominator_id].sum() == 0:
        proportion = 0
    else:
        proportion = data[numerator_id].sum() / data[denominator_id].sum()
#        ci = proportion.proportion_confint(data[numerator_id].sum(), data[denominator_id].sum(), method="wilson")
    start_date, end_date, freq = fix_dates(start_date,
                                           end_date,
                                           epi_week_start_day)

    dates = pd.date_range(start_date, end_date, freq=freq, closed="left")
    data = data[data["date"] >= start_date]
    data = data[data["date"] <= end_date]
    timeline = data.groupby(
        pd.TimeGrouper(key="date", freq=freq, label="left", closed="left")).sum()
    timeline = timeline.reindex(dates).fillna(0)
    timeline.loc[timeline[denominator_id] == 0, denominator_id] = 1
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
        if locs[str(clinic)]["case_report"]:
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


def number_of_sites(data, level, start_date=None, end_date=None,
                           epi_week_start_day=None):
    start_date, end_date, freq = fix_dates(start_date,
                                           end_date,
                                           epi_week_start_day)

    dates = pd.date_range(start_date, end_date, freq=freq, closed="left")

    data = data[data["date"] >= start_date]
    data = data[data["date"] <= end_date]
    total = data[level].nunique()
    timeline = data.groupby(
        pd.TimeGrouper(
            key="date", freq=freq,
            label="left", closed="left")).agg({level: pd.Series.nunique})[level]
    timeline = timeline.reindex(dates).fillna(0)
    return (total, timeline)


def grouped_count_over_count(data, numerator, denominator, restrict=False,
                             group_by="clinic", start_date=None, end_date=None,
                             epi_week_start_day=None,
                             fields=["region", "district", "clinic_type"]):
    """
    Returns the total count_over_count indicators per group_by, with fields.
    Args:
        data: data in dataframe
        denominator: the denominator id
        numerator: the numerator_id
        start_date: start date
        end_date: end_date
        epi_week_start_day: what day of the week to start the timeline(Mon=0)
        restrict: if true only data rows with denominator counts for numerator
    Returns:
       dataframe: With a row for each group by
    """

    clinics = pd.DataFrame(columns=["score", "N"] + fields, index=[group_by])
    for name, group in data.groupby(group_by):
        if np.sum(group[denominator]) > 0:
            row = [
                count_over_count(group, numerator, denominator,
                                 start_date=start_date, end_date=end_date,
                                 epi_week_start_day=epi_week_start_day,
                                 restrict=restrict)[0],
                np.sum(group[denominator])
            ]
            for f in fields:
                row.append(group[f][group.index[0]])
            clinics.loc[name] = row
    return clinics


def plot_level_total(data, locations, level,  cutoff_per_week=None):
    """
    Transform clinic data to data on a higher level and plots it

    Args:
       data: Data Frame with clinic data
       locations: Location class
       level: district, region or country
       cutoff_per_week: a cut off
    """

    total = data.groupby(level=1).mean() / cutoff_per_week * 100
    fig, ax = pylab.subplots()
    sublevels = clinic_to_level(data, locations, level, cutoff_per_week)

    for label in sublevels.index.levels[0]:
        t = sublevels.loc[label, :]
        if len(t) > 0:
            t.index = t.index.droplevel(level=0)
            t = t / cutoff_per_week * 100
            t.plot(label=label, color="black", alpha=0.4)
    total.plot(label="Country", lw=5)
    axis = pylab.axis()
    x = [axis[0], axis[1]]
    green_upper = [100, 100]
    green_lower = [80, 80]
    ax.fill_between(x, green_upper, green_lower, facecolor="green", alpha=0.5)
    orange_upper= [80, 80]
    orange_lower = [40, 40]
    ax.fill_between(x, orange_upper, orange_lower, facecolor="yellow", alpha=0.5)
    red_upper = [40, 40]
    red_lower = [-10, -10]
    ax.fill_between(x, red_upper, red_lower, facecolor="red", alpha=0.5)




def plot_multilevel_timeline(data):
    """
    Plots multilevel timeline

    Args:
       data: data to plot
    """
    f = pylab.figure()
    for label in data.index.levels[0]:
        t = data.loc[label, :]
        if len(t) > 0:
            t.index = t.index.droplevel(level=0)
            t.plot(label=label)
    pylab.legend(loc="best")
    #return f
