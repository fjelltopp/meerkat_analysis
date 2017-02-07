import pandas as pd
from statsmodels.stats import proportion


def incidence_rate_by_location(data, locations, var_id, level="clinic"):
    """
    Returns an incidence rate for each location

    Args: 
        data: pandas data frame with data
        locations: location class
        var_id: variable_id
        level: what level to calculate for(deafult: clinic)
    Returns:
       data frame with incidence rates for each location
    """

    N = data.groupby(level).sum()[var_id]
    locs = locations.get_level(level)
    print(locs)
    ret = pd.DataFrame(columns=["incidence_rate", "ci_lower", "ci_upper"])
    for l in locs:
        if int(l) in N.index:
            n = N[int(l)]
        else:
            n = 0
        i = n / locations.population(l)
        confidence_interval = proportion.proportion_confint(n,
                                                            locations.population(l)
                                                            , method="wilson")
        ret.loc[locations.name(l)] = [i,
                                      i - confidence_interval[0],
                                      confidence_interval[1] - i]
    return ret
