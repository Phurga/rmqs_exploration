from utilities import load_data, relabel_bottom, save_fig

import pandas as pd
import numpy as np


def average_cf_approach(data: pd.DataFrame):
    indicator = "otu_richness"
    reference_land_use = "broadleaved forests"
    data['signific_ger_95'] = relabel_bottom(data['signific_ger_95'])
    pvt = data.pivot_table(index=["land_use","bioregion","signific_ger_95"],values="otu_richness", aggfunc="median", fill_value=np.nan)
    data["reference_cf"] = pvt.loc[(reference_land_use, data["bioregion"], data["signific_ger_95"])]["otu_richness"].median()
    data['cf'] = 1 - data[indicator]/ pvt.loc[reference_land_use, (data["signific_ger_95"], data["bioregion"])]
    return data

#plot distribution of cf_vs_broadleaved_forests values
def show_cf(cf_df):
    import seaborn as sns
    import matplotlib.pyplot as plt
    fig, [ax1, ax2] = plt.subplots(nrows=2, figsize=(12, 12))
    ax1 = plt.scatter(ax=ax1, data=cf_df, x="bioregion", y="cf")
    ax2 = plt.scatter(ax=ax2, data=cf_df, x="signific_ger_95", y="cf")
    fig.title("Distribution of CF")
    save_fig(fig, "statistics", "cf_vs_bioregion_and_soil")
    return fig


if __name__ == "__main__":
    data = load_data()
    show_cf(average_cf_approach(data))
