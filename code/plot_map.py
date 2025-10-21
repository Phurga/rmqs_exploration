import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt

from utilities import load_data, save_fig, relabel_top_n
from GLOBALS import WORLD_PATH, LAND_USE_COLOR_MAPPING

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

def plot_sample_sites(gdf: gpd.GeoDataFrame, group_col: str, alias: str):
    # Load France geometry and clip to bounds
    world = gpd.read_file(WORLD_PATH)
    france = world[world["name"] == "France"].copy()
    france = france.clip(gdf.total_bounds)

    # Assign colors to each point based on land use
    if group_col == 'land_use':
        COLOR_MAP = LAND_USE_COLOR_MAPPING
        gdf["color"] = gdf[group_col].map(COLOR_MAP).fillna("gray")

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 10))  # Adjusted figure size for legend
    france.plot(ax=ax, color="#f0f0f0", edgecolor="k")

    
    # Plot points with color-coding
    #gdf.plot(ax=ax, column=DIMENSION[0], cmap='Set1', legend=True, markersize=50, alpha=0.7, linewidth=0, categorical=True, marker='s',
    #        legend_kwds={'loc': 'center left', 'bbox_to_anchor':(1,0.5), 'ncol': 2})
    gdf.plot(ax=ax, column=group_col, cmap='Set1', legend=True, markersize=50, alpha=0.7, linewidth=0, categorical=True, marker='s')

    ax.set_title("Sample Sites in France by " + alias, fontsize=16)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_xlim(gdf.bounds.minx.min() - 1, gdf.bounds.maxx.max() + 1)
    ax.set_ylim(gdf.bounds.miny.min() - 1, gdf.bounds.maxy.max() + 1)

    plt.tight_layout()
    save_fig(fig, "map", f"france_{alias}")
    return None

def plot_map(metadata_df, group_col, alias, top_n = 9):
    if top_n is not None:
        metadata_df[group_col] = relabel_top_n(metadata_df[group_col], top_n)
    gdf_pts = gdf_definition(metadata_df)
    plot_sample_sites(gdf_pts, group_col, alias)

if __name__ == "__main__":
    [group_col, alias] = ("wrb_guess", 'soil_class')
    metadata_df = load_data()
    plot_map(metadata_df, group_col, alias)

DIMENSIONS = [
    ("signific_ger_95", 'soil_type'),
    ("parent_material", 'parent_material'),
    ("desc_code_occupation3", 'land_use_fine'),
    ("land_use", 'land_use'),
    ("wrb_guess", 'soil_class')
]