import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from utilities import save_fig, relabel_bottom, load_rmqs_data

def build_pivot(data: pd.DataFrame, 
                value_field: str,
                line_field: str, 
                col_field: str,
                func: str):
    try:
        data[line_field]
    except KeyError:
        raise KeyError(f"Column {line_field} not found in data.")
    
    data[line_field] = relabel_bottom(data[line_field], cutoff_quantile=0.9)

	# Aggregate richness by land use and soil group

    pvt = data.pivot_table(index=line_field, columns=col_field, values=value_field, aggfunc=func)
    pvt = pvt.loc[pvt.sum(1).sort_values(ascending=False).index] #sort by total row values
    return pvt


def plot_heatmap(data, value_field, line_field, line_field_alias, col_field, col_field_alias, func='median'):
    """Plot heatmap of value_field aggregated by line_field and col_field."""
    pvt = build_pivot(data=data, value_field=value_field, line_field=line_field, col_field=col_field, func=func)

    plt.figure(figsize=(12, 6))
    ax = sns.heatmap(pvt, cmap="viridis", annot=True, fmt=".1f", linewidths=0.5, linecolor="#eeeeee")
    ax.set_xlabel(col_field_alias)
    ax.set_ylabel(line_field_alias)
    title = f"{value_field.capitalize()} {func} by {line_field_alias} x {col_field_alias}"
    ax.set_title(title)
    plt.tight_layout()
    save_fig(plt.gcf(), "heatmap", f"{value_field}_{func}_by_{line_field}_x_{col_field}")
    return None


if __name__ == "__main__":
    data = load_rmqs_data()
    plot_heatmap(data, 
                 value_field="otu_richness", 
                 line_field="signific_ger_95", line_field_alias="soil_type", 
                 col_field="bioregion", col_field_alias="bioregion", 
                 func='count')