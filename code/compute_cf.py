from utilities import write_csv, load_data
import GLOBALS

import pandas as pd
import geopandas as gpd
import numpy as np

def lookup_reference(row: pd.Series, reference_land_use: str, median_pivot: pd.DataFrame, attribute: str, value: str):
    """
    Looks up in a pivot containing median values of otu richness for a classifiers
    replacing the following that does not work : 
    data["reference_cf"] = pvt.loc[(reference_land_use, data["bioregion"], data["signific_ger_95"])]["otu_richness"].median()
    """
    try:
        return median_pivot.loc[(reference_land_use, row[attribute]), value]
    except KeyError:
        return np.nan

def compute_land_use_cf_median_context(
    data: gpd.GeoDataFrame,
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
    # combine classifiers to get the context (supports any number of context columns)
    data["context"] = data[context].astype(str).agg('_'.join, axis=1)

    # calculate median quality indicator per combination of classifiers
    median_indicator_context = data.pivot_table(
        index=['land_use','context'], 
        values=indicator, 
        aggfunc="median", 
        fill_value=np.nan)

    # compute cf, ie 1 - Ic/Ic,rel where Ic is the indicator in context c defined by the classifiers
    data[f"reference_median_{indicator}"] = pd.Series(
        [lookup_reference(
            row=row, 
            reference_land_use=reference_land_use, 
            median_pivot=median_indicator_context, 
            attribute="context",
            value= indicator)
         for _, row in data.iterrows()]
    )
    data[f"relative_{indicator}"] = data[indicator] / data[f"reference_median_{indicator}"]
    data['cf'] = 1 - data[f"relative_{indicator}"]

    # compute median CF per classifiers
    median_cf_context = data.pivot_table(
        index=['land_use', 'context'],
        values=[f"relative_{indicator}","cf"],
        aggfunc=["median", "count"])
    
    # write results in disk and return
    results_cols = [f"reference_median_{indicator}", f"relative_{indicator}", "cf"]
    write_csv(data[results_cols], GLOBALS.RMQS_CF_PATH)
    write_csv(median_cf_context, GLOBALS.RMQS_CF_SUMMARY_PATH)

    # plot distribution of cf values
    from plot_distribution import plot_land_use_distribution
    plot_land_use_distribution(data, f"relative_{indicator}", 'context')
    
    return data


if __name__ == "__main__":
    indicator = "otu_richness"
    data = load_data()
    compute_land_use_cf_median_context(data)