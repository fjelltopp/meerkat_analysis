import pandas as pd

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


def incidence_rate_by_category(data, category, variables, populations=None, var_id=None, name=None):
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
        group_data = data[data[group] == 1]
        if populations:
            name = variables.name(group)
            if name in populations:
                population = populations[name]
            elif group in populations:
                population = populations[group]
            else:
                raise KeyError("Populations needs to include either variable id or name")
            incidence_rate = univariate.incidence_rate(group_data, population=population,
                                                       var_id=var_id, name=name, variables=variables)
        else:
            incidence_rate = univariate.incidence_rate(group_data, var_id=var_id, name=name, variables=variables)
        ret.loc[variables.name(group)] = [incidence_rate[0], incidence_rate[0]-incidence_rate[1][0], incidence_rate[1][1]-incidence_rate[0]]
    return ret


def plot_incidece_rate(incidence_rates):
    """
    Plot a bar chart of incidece rates with error bars

    Args: 
        incidence_rates: data frame with incidence rates

    """
    error = np.array(incidence_rates[["ci_lower", "ci_upper"]])
    incidence_rates["incidence_rate"].plot(kind="bar",yerr=error.transpose())
