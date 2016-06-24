import pandas as pd


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
