import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from pathlib import Path

from plot_richness import add_soil_data
from GLOBALS import DEFAULT_META, WORLD_PATH

DIMENSION = ("signific_ger_95", 'soil_type')
DIMENSION = ("parent_material", 'parent_material')
DIMENSION = ("desc_code_occupation3", 'land_use_fine')
DIMENSION = ("land_use", 'land_use')
DIMENSION = ("wrb_guess", 'soil_class')

# Define color mapping for land use types
COLOR_MAP = {
    "friches": "gray",                                     # color code for wastelands
    "milieux naturels particuliers": "lightgreen",      # color code for natural sites
    "parcs et jardins": "green",                         # color code for urban green spaces
    "successions culturales": "yellow",                # color code for annual crops
    "surfaces boisees": "forestgreen",                # color code for woods
    "surfaces toujours en herbe": "lightyellow",      # color code for meadows
    "forets caducifoliees": "darkgreen",             # color code for broadleaves
    "forets de coniferes": "green",                  # color code for coniferous
    "vignes vergers et cultures perennes arbustives": "purple" # color code for permanent crops
}

def load_metadata(top_n: int, column):
    metadata_df = pd.read_csv(
        DEFAULT_META,
        index_col="id_site",
        encoding="windows-1252",
    ).dropna()

    metadata_df = add_soil_data(metadata_df)
    metadata_df = metadata_df[['x_theo', 'y_theo', column]]
    # Convert coordinates to numeric
    metadata_df['x_theo'] = pd.to_numeric(metadata_df['x_theo'], errors='coerce')
    metadata_df['y_theo'] = pd.to_numeric(metadata_df['y_theo'], errors='coerce')
    metadata_df.dropna(inplace=True)

    # Relabel non-top categories as "others" instead of removing rows
    n_unique = metadata_df[column].nunique()
    if top_n is not None and n_unique > top_n:
        top_values = metadata_df[column].value_counts().nlargest(top_n).index
        metadata_df[column] = metadata_df[column].where(
            metadata_df[column].isin(top_values),
            'others'
        )

    return metadata_df

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

def plot_sample_sites(gdf: gpd.GeoDataFrame, COLOR_MAP: dict, dimension):
    # Load France geometry and clip to bounds
    world = gpd.read_file(WORLD_PATH)
    france = world[world["name"] == "France"].copy()
    france = france.clip(gdf.total_bounds)

    # Assign colors to each point based on land use
    gdf["color"] = gdf[DIMENSION[0]].map(COLOR_MAP).fillna("gray")

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 10))  # Adjusted figure size for legend
    france.plot(ax=ax, color="#f0f0f0", edgecolor="k")

    
    # Plot points with color-coding
    #gdf.plot(ax=ax, column=DIMENSION[0], cmap='Set1', legend=True, markersize=50, alpha=0.7, linewidth=0, categorical=True, marker='s',
    #        legend_kwds={'loc': 'center left', 'bbox_to_anchor':(1,0.5), 'ncol': 2})
    gdf.plot(ax=ax, column=DIMENSION[0], cmap='Set1', legend=True, markersize=50, alpha=0.7, linewidth=0, categorical=True, marker='s')

    ax.set_title("Sample Sites in France by Land Use")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_xlim(gdf.bounds.minx.min() - 1, gdf.bounds.maxx.max() + 1)
    ax.set_ylim(gdf.bounds.miny.min() - 1, gdf.bounds.maxy.max() + 1)

    # Add legend
    # ax.legend(title="Land Use", loc="upper right") # handled by gdf_pts.plot

    plt.tight_layout()
    out = Path(fr"c:\Users\aburg\Documents\calculations\rmqs_exploration\results\sample_sites_france_{DIMENSION[1]}.png")
    fig.savefig(out, dpi=300)
    return None

if __name__ == "__main__":
    metadata_df = load_metadata(top_n=9, column=DIMENSION[0])  # optionally pass a different cutoff: load_metadata(top_n=15)
    gdf_pts = gdf_definition(metadata_df)
    plot_sample_sites(gdf_pts, COLOR_MAP, dimension=DIMENSION)
