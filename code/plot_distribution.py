import warnings
import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns

from utilities import load_data, save_fig, relabel_bottom

# globally silence FutureWarning messages
warnings.filterwarnings("ignore", category=FutureWarning)

def prepare_data(meta_df: pd.DataFrame, group_col: str, value_col: str):
    """Prepares the data for plotting."""
    meta_df[group_col] = relabel_bottom(meta_df[group_col])

    # order categories by median (descending)
    medians = meta_df.groupby(group_col)[value_col].median().sort_values(ascending=False)
    order = medians.index.tolist()

    # counts per category for labels
    counts = meta_df.groupby(group_col).size().reindex(order).fillna(0).astype(int)
    y_labels = [f"{cat} ({cnt}p)" for cat, cnt in zip(order, counts)]
    
    # build colormap mapping from counts -> color
    cmap = mpl.cm.viridis
    norm = mpl.colors.Normalize(vmin=counts.min(), vmax=counts.max())
    color_map = {cat: cmap(norm(cnt)) for cat, cnt in zip(order, counts)}
    
    return meta_df, order, counts, y_labels, color_map, medians, norm, cmap

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

def annotate_medians(ax: plt.Axes, medians: pd.Series):
    """Annotates the medians on the plot."""
    offset = max(medians.max() * 0.005, 0.5)
    fmt = lambda x, pos=None: f"{x:,.0f}".replace(",", "'")
    for i, (cat, med) in enumerate(medians.items()):
        ax.text(med + offset, i, fmt(med), va="center", ha="left", fontsize=8, fontweight="bold", color="white")

def plot_distribution(meta_df: pd.DataFrame, value_col: str, group_col: str, alias: str):
    """Plots the distribution and median of a specified value column by a grouping column."""
    (meta_df, order, counts, y_labels, color_map, 
     medians, norm, cmap) = prepare_data(meta_df, group_col, value_col)

    # figure portrait
    fig_w, fig_h = 8, max(8, 0.35 * len(order))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    plot_violin(ax, meta_df, value_col, group_col, order, color_map)
    plot_jitter(ax, meta_df, value_col, group_col, order)
    annotate_medians(ax, medians)

    # set y labels and formatting
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(y_labels)
    ax.set_xlabel(value_col)
    ax.set_ylabel("")
    ax.set_title(f"Distribution and median of {value_col} by {alias}")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos=None: f"{x:,.0f}".replace(",", "'")))
    
    # create colorbar — adjust fraction to control thickness
    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array(counts.values)
    cbar = fig.colorbar(sm, ax=ax, pad=0.02, fraction=0.03)
    cbar.set_label("samples count", rotation=270, labelpad=12)
    plt.tight_layout()

    save_fig(fig, "distribution", f"{value_col}_by_{alias}")
    return None


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