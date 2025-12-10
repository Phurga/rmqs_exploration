from utilities import load_data, relabel_bottom

import pandas as pd
import numpy as np


def average_cf_approach(data: pd.DataFrame):
    indicator = "otu_richness"
    reference_land_use = "broadleaved forests"
    data['signific_ger_95'] = relabel_bottom(data['signific_ger_95'])
    pvt = data.pivot_table(index=["land_use","bioregion","signific_ger_95"], values="otu_richness", aggfunc="median", fill_value=np.nan)
    
    def lookup(row):
        idx = (reference_land_use, row["bioregion"], row["signific_ger_95"])
        try:
            return pvt.loc[idx, "otu_richness"]
        except KeyError:
            return np.nan

    data[f"reference_{indicator}"] = data.apply(lookup, axis=1)
    # replacing the following that does not work : data["reference_cf"] = pvt.loc[(reference_land_use, data["bioregion"], data["signific_ger_95"])]["otu_richness"].median()
    data['cf'] = 1 - data[indicator]/ data[f"reference_{indicator}"]
    return data

#plot distribution of cf_vs_broadleaved_forests values

def show_cf(data):
    from plot_distribution import plot_distribution
    fig1 = plot_distribution(data, "cf", "bioregion")
    fig1
    plot_distribution(data, "cf", "signific_ger_95", "soil_type")
    return None


if __name__ == "__main__":
    data = load_data()
    show_cf(average_cf_approach(data))
