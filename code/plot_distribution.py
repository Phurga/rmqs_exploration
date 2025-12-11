import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
from blume import table

from utilities import load_data, save_fig, relabel_bottom

# globally silence FutureWarning messages
#import warnings
#warnings.filterwarnings("ignore", category=FutureWarning)

#define default parameters for plots
kwargs_violin = {
    'inner': 'quartile',
    'density_norm': 'width',
    'width': 0.9,
    'linewidth': 1.8,
    'cut': 0
}

kwargs_jitter = {
    "color":"k",
    "size":3.6,
    "jitter":0.25,
    "alpha":0.55
}

def plot_distribution(data: pd.DataFrame, value: str, 
                      attribute: str, alias: str = None):
    """Plots the distribution and median of a specified value column by a grouping attribute."""
    if alias is None: alias = attribute
    data[attribute] = relabel_bottom(data[attribute], approach='n_cats', top_n=8) #reduce size for plotting

    # order categories by median
    statistics = ['median', 'count']
    data_summary = data.pivot_table(values=value,index=attribute,aggfunc=statistics)
    data_summary = data_summary.sort_values((statistics[0], value), ascending=False)

    # figure portrait
    fig_h = max(8, 0.35 * len(data_summary))
    fig, ax = plt.subplots(figsize=(8, fig_h))
    sns.violinplot(data = data, x = value, y = attribute, order = data_summary.index,
                   ax = ax, **kwargs_violin)
    sns.stripplot(data=data, x=value, y=attribute, order=data_summary.index, 
                  ax=ax, **kwargs_jitter)

    # set y labels and formatting
    ax.set_title(f"Distribution and median of {value} by {attribute} ({alias})")

    if data[value].min() > 100:
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x: f"{x:,.0f}".replace(",", "'")))
    ax.set_yticklabels([f"{i}\n {statistics[0]}: {val[0]:.2f}, {statistics[1]}: {val[1]:.0f}" 
                         for i, val in data_summary.iterrows()])
    save_fig(fig, "distribution", f"{value}_by_{attribute}_{alias}")
    return fig


if __name__ == "__main__":
    meta_df = load_data()
    plot_distribution(meta_df, "otu_richness", "bioregion", 'bioregion')

"""
"signific_ger_95", 'soil type'
"wrb_guess", 'WRB class'
"parent_material", 'parent material'
"desc_code_occupation3", 'land use (fine)'
"land_use", 'land_use'
"bioregion", "bioregion"
"""