import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

from utilities import load_data, save_fig

def build_pivot(meta: pd.DataFrame, rich: pd.DataFrame, top_n: int,
				land_col: str, soil_col: str,
				agg: str):
    rich_col = "otu_richness"
    df = pd.merge(rich[rich_col], meta[[land_col, soil_col]], left_index=True, right_index=True, how="inner").copy()

	# Aggregate richness by land use and soil group
    if agg not in ("mean", "median"):
        raise ValueError("agg must be 'mean' or 'median'")
    func = np.nanmedian if agg == "median" else np.nanmean
    pvt = (
		df.pivot_table(index=land_col, columns=soil_col, values=rich_col, aggfunc=func)
		  .sort_index()
		  .reindex(sorted(df[soil_col].unique(), key=lambda x: (x != "Other", x)), axis=1)
	)
    return pvt


def plot_heatmap(pvt: pd.DataFrame, land_col: str, soil_col: str, rich_col: str) -> None:
    plt.figure(figsize=(12, 6))
    ax = sns.heatmap(pvt, cmap="viridis", annot=True, fmt=".1f", linewidths=0.5, linecolor="#eeeeee")
    ax.set_xlabel(soil_col)
    ax.set_ylabel(land_col)
    title = f"{rich_col.capitalize()} by {land_col} x {soil_col}"
    ax.set_title(title)
    plt.tight_layout()
    save_fig(plt.gcf(), "heatmap", f"{rich_col}_by_{land_col}_x_{soil_col}")
    return None


def main(value_col, land_col, soil_col) -> int:
    rich, meta = load_data(top_n=10, top_column=soil_col)
    pvt = build_pivot(meta, rich, top_n=10, land_col=land_col, soil_col=soil_col, agg='median')
    plot_heatmap(pvt, land_col, soil_col, value_col)
    return None

if __name__ == "__main__":
	main("land_use", "wrb_guess", "otu_richness")