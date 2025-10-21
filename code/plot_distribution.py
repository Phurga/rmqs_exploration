import warnings
from pathlib import Path
import matplotlib as mpl
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns

from utilities import load_data, save_fig

# globally silence FutureWarning messages
warnings.filterwarnings("ignore", category=FutureWarning)

def plot_richness(otu_counts: pd.DataFrame, meta_df: pd.DataFrame, value_col: str, group_col: str, alias: str):
    result_df = otu_counts.join(meta_df[[group_col]], how='left')

    # order categories by median (descending)
    medians = result_df.groupby(group_col)[value_col].median().sort_values(ascending=False)
    order = medians.index.tolist()

    # counts per category for labels
    counts = result_df.groupby(group_col).size().reindex(order).fillna(0).astype(int)
    y_labels = [f"{cat} ({cnt}p)" for cat, cnt in zip(order, counts)]
    
    # build colormap mapping from counts -> color
    cmap = mpl.cm.viridis
    norm = mpl.colors.Normalize(vmin=counts.min(), vmax=counts.max())
    color_map = {cat: cmap(norm(cnt)) for cat, cnt in zip(order, counts)}

    # figure portrait
    fig_w, fig_h = 8, max(8, 0.35 * len(order))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # thicker violins: no inner to reduce clutter
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

    # jittered points overlay — slightly larger & semi-transp
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

    # annotate medians
    medians = result_df.groupby(group_col)[value_col].median().reindex(order)
    offset = max(medians.max() * 0.005, 0.5)
    fmt = lambda x, pos=None: f"{x:,.0f}".replace(",", "'")
    for i, (cat, med) in enumerate(medians.items()):
        ax.text(med + offset, i, fmt(med), va="center", ha="left", fontsize=8, fontweight="bold", color="white")

    # set y labels and formatting
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(y_labels)
    ax.set_xlabel(value_col)
    ax.set_ylabel("")
    ax.set_title(f"Distribution and median of {value_col} by {alias}")
    ax.xaxis.set_major_formatter(FuncFormatter(fmt))
    
    # create colorbar — adjust fraction to control thickness
    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array(counts.values)
    cbar = fig.colorbar(sm, ax=ax, pad=0.02, fraction=0.03)
    cbar.set_label("samples count", rotation=270, labelpad=12)
    plt.tight_layout()

    save_fig(fig, "distribution", f"{value_col}_by_{alias}")


def main(value_col, group_col, alias):
    otu_counts, meta_df = load_data()
    plot_richness(otu_counts, meta_df, value_col, group_col, alias)

if __name__ == "__main__":
    main("otu_richness", "bioregion", 'bioregion')

"""
"signific_ger_95", 'soil type'
"wrb_guess", 'WRB class'
"parent_material", 'parent material'
"desc_code_occupation3", 'land use (fine)'
"land_use", 'land_use'
"bioregion", "bioregion"
"""