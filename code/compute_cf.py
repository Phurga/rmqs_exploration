from utilities import load_data, write_csv
import GLOBALS

import pandas as pd
import numpy as np

def lookup_reference(row, reference_land_use, median_pivot, classifiers : list, value):
    """
    Looks up in a pivot containing median values of otu richness for a classifiers
    replacing the following that does not work : 
    data["reference_cf"] = pvt.loc[(reference_land_use, data["bioregion"], data["signific_ger_95"])]["otu_richness"].median()
    """
    idx = (reference_land_use, *[row[classifier] for classifier in classifiers])
    try:
        return median_pivot.loc[idx, value]
    except KeyError:
        return np.nan

def compute_cf_median_classified_references(
        data: pd.DataFrame, 
        context = ["bioregion", 'WRB_LVL1'],
        reference_land_use = "broadleaved forests",
        indicator = "otu_richness",
        ):
    """
    Docstring for compute_cf_median_classified_references
    
    :param data: data source
    :type data: pd.DataFrame
    :param classifiers: attributes of data, where each combination of classifier is a consistent group to derive median indicator value
    :param reference_land_use: reference land use to calculate a natural counterfactual indicator value
    :param indicator: indicator for ecosystem quality defined
    """
    # combine classifiers to get the context
    data["context"] = data[context[0]] + '_' + data[context[1]] #TODO: improve to get n sized context

    # calculate median quality indicator per combination of classifiers
    median_indicator_context = data.pivot_table(
        index=['land_use','context'], 
        values=indicator, 
        aggfunc="median", 
        fill_value=np.nan)

    # compute cf, ie 1 - Ic/Ic,rel where Ic is the indicator in context c defined by the classifiers
    data[f"reference_median_{indicator}"] = data.apply(
        lookup_reference, 
        args=(reference_land_use, median_indicator_context, context, indicator), 
        axis=1)
    data[f"relative_{indicator}"] = data[indicator] / data[f"reference_median_{indicator}"]
    data['cf'] = 1 - data[f"relative_{indicator}"]

    # compute median CF per classifiers
    median_cf_context = data.pivot_table(
        index=['land_use', 'context'],
        values=[f"relative_{indicator}","cf"],
        aggfunc=["median", "count"])
    
    # temporarily remove uninteresting results
    data = data[data["land_use"].isin(['natural sites', 'urban sites']) == False]

    # see some results
    from plot_distribution import plot_distribution
    plot_distribution(data, f"relative_{indicator}", 'context')
    
    # write results in disk
    results_cols = [f"reference_median_{indicator}", f"relative_{indicator}", "cf"]
    write_csv(data[results_cols], GLOBALS.RMQS_CF_PATH)
    write_csv(median_cf_context, GLOBALS.RMQS_CF_SUMMARY_PATH)
    return data

    #plot distribution of cf_vs_broadleaved_forests values


if __name__ == "__main__":
    data = load_data()
    soil_classifier='WRB_LVL1'
    compute_cf_median_classified_references(data)