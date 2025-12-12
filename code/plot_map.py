import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

from utilities import save_fig, relabel_bottom, box_to_france, load_data
import GLOBALS

FONTSIZE = 24

def plot_rmqs_with_attribute(data : gpd.GeoDataFrame, attribute: str, attribute_alias: str = None, categorical : bool =True, top_n = 9, background=GLOBALS.FRANCE_BORDERS_PATH, bounds=None) -> None:
    """Plot RMQS sample sites in France colored by a specified attribute."""
    
    if attribute_alias is None:
        attribute_alias = attribute
    # Relabel to 'others' if there are too many categories to display
    if top_n is not None:
        data[attribute] = relabel_bottom(data[attribute], approach='top_cats', param=top_n)
    
    fig, ax = plt.subplots(figsize=(12, 10))  # Adjusted figure size for legend
    # Load background geometry
    background = gpd.read_file(background).to_crs(data.crs)
    background.plot(ax=ax, kind='geo', color='white', edgecolor='black')

    # Choose colormap based on whether the data is categorical or continuous
    if categorical:
        cmap = 'Set1'  # discrete colormap for categories
        if attribute == 'land_use': # Assign colors to each point based on land use (special case)
            data["color"] = data[attribute].map(GLOBALS.LAND_USE_COLOR_MAPPING).fillna("gray")
    else:
        cmap = 'viridis'  # continuous colormap for ranges

    
    data.plot(ax=ax, kind='geo', column=attribute, cmap=cmap, legend=True, markersize=30, categorical=categorical, marker='o')

    # set title and axis labels using FS
    ax.set_title("Sample Sites in France by " + attribute_alias, fontsize=FONTSIZE)
    ax.set_xlabel("Longitude", fontsize=FONTSIZE)
    ax.set_ylabel("Latitude", fontsize=FONTSIZE)
    if bounds is not None:
        ax.set_xlim(bounds[0], bounds[1])
        ax.set_ylim(bounds[2], bounds[3])

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

def plot_rmqs_with_regions(data: gpd.GeoDataFrame, regions_file, region_col, alias):#show a map with points and regions
    """plot rmqs points and regions from a shapefile"""

    regions = gpd.read_file(regions_file)[[region_col, "geometry"]]
    if data.crs != regions.crs:
        regions = regions.to_crs(data.crs)
    
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8,8))
    ax = box_to_france(ax, crs=regions.crs)

    # color regions by code and show a legend; fall back to a simple grey fill
    #remove regions that do not appear in xlim and ylim
    visible_regions = regions.cx[GLOBALS.FRANCE_BOX_EPSG_2154[0]:GLOBALS.FRANCE_BOX_EPSG_2154[2], GLOBALS.FRANCE_BOX_EPSG_2154[1]:GLOBALS.FRANCE_BOX_EPSG_2154[3]]
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
    data.plot(
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
    #plot_rmqs_with_regions(GLOBALS.EEA_SHP_BIOREGION_PATH, "code", "bioregion")
    subdata = data[data["bioregion"].isna()]
    plot_rmqs_with_attribute(subdata, "ph_eau_6_1", "soil_ph_nobioregion", 
                             False, None, bounds = [0.8e6,0.9e6,6.2e6,6.3e6],
                             background=GLOBALS.EEA_BIOREGION_BORDERS_PATH)
    #plot_rmqs_with_regions(GLOBALS.ECOREGIONS_PATH, "ECO_NAME", "ecoregion")

"""
    ("signific_ger_95", 'soil_type'),
    ("parent_material", 'parent_material'),
    ("desc_code_occupation3", 'land_use_fine'),
    ("land_use", 'land_use'),
    ("wrb_guess", 'soil_class'),
    ("bioregion", 'bioregion'),
    ("ph_eau_6_1", "soil_ph", False, None)
"""