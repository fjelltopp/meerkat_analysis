import pandas as pd

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
        results.loc[name] = [data[i].sum()]

    return results
    
