import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from utilities import load_data, save_fig, relabel_top_n

def build_pivot(meta: pd.DataFrame, 
                value_col: str,
                land_col: str, 
                soil_col: str,
                top_n: int,  
                agg: str):
    
    meta[land_col] = relabel_top_n(meta[land_col], top_n)

	# Aggregate richness by land use and soil group
    if agg not in ("mean", "median"):
        raise ValueError("agg must be 'mean' or 'median'")
    func = np.nanmedian if agg == "median" else np.nanmean
    pvt = (
		meta.pivot_table(index=land_col, columns=soil_col, values=value_col, aggfunc=func)
		  .sort_index()
		  .reindex(sorted(meta[soil_col].unique(), key=lambda x: (x != "Other", x)), axis=1)
	)
    return pvt


def plot_heatmap(meta, value_col, land_col, land_col_alias, soil_col, soil_col_alias, top_n=10, agg='median'):
    pvt = build_pivot(meta=meta, value_col=value_col, land_col=land_col, soil_col=soil_col, top_n=top_n, agg=agg)
    
    plt.figure(figsize=(12, 6))
    ax = sns.heatmap(pvt, cmap="viridis", annot=True, fmt=".1f", linewidths=0.5, linecolor="#eeeeee")
    ax.set_xlabel(soil_col_alias)
    ax.set_ylabel(land_col_alias)
    title = f"{value_col.capitalize()} {agg} by {land_col_alias} x {soil_col_alias}"
    ax.set_title(title)
    plt.tight_layout()
    save_fig(plt.gcf(), "heatmap", f"{value_col}_{agg}_by_{land_col}_x_{soil_col}")
    return None


if __name__ == "__main__":
    meta = load_data()
    plot_heatmap(meta, "otu_richness", "land_use", "land_use", "bioregion", "bioregion", top_n=10, agg='median')