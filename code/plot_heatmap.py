import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from utilities import load_data, save_fig, relabel_top_n

def build_pivot(data: pd.DataFrame, 
                value_field: str,
                line_field: str, 
                col_field: str,
                top_n: int,  
                func: str):
    
    data[line_field] = relabel_top_n(data[line_field], top_n)

	# Aggregate richness by land use and soil group

    pvt = (
		data.pivot_table(index=line_field, columns=col_field, values=value_field, aggfunc=func)
		  .sort_index()
		  #.reindex(sorted(meta[col_field].unique(), key=lambda x: (x != "Other", x)), axis=1)
	)
    return pvt


def plot_heatmap(data, value_field, line_field, line_field_alias, col_field, col_field_alias, top_n=10, func='median'):
    """Plot heatmap of value_field aggregated by line_field and col_field."""
    pvt = build_pivot(data=data, value_field=value_field, line_field=line_field, col_field=col_field, top_n=top_n, func=func)
    
    plt.figure(figsize=(12, 6*top_n/10))
    ax = sns.heatmap(pvt, cmap="viridis", annot=True, fmt=".1f", linewidths=0.5, linecolor="#eeeeee")
    ax.set_xlabel(col_field_alias)
    ax.set_ylabel(line_field_alias)
    title = f"{value_field.capitalize()} {func} by {line_field_alias} x {col_field_alias}"
    ax.set_title(title)
    plt.tight_layout()
    save_fig(plt.gcf(), "heatmap", f"{value_field}_{func}_by_{line_field}_x_{col_field}")
    return None


if __name__ == "__main__":
    data = load_data()
    #plot_heatmap(meta, "otu_richness", "land_use", "land_use", "bioregion", "bioregion", top_n=10, agg='median')
    plot_heatmap(data, 
                 value_field="otu_richness", 
                 line_field="bioregion", line_field_alias="bioregion", 
                 col_field="land_use", col_field_alias="land_use", 
                 top_n=20, func='median')