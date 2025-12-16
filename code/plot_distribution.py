import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns

from utilities import save_fig, relabel_bottom, load_rmqs_data

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
    "palette":"dark:k",
    "size":3.6,
    "jitter":0.25,
    "alpha":0.55
}

def plot_land_use_distribution(
        data: pd.DataFrame, 
        value: str, attribute: str, alias: str = None,
        relabel_approach = None,
        relabel_param = None
        ) -> plt.Figure:
    """Plots the distribution and median of a specified value column by a grouping attribute."""
    if alias is None: alias = attribute
    # temporarily remove uninteresting land use classes and tidy data
    data[attribute] = relabel_bottom(data[attribute], approach=relabel_approach, param=relabel_param)
    data = data[data["land_use"].isin(['natural sites', 'urban sites']) == False]
    land_use_order = [
        'broadleaved forests',
        'coniferous forests',
        'meadows',
        'annual crops',
        'permanent crops']
    data[attribute] = relabel_bottom(data[attribute], approach='top_cats', param=20) #reduce size for plotting

    # order categories by median
    statistics = ['median', 'count']
    data_summary = data.pivot_table(values=value,index=[attribute,"land_use"],aggfunc=statistics)
    data_summary = data_summary.sort_values((statistics[0], value), ascending=False)

    attribute_summary = data.pivot_table(values=value,index=attribute,aggfunc=statistics)
    attribute_summary = attribute_summary.sort_values((statistics[1], value), ascending=False)

    # figure portrait
    fig_h = max(8, 0.35 * len(data_summary))
    fig, ax = plt.subplots(figsize=(8, fig_h))
    ax.axvline(x=1, color='k', linestyle='-', zorder=0)
    sns.violinplot(data = data, x = value, y = attribute, order=attribute_summary.index,
                   ax = ax, **kwargs_violin, hue="land_use", hue_order=land_use_order)

    # set y labels and formatting
    ax.set_title(f"Distribution and median of {value} by {attribute} ({alias})")

    if data[value].min() > 100:
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x: f"{x:,.0f}".replace(",", "'")))
    # build y tick labels with counts and set matching tick positions to avoid FixedFormatter warnings
    yticklabels = [f"{i}\n{statistics[1]}: {val.iloc[1]:.0f}" for i, val in attribute_summary.iterrows()]
    ax.set_yticks(range(len(yticklabels)))
    ax.set_yticklabels(yticklabels)
    save_fig(fig, "distribution", f"{value}_by_{attribute}_{alias}")
    return fig


if __name__ == "__main__":
    meta_df = load_rmqs_data()
    plot_land_use_distribution(meta_df, "otu_richness", "bioregion", 'bioregion')

"""
"signific_ger_95", 'soil type'
"wrb_guess", 'WRB class'
"parent_material", 'parent material'
"desc_code_occupation3", 'land use (fine)'
"land_use", 'land_use'
"bioregion", "bioregion"
"""