from utilities import load_data, relabel_bottom

import pandas as pd
import numpy as np


def average_cf_approach(data: pd.DataFrame, soil_classifier = 'WRB_LVL1'):
    indicator = "otu_richness"
    reference_land_use = "broadleaved forests"
    data[soil_classifier] = relabel_bottom(data[soil_classifier])
    pvt = data.pivot_table(index=["land_use","bioregion",soil_classifier], values="otu_richness", aggfunc="median", fill_value=np.nan)
    
    def lookup(row):
        idx = (reference_land_use, row["bioregion"], row[soil_classifier])
        try:
            return pvt.loc[idx, "otu_richness"]
        except KeyError:
            return np.nan

    data[f"reference_{indicator}"] = data.apply(lookup, axis=1)
    # replacing the following that does not work : data["reference_cf"] = pvt.loc[(reference_land_use, data["bioregion"], data["signific_ger_95"])]["otu_richness"].median()
    data['cf'] = 1 - data[indicator]/ data[f"reference_{indicator}"]
    
    return data

#plot distribution of cf_vs_broadleaved_forests values

def show_cf(data, soil_classifier):
    from plot_distribution import plot_distribution
    fig1 = plot_distribution(data, "cf", "bioregion")
    plot_distribution(data, "cf", soil_classifier, "soil_type")
    return None


if __name__ == "__main__":
    data = load_data()
    soil_classifier='WRB_LVL1'
    show_cf(average_cf_approach(data, soil_classifier=soil_classifier), soil_classifier=soil_classifier)