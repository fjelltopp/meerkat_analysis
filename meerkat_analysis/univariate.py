import pandas as pd
from statsmodels.stats import proportion
from matplotlib import pylab

from . import util

def breakdown_by_category(variables, category, data, use_names=True):
    """
    Gives a breakdown of data for category

    Args:
       variables: Variables class
       category: name of category
       data: structured data in pandas Data Frame
       use_names: return object used variable names instead of ids
    """
    if category in ["country", "region", "district", "clinic"]:
        return data[category].value_counts()

    if category not in variables.groups:
        raise KeyError("Category does not exists")

    results = pd.DataFrame(columns=["value"])
    ids = sorted(variables.groups[category])
    for number, i in enumerate(ids):
        if use_names:
            name = variables.name(i)
        else:
            name = i
        if i in data.columns:
            results.loc[name] = [data[i].sum()]
        else:
            results.loc[name] = [0]

    return results
    
def plot_timeline_by_category(variables, category, data, use_names=True, freq="W",
                              smooth=True, lw=1):
    """
    Gives a breakdown of data for category

    Args:
       variables: Variables class
       category: name of category
       data: structured data in pandas Data Frame
       use_names: return object used variable names instead of ids
    """
    if category in ["country", "region", "district", "clinic"]:
        return data[category].value_counts()

    if category not in variables.groups:
        raise KeyError("Category does not exists")

    results = pd.DataFrame(columns=["value"])
    ids = sorted(variables.groups[category])
    fig, ax = pylab.subplots()
    results = data.groupby(pd.Grouper(key="date", freq=freq)).sum()
    for number, i in enumerate(ids):
        if smooth:
            if freq in ["1D", "D"]:
                smooth_freq = "1H"
            else:
                smooth_freq = "1D"
            if i in results.columns:
                results[i].resample(smooth_freq).interpolate(method="cubic").plot(
                    label=variables.name(i), ax=ax, lw=lw)
        else:
            results[i].plot(label=variables.name(i), ax=ax, lw=lw)
    pylab.legend(loc="best")
    return ax

def incidence_rate(data, population=None, var_id=None, name=None, variables=None, alpha=0.95):
    """
    Calculates the incidence rate and confidence interval for the variable specified either by id or name

    Args:
       data: data frame
       var_id: variable id
       name: name of variable
       variables: Variables class
    Returns:
       incedence rate, confidence interval
    """

    var_id = util.name_id(var_id=var_id, name=name, variables=variables)
    

    if var_id not in data.columns:
        return (0, (0,0))
    count = data[var_id].sum()
    
    if population is None:
        population = len(data)
    incidence = count / population

    confidence_interval = proportion.proportion_confint(count, population, method="wilson")
    return (incidence, confidence_interval)

