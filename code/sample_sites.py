import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from pathlib import Path

DEFAULT_META = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\data\RMQS1_occupation_nommatp_nomsol_23_03_2022.csv")

# Load metadata, use only necessary columns, and drop rows with missing coordinates
metadata_df = pd.read_csv(
    DEFAULT_META,
    index_col="id_site",
    encoding="windows-1252",
    usecols=["id_site", "x_theo", "y_theo"],
).dropna()

# Convert coordinates to numeric
metadata_df['x_theo'] = pd.to_numeric(metadata_df['x_theo'], errors='coerce')
metadata_df['y_theo'] = pd.to_numeric(metadata_df['y_theo'], errors='coerce')
metadata_df.dropna(inplace=True)

# Determine CRS based on coordinate values
if (metadata_df['x_theo'].abs().max() <= 180) and (metadata_df['y_theo'].abs().max() <= 90):
    input_crs = "EPSG:4326"  # Lon/Lat
else:
    input_crs = "EPSG:2154"  # Lambert-93

# Create GeoDataFrame
gdf_pts = gpd.GeoDataFrame(
    metadata_df,
    geometry=[Point(x, y) for x, y in zip(metadata_df['x_theo'], metadata_df['y_theo'])],
    crs=input_crs,
)

# Convert to EPSG:4326 if necessary
if gdf_pts.crs != "EPSG:4326":
    gdf_pts = gdf_pts.to_crs("EPSG:4326")

# Load France geometry and clip to bounds
world = gpd.read_file("https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson")
france = world[world["name"] == "France"].copy()  # Avoid SettingWithCopyWarning
france = france.clip(gdf_pts.total_bounds)

# Plotting
fig, ax = plt.subplots(figsize=(10, 8))
france.plot(ax=ax, color="#f0f0f0", edgecolor="k")
gdf_pts.plot(ax=ax, markersize=15, color="tab:red", alpha=0.7, linewidth=0)

ax.set_title("Sample Sites in France")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_xlim(gdf_pts.bounds.minx.min() - 1, gdf_pts.bounds.maxx.max() + 1)
ax.set_ylim(gdf_pts.bounds.miny.min() - 1, gdf_pts.bounds.maxy.max() + 1)

plt.tight_layout()
out = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\results\sample_sites_france.png")
fig.savefig(out, dpi=300)