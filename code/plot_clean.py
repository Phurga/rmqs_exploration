import GLOBALS
import utilities

import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import pandas as pd

data_rmqs = utilities.load_rmqs_data()

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

kwargs_heatmap = {
    'cmap': sns.color_palette("vlag", as_cmap=True),
    'linewidths': 0.5, 
    'linecolor':"#eeeeee",
    'center':1
    }

def trim_floats(val):
    if type(val) is float:
        return f"{val:.2f}"
    else:
        return val

def add_count_to_series(series : pd.Series, counts: pd.Series) -> pd.Series:
    series = series.map(trim_floats, na_action="ignore")
    def format_counts(val):
        return f"\n(n: {int(val)})"
    return series + counts.map(format_counts, na_action="ignore")

def plot_median_rel_rich_pedoclim_croplands(data_rmqs: gpd.GeoDataFrame):
    data_rmqs = data_rmqs[data_rmqs["land_use"] == "annual crops"]
    
    medians = data_rmqs.pivot_table(
        values="relative_otu_richness",
        index="bioregion",
        columns="WRB_LVL1",
        aggfunc="median",
        margins=True
        )

    counts = data_rmqs.pivot_table(
        values="relative_otu_richness",
        index="bioregion",
        columns="WRB_LVL1",
        aggfunc="count",
        margins=True
        )

    annot_data = add_count_to_series(medians, counts)

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.heatmap(
        ax=ax,
        data=medians,
        annot=annot_data,
        fmt = "",
        **kwargs_heatmap,
        )

    ax.set_xlabel("soil class (WRB LEVEL 1)")
    ax.set_ylabel("climate (EEA bioregions)")
    ax.set_title("Median relative OTU richness by pedoclimatic region, for annual cropland")
    utilities.save_fig(fig, "LCAFOOD", "median_rel_rich_pedoclim_croplands")
    return fig

def plot_median_rel_rich_pedoclim_vs_lu(data_rmqs: gpd.GeoDataFrame):
    data_rmqs['context'] = utilities.relabel_bottom(data_rmqs['context'], approach='top_cats', param=10)
    index = ['context']
    values="relative_otu_richness"
    columns="land_use"
    medians = data_rmqs.pivot_table(
        values=values,
        index=index,
        columns=columns,
        aggfunc="median",
        margins=True)

    counts = data_rmqs.pivot_table(
        values=values,
        index=index,
        columns=columns,
        aggfunc="count",
        margins=True)

    values_labels = add_count_to_series(medians, counts)
    assert counts.index.equals(medians.index) # just a check to avoid plotting errors

    fig, ax = plt.subplots(figsize=(12, 12))

    sns.heatmap(
        ax=ax,
        data=medians,
        annot=values_labels,
        fmt = "",
        **kwargs_heatmap)

    ax.set_xlabel("land use class")
    ax.set_ylabel("pedoclimatic class")
    ax.set_title("Median relative bacterial richness by pedoclimatic region and land use class")
    utilities.save_fig(fig, "LCAFOOD", "median_rel_rich_pedoclim_vs_landuse")
    return fig

def catplot_context_vs_landuse(data_rmqs: gpd.GeoDataFrame):
    data_rmqs['context'] = utilities.relabel_bottom(data_rmqs['context'], approach='top_cats', param=10)
    index = ['context', 'land_use']
    values="relative_otu_richness"
    columns="land_use"

    medians = data_rmqs.pivot_table(
        values=values,
        index=index,
        aggfunc="median",
        margins=True)
    
    fig, ax = plt.subplots(figsize=(6,6))
    sns.stripplot(
        data=medians,
        x="context",
        y="relative_otu_richness",
        hue="land_use",
        ax=ax)
    
    ax.tick_params(axis='x', labelrotation=90)
    
    utilities.save_fig(fig,"results/LCAFOOD/","catplot")
    return None

#plot_median_rel_rich_pedoclim_croplands(data_rmqs)
#plot_median_rel_rich_pedoclim_vs_lu(data_rmqs)
catplot_context_vs_landuse(data_rmqs)