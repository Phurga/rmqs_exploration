import GLOBALS
import utilities
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import pandas as pd

data_rmqs = utilities.load_rmqs_data()
data_rmqs = data_rmqs[data_rmqs["land_use"] == "annual crops"]
medians = data_rmqs.pivot_table(
    values="relative_otu_richness",
    index="bioregion",
    columns="WRB_LVL1",
    aggfunc="median")

counts = data_rmqs.pivot_table(
    values="relative_otu_richness",
    index="bioregion",
    columns="WRB_LVL1",
    aggfunc="count",
    )

def format_median(val):
    return f"{val:.2f}"

def format_counts(val):
    return f"({int(val)} samples)"

annot_data = medians.map(format_median, na_action="ignore") + "\n" + counts.map(format_counts, na_action="ignore")

fig, ax = plt.subplots(figsize=(12, 6))

sns.heatmap(
    ax=ax,
    data=medians,
    annot=annot_data,
    fmt = "",
    linewidths=0.5, 
    linecolor="#eeeeee")

ax.set_xlabel("soil class (WRB LEVEL 1)")
ax.set_ylabel("climate (EEA bioregions)")
ax.set_title("Median relative OTU richness by pedoclimatic region, for annual cropland")
utilities.save_fig(fig, "LCAFOOD", "median_rel_rich_pedoclim_croplands.png")