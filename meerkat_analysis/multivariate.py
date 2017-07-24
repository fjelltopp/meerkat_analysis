import pandas as pd
import numpy as np
from matplotlib import pylab
from textwrap import fill
from . import univariate

def cross_table(variables, category1, category2, data, use_names=True):
    """
    Gives a cross table of category1 and category2

    Args:
       variables: Variables class
       category1: name of category
       category2: name of category
       data: structured data in pandas Data Frame
       use_names: return object used variable names instead of ids
    """
    # if category in ["country", "region", "district", "clinic"]:
    #     return data[category].value_counts()

    if category1 not in variables.groups:
        raise KeyError("Category1 does not exists")
    if category2 not in variables.groups:
        raise KeyError("Category1 does not exists")

    ids1 = sorted(variables.groups[category1])
    ids2 = sorted(variables.groups[category2])
    if use_names:
        columns = [variables.name(i) for i in ids1]
    else:
        columns = ids1
    results = pd.DataFrame(columns=columns)

    for number, i2 in enumerate(ids2):
        if use_names:
            name = variables.name(i2)
        else:
            name = i2

        if i2 in data.columns:
            row = []
            for i1 in ids1:
                if i1 in data.columns:
                    row.append(data[data[i1] == 1][i2].sum())
                else:
                    row.append(0)
            results.loc[name] = row
        else:
            results.loc[name] = [0 for _ in ids1]
    return results.fillna(0)


def incidence_rate_by_category(data, category, variables, populations=None, var_id=None, name=None, exclude=[]):
    """
    Calculate the incidence rates for all the groups in cateogory based on var_id
    
    Args: 
        data: data frame with data
        category: name of cateogory
        variables: Variables object
        populations: list of populations to use, same length as number of variables in category
        var_id: variable_id
        name: name of variable
    """

    ret = pd.DataFrame(columns=["incidence_rate", "ci_lower", "ci_upper"])
    for group in variables.groups[category]:
        if group not in exclude:
            group_data = data[data[group] == 1]
            if populations:
                name = variables.name(group)
                if name in populations:
                    population = populations[name]
                elif group in populations:
                    population = populations[group]
                else:
                    print(name, group)
                    raise KeyError("Populations needs to include either variable id or name")
                incidence_rate = univariate.incidence_rate(group_data, population=population,
                                                       var_id=var_id, name=name, variables=variables)
            else:
                incidence_rate = univariate.incidence_rate(group_data, var_id=var_id, name=name, variables=variables)
            ret.loc[variables.name(group)] = [incidence_rate[0], incidence_rate[0]-incidence_rate[1][0], incidence_rate[1][1]-incidence_rate[0]]
    return ret


def incidence_rate_by_location(data, level, locations, variables, populations=None, var_id=None, name=None, exclude=[]):
    """
    Calculate the incidence rates for all the groups in cateogory based on var_id
    
    Args: 
        data: data frame with data
        category: name of cateogory
        variables: Variables object
        populations: list of populations to use, same length as number of variables in category
        var_id: variable_id
        name: name of variable
    """

    ret = pd.DataFrame(columns=["incidence_rate", "ci_lower", "ci_upper"])
    for loc in locations.get_level(level):
        if loc not in exclude:
            group_data = data[data[level] == int(loc)]
            add = False
            if populations:
                name = locations.name(loc)
                if name in populations:
                    population = populations[name]
                elif loc in populations:
                    population = populations[loc]
                else:
                    print(populations)
                    print(name, loc)


                    raise KeyError("Populations needs to include either variable id or name")

                if population != 0:
                    add = True
                    incidence_rate = univariate.incidence_rate(group_data, population=population,
                                                               var_id=var_id, name=name, variables=variables)
            else:
                add = True
                incidence_rate = univariate.incidence_rate(group_data, var_id=var_id, name=name, variables=variables)
            if add:
                ret.loc[locations.name(loc)] = [incidence_rate[0], incidence_rate[0]-incidence_rate[1][0], incidence_rate[1][1]-incidence_rate[0]]
    return ret


def plot_incidence_rate(incidence_rates, mult_factor=1, sort=False):
    """
    Plot a bar chart of incidece rates with error bars

    Args: 
        incidence_rates: data frame with incidence rates

    """

    incidence_rates = incidence_rates.copy()
    if sort:
        incidence_rates.sort_index(inplace=True)
    
    error = np.array(incidence_rates[["ci_lower", "ci_upper"]]) * mult_factor
    incidence_rates["incidence_rate"] = incidence_rates["incidence_rate"] * mult_factor
    incidence_rates["incidence_rate"].plot(kind="bar",yerr=error.transpose())

