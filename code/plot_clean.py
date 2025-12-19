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

kwargs_legend = {
    'ncol': 2,
    'bbox_to_anchor': (0.5, 0),
    'loc': 'upper center'
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

def heatmap_pedoclim_croplands(data: gpd.GeoDataFrame):
    data = data[data["land_use"] == "annual crops"]
    
    medians = data.pivot_table(
        values="relative_otu_richness",
        index="bioregion",
        columns="WRB_LVL1",
        aggfunc="median",
        margins=True
        )

    counts = data.pivot_table(
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
    filetitle = '_'.join([
        "heatmap_of",
        "relative_otu_richness",
        "vars",
        "bioregion",
        "WRB_LVL1"
    ])
    utilities.save_fig(fig,"LCAFOOD",filetitle)
    return fig

def heatmap_pedoclim_vs_lu(data: gpd.GeoDataFrame):
    data['context'] = utilities.relabel_bottom(data['context'], approach='top_cats', param=10)
    index = ['context']
    values="relative_otu_richness"
    columns="land_use"
    medians = data.pivot_table(
        values=values,
        index=index,
        columns=columns,
        aggfunc="median",
        margins=True)

    counts = data.pivot_table(
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
    filetitle = '_'.join([
        "heatmap_of",
        values,
        "vars",
        *index,
        columns
    ])
    utilities.save_fig(fig,"LCAFOOD",filetitle)
    return fig

def stripplot_context_vs_landuse(data: gpd.GeoDataFrame):
    data['context'] = utilities.relabel_bottom(data['context'], approach='top_cats', param=10)
    index = ['context', "land_use"]
    values="relative_otu_richness"

    medians = data.pivot_table(
        values=values,
        index=index,
        aggfunc="median")
    
    fig, ax = plt.subplots()
    ax.axvline(1, color='k', ls='dotted')
    sns.stripplot(
        data=medians,
        x=values,
        y=index[0],
        hue=index[1],
        ax=ax)
    
    identifier = [
        "median",
        "of",
        values,
        "vs",
        *index
    ]
    ax.xaxis.set_tick_params(bottom=False, top=True, labelbottom=False, labeltop=True)
    ax.xaxis.set_label_text(None)
    sns.move_legend(ax, **kwargs_legend)
    ax.set_title(' '.join(identifier), wrap=True)
    utilities.save_fig(fig, "LCAFOOD", '_'.join(identifier))
    return None

def boxplot_context_vs_landuse(data: gpd.GeoDataFrame):
    data['context'] = utilities.relabel_bottom(data['context'], approach='top_cats', param=10)
    data = data[data['land_use'].isin(["natural sites", "urban sites"]) == False]
    x = "relative_otu_richness"
    y = 'context'
    hue = "land_use"
    
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.axvline(1)
    sns.boxplot(
        data=data,
        x=x,
        y=y,
        hue=hue,
        ax=ax)
    
    filetitle = '_'.join([
        "median of",
        x,
        "vars",
        y,
        hue
    ])
    sns.move_legend(ax, **kwargs_legend)
    ax.set_title(filetitle)
    utilities.save_fig(fig,"LCAFOOD",filetitle)
    return None

heatmap_pedoclim_croplands(data_rmqs)
heatmap_pedoclim_vs_lu(data_rmqs)
stripplot_context_vs_landuse(data_rmqs)
boxplot_context_vs_landuse(data_rmqs)