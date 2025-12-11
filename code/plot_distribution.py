import warnings
import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns

from utilities import load_data, save_fig, relabel_bottom

# globally silence FutureWarning messages
warnings.filterwarnings("ignore", category=FutureWarning)

def plot_violin(ax: plt.Axes, result_df: pd.DataFrame, value_col: str, group_col: str, order: list, color_map: dict):
    """Plots the violin plot."""
    sns.violinplot(
        x=value_col,
        y=group_col,
        data=result_df,
        order=order,
        inner='quartile',
        scale="width",
        width=0.9,
        linewidth=1.8,
        cut=0,
        palette=color_map,
        ax=ax,
    )

def plot_jitter(ax: plt.Axes, result_df: pd.DataFrame, value_col: str, group_col: str, order: list):
    """Overlays jittered points on the violin plot."""
    sns.stripplot(
        x=value_col,
        y=group_col,
        data=result_df,
        order=order,
        color="k",
        size=3.6,
        jitter=0.25,
        alpha=0.55,
        ax=ax,
    )

def plot_distribution(data: pd.DataFrame, value: str, attribute: str, alias: str = None):
    """Plots the distribution and median of a specified value column by a grouping column."""
    if alias is None: alias = attribute

    # order categories by median
    medians = data.groupby(attribute)[value].median().sort_values(ascending=False)
    sorted_groups = medians.index.tolist()

    # figure portrait
    fig_h = max(8, 0.35 * len(sorted_groups))
    fig, ax = plt.subplots(figsize=(8, fig_h))
    plot_violin(ax, data, value, attribute, sorted_groups, None)
    plot_jitter(ax, data, value, attribute, sorted_groups)

    # set y labels and formatting
    ax.set_title(f"Distribution and median of {value} by {alias}")

    if data[value].min() > 100:
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x: f"{x:,.0f}".replace(",", "'")))

    save_fig(fig, "distribution", f"{value}_by_{alias}")
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