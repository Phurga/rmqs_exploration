import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

from utilities import load_data, save_fig, relabel_top_n, generate_rmqs_geodataframe, box_to_france
from GLOBALS import FRANCE_BORDERS_PATH, LAND_USE_COLOR_MAPPING, EEA_SHP_BIOREGION_PATH, ECOREGIONS_PATH

FONTSIZE = 24

def plot_rmqs_with_attribute(data, attribute, attribute_alias, categorical=True, top_n = 9) -> None:
    """Plot RMQS sample sites in France colored by a specified attribute."""
    
    if top_n is not None:
        data[attribute] = relabel_top_n(data[attribute], top_n)
    gdf = generate_rmqs_geodataframe(data)
    
    fig, ax = plt.subplots(figsize=(12, 10))  # Adjusted figure size for legend
    # Load France geometry and clip to bounds
    france = gpd.read_file(FRANCE_BORDERS_PATH).to_crs(gdf.crs)
    france.plot(ax=ax, kind='geo', color='white', edgecolor='black')

    # Choose colormap based on whether the data is categorical or continuous
    if categorical:
        cmap = 'Set1'  # discrete colormap for categories
        if attribute == 'land_use': # Assign colors to each point based on land use (special case)
            gdf["color"] = gdf[attribute].map(LAND_USE_COLOR_MAPPING).fillna("gray")
    else:
        cmap = 'viridis'  # continuous colormap for ranges

    
    gdf.plot(ax=ax, kind='geo', column=attribute, cmap=cmap, legend=True, markersize=30, categorical=categorical, marker='o', legend_kwds={'label': attribute_alias})

    # set title and axis labels using FS
    ax.set_title("Sample Sites in France by " + attribute_alias, fontsize=FONTSIZE)
    ax.set_xlabel("Longitude", fontsize=FONTSIZE)
    ax.set_ylabel("Latitude", fontsize=FONTSIZE)

    # adjust legend text and title font sizes
    if ax.get_legend() is not None:
        ax.get_legend().set_title(attribute_alias, prop={'size': FONTSIZE})
        for text in ax.get_legend().get_texts():
            text.set_fontsize(FONTSIZE)
        title = ax.get_legend().get_title()
        if title is not None:
            title.set_fontsize(FONTSIZE)
    
    plt.tight_layout()
    save_fig(fig, "map", f"france_{attribute_alias}")
    return fig

def plot_rmqs_with_regions(regions_file, region_col, alias):#show a map with points and regions
    """plot rmqs points and regions from a shapefile"""
    rmqs_pts = generate_rmqs_geodataframe(load_data())

    regions = gpd.read_file(regions_file)[[region_col, "geometry"]]
    if rmqs_pts.crs != regions.crs:
        regions = regions.to_crs(rmqs_pts.crs)
    
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8,8))
    ax = box_to_france(ax)

    # color regions by code and show a legend; fall back to a simple grey fill
    #remove regions that do not appear in xlim and ylim
    visible_regions = regions.cx[0e6:1.1e6, 6.0e6:7.25e6]
    visible_regions.plot(
        ax=ax,
        column=region_col,
        cmap="Pastel1",
        edgecolor="black",
        legend=True,
        legend_kwds={"title": "bioregion", "loc": "upper left", "fontsize": 8},
    )

    fig.gca().add_artist(ax.get_legend()) #manually adding the first legend as an artist to avoid it being overwritten by the second

    # plot points on top, color-coded by 'land_use' when available
    rmqs_pts.plot(
        ax=ax,
        column="land_use",
        categorical=True,
        legend=True,
        legend_kwds={"title": "land_use", "loc": "lower left", "fontsize": 8},
        cmap="Dark2",
        markersize=20,
        edgecolor="black",
        alpha=0.9,
        zorder=5,
    )

    ax.set_title(f"RMQS points and {alias}")
    save_fig(fig, "map", f"rmqs_points_{alias}")

    return None

if __name__ == "__main__":
    data = load_data()
    plot_rmqs_with_attribute(data, "ph_eau_6_1", "soil_ph", False, None)

    plot_rmqs_with_regions(EEA_SHP_BIOREGION_PATH, "code", "bioregion")
    #"C:\\Users\\aburg\\Documents\\analyses\\rmqs_exploration\\data_sm\\wwf_terr_ecos\\wwf_terr_ecos.shp"
    plot_rmqs_with_regions(ECOREGIONS_PATH, "ECO_NAME", "ecoregion")

DIMENSIONS = [
    ("signific_ger_95", 'soil_type'),
    ("parent_material", 'parent_material'),
    ("desc_code_occupation3", 'land_use_fine'),
    ("land_use", 'land_use'),
    ("wrb_guess", 'soil_class'),
    ("bioregion", 'bioregion'),
    ("ph_eau_6_1", "soil_ph", False, None)
]