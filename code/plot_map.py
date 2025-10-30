import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt

from utilities import load_data, save_fig, relabel_top_n
from GLOBALS import FRANCE_BORDERS_PATH, LAND_USE_COLOR_MAPPING
FS = 24

def gdf_definition(metadata_df: pd.DataFrame):
    # Determine CRS based on coordinate values
    if (metadata_df['x_theo'].abs().max() <= 180) and (metadata_df['y_theo'].abs().max() <= 90):
        input_crs = "EPSG:4326"  # Lon/Lat
    else:
        input_crs = "EPSG:2154"  # Lambert-93

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        metadata_df,
        geometry=[Point(x, y) for x, y in zip(metadata_df['x_theo'], metadata_df['y_theo'])],
        crs=input_crs,
    )

    # Convert to EPSG:4326 if necessary
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    return gdf

def plot_sample_sites_france(gdf: gpd.GeoDataFrame, group_col: str, alias: str, categorical: bool) -> None:
    fig, ax = plt.subplots(figsize=(12, 10))  # Adjusted figure size for legend
    # Load France geometry and clip to bounds
    france = gpd.read_file(FRANCE_BORDERS_PATH).to_crs(gdf.crs)
    france.plot(ax=ax, kind='geo', color='white', edgecolor='black')

    # Choose colormap based on whether the data is categorical or continuous
    if categorical:
        cmap = 'Set1'  # discrete colormap for categories
        if group_col == 'land_use': # Assign colors to each point based on land use (special case)
            gdf["color"] = gdf[group_col].map(LAND_USE_COLOR_MAPPING).fillna("gray")
    else:
        cmap = 'viridis'  # continuous colormap for ranges

    
    gdf.plot(ax=ax, kind='geo', column=group_col, cmap=cmap, legend=True, markersize=30, categorical=categorical, marker='o', legend_kwds={'label': alias})

    # set title and axis labels using FS
    ax.set_title("Sample Sites in France by " + alias, fontsize=FS)
    ax.set_xlabel("Longitude", fontsize=FS)
    ax.set_ylabel("Latitude", fontsize=FS)

    # adjust legend text and title font sizes
    if ax.get_legend() is not None:
        ax.get_legend().set_title(alias, prop={'size': FS})
        for text in ax.get_legend().get_texts():
            text.set_fontsize(FS)
        title = ax.get_legend().get_title()
        if title is not None:
            title.set_fontsize(FS)
    
    plt.tight_layout()
    save_fig(fig, "map", f"france_{alias}")
    return fig

def plot_map(metadata_df, group_col, alias, categorical=True, top_n = 9) -> None:
    if top_n is not None:
        metadata_df[group_col] = relabel_top_n(metadata_df[group_col], top_n)
    gdf_pts = gdf_definition(metadata_df)
    fig = plot_sample_sites_france(gdf_pts, group_col, alias, categorical)
    return fig

if __name__ == "__main__":
    metadata_df = load_data()
    plot_map(metadata_df, "ph_eau_6_1", "soil_ph", False, None)

DIMENSIONS = [
    ("signific_ger_95", 'soil_type'),
    ("parent_material", 'parent_material'),
    ("desc_code_occupation3", 'land_use_fine'),
    ("land_use", 'land_use'),
    ("wrb_guess", 'soil_class'),
    ("bioregion", 'bioregion'),
    ("ph_eau_6_1", "soil_ph", False, None)
]