def plot_odds_ratios(odds_ratios, rot=0):
    """
    Plot a bar chart of incidece rates with error bars

    Args: 
        incidence_rates: data frame with incidence rates

    """
    upper_errors = odds_ratios["ci_upper"] - odds_ratios["odds_ratio"]
    lower_errors = odds_ratios["odds_ratio"] - odds_ratios["ci_lower"]
    
    errors = np.array([upper_errors, lower_errors])
    odds_ratios["odds_ratio"].plot(kind="bar",yerr=errors, rot=rot)
    ax = pylab.axis()
    pylab.plot([ax[0], ax[1]], [1, 1], color="black", alpha=0.4)
    
def plot_many_incidence_rates(rate_list, rot=0, mult_factor=1):
    """
    Plot a dictionary of different incidence rates in one plot

    Args: 
        rate_list: ["name", incidence_rate_object]
    """

    keys = [r[0] for r in rate_list]

    data = rate_list[0][1].copy()
    del data["incidence_rate"]
    del data["ci_lower"]
    del data["ci_upper"]
    errors = np.zeros((2, 2, len(rate_list)))
    for i, k in enumerate(keys):
        data[fill(k, 20)] = rate_list[i][1]["incidence_rate"] * mult_factor
        errors[:, 0, i] = rate_list[i][1]["ci_upper"] * mult_factor
        errors[:, 1, i] = rate_list[i][1]["ci_lower"] * mult_factor

    data.transpose().plot(kind="bar", yerr=errors,  rot=rot)

def odds_ratio_many(data, diseases, group, population=None, variables=None):
    """
    Calculate the incidence rates for all the groups in cateogory based on var_id
    
    Args: 
        data: data frame with data
        diseases: list of disease
        group: (gr_1, gr_2)
        population: poulation dict
    """
    ret_data = pd.DataFrame(columns=["odds_ratio", "ci_lower", "ci_upper"])

    for d in diseases:
        o_r = odds_ratio(data, d, group, population)

        if variables:
            name = variables.name(d)
        else:
            name = d
        ret_data.loc[name] = o_r
    return ret_data
def odds_ratio(data, disease, group, population=None):
    """
    Calculates the odds ratio of disease by group
    Args: 
        data: data frame with data
        disease: the disease id
        group: (gr_1, gr_2)
        population: poulation dict
    """
    if disease not in data.columns:
        return (0, 0, 0)
    group_one = data[data[group[0]] == 1]
    group_two = data[data[group[1]] == 1]
    
    numerator_count = group_one[disease].sum()
    denominator_count = group_two[disease].sum()
    if numerator_count == 0:
        return (0, 0, 0)
    if population:
        numerator_pop = population[group[0]]
        denominator_pop = population[group[1]]
    else:
        numerator_pop = len(group_one)
        denominator_pop = len(group_two)
    return calc_odds_ratio(numerator_count, numerator_pop, denominator_count, denominator_pop)


def calc_odds_ratio(numerator_count, numerator_pop, denominator_count, denominator_pop):
    """
    Calculates the odds ratio with confidence interval

    Args:
       numerator_count
       numerator_pop
       denominator_count
       denominator_pop
    """

    o_r = (numerator_count / numerator_pop) / (denominator_count / denominator_pop)

    # CI http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2938757/

    upper = np.exp( np.log(o_r) + 1.96 * np.sqrt(
        1 / numerator_count + 1 / numerator_pop + 1 / denominator_count + 1 / denominator_pop))
    lower = np.exp( np.log(o_r) - 1.96 * np.sqrt(
        1 / numerator_count + 1 / numerator_pop + 1 / denominator_count + 1 / denominator_pop))
    return (o_r, upper, lower)


def many_incidence_rates_to_flat(rate_list, rot=0, mult_factor=1):
    """
    Plot a dictionary of different incidence rates in one plot

    Args: 
        rate_list: ["name", incidence_rate_object]
    """

    keys = [r[0] for r in rate_list]

    columns = []
    for i in rate_list[0][1].index:
        columns.append(i)
        columns.append(i +" error_lower")
        columns.append(i +" error_upper")
        
    data = pd.DataFrame(columns=columns)
    for i, k in enumerate(keys):
        row = []
        for c in rate_list[i][1].index:
            r = rate_list[i][1].loc[c]
            row.append(r["incidence_rate"] * mult_factor)
            row.append(r["ci_lower"] * mult_factor)
            row.append(r["ci_upper"] * mult_factor)
        data.loc[k] = row

        
    return data
