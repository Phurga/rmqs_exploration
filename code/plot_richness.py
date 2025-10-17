import warnings
from pathlib import Path
import matplotlib as mpl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns

# globally silence FutureWarning messages
warnings.filterwarnings("ignore", category=FutureWarning)

DEFAULT_OTU_RICH = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\results\otu_richness.csv")
DEFAULT_META = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\data\RMQS1_occupation_nommatp_nomsol_23_03_2022.csv")
OUT_DIR = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\results")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_land_use_from_desc(meta: pd.DataFrame):
    """
    Recreate the custom 'land_use' classification:
    - keep desc_code_occupation1 except for 'surfaces boisees'
    - for 'surfaces boisees' use desc_code_occupation3 but only keep allowed subclasses
    - rows with other forest subclasses are set to NaN (dropped later)
    """
    def make_custom(row):
        keep1 = 'surfaces boisees'
        keep3 = 'forets caducifoliees'
        other3 = 'forets de coniferes'
        if row['desc_code_occupation1'] == keep1:
            if row['desc_code_occupation3'] == keep3:
                return keep3
            return other3
        return row['desc_code_occupation1']
    
    meta['land_use'] = meta.apply(make_custom, axis=1)
    return meta

def load_inputs(otu_path: Path, meta_path: Path):
    # load richness (parquet preferred)
    if otu_path.exists() and otu_path.suffix in (".parquet",):
        otu_counts = pd.read_parquet(otu_path)
    elif otu_path.exists():
        # parquet not available: try CSV
        otu_counts = pd.read_csv(otu_path, sep=";", index_col="id_site", encoding="windows-1252")
    else:
        raise FileNotFoundError(f"OTU richness file not found: {otu_path}")

    otu_counts.index = otu_counts.index.astype(str).str.strip()

    meta_df = pd.read_csv(meta_path, index_col="id_site", encoding="windows-1252")
    meta_df.index = meta_df.index.astype(str).str.strip()
    meta_df = build_land_use_from_desc(meta_df)
    return otu_counts, meta_df


def plot_richness(otu_counts: pd.DataFrame, meta_df: pd.DataFrame, group_col: str, alias: str, out_path: Path):
    # If requested group column doesn't exist, try to create land_use from desc fields
    result_df = otu_counts.join(meta_df[group_col], how='inner')

    # order categories by median (descending)
    medians = result_df.groupby(group_col)["otu_richness"].median().sort_values(ascending=False)
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
        x="otu_richness",
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
        x="otu_richness",
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
    medians = result_df.groupby(group_col)["otu_richness"].median().reindex(order)
    offset = max(medians.max() * 0.005, 0.5)
    fmt = lambda x, pos=None: f"{x:,.0f}".replace(",", "'")
    for i, (cat, med) in enumerate(medians.items()):
        ax.text(med + offset, i, fmt(med), va="center", ha="left", fontsize=8, fontweight="bold", color="white")

    # set y labels and formatting
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("OTU richness")
    ax.set_ylabel("")
    ax.set_title(f"Distribution of OTU richness by {alias} (violins + jitter) — medians shown")
    ax.xaxis.set_major_formatter(FuncFormatter(fmt))

    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    print(f"Saved figure to: {out_path}")


def main(group_col, alias):
    out_path = (OUT_DIR / f"otu_richness_by_{alias}.png")
    otu_counts, meta_df = load_inputs(DEFAULT_OTU_RICH, DEFAULT_META)
    plot_richness(otu_counts, meta_df, group_col, alias, out_path)


if __name__ == "__main__":
    main('signific_ger_95', 'soil type')