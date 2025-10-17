import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from pathlib import Path

from src.GLOBALS import DEFAULT_META

# use existing metadata_df (index = id_site) and expect columns x_theo, y_theo
metadata_df = pd.read_csv(DEFAULT_META, index_col="id_site", encoding="windows-1252")
pts = metadata_df[['x_theo', 'y_theo']].dropna().copy()
if pts.empty:
    raise RuntimeError("No x_theo / y_theo coordinates found in metadata_df")

# ensure numeric
pts['x_theo'] = pd.to_numeric(pts['x_theo'], errors='coerce')
pts['y_theo'] = pd.to_numeric(pts['y_theo'], errors='coerce')
pts = pts.dropna()

# guess input CRS: if coordinates look like degrees (lon/lat) use EPSG:4326,
# otherwise assume French projection (Lambert-93 EPSG:2154) and convert to 4326 for plotting
if (pts['x_theo'].abs().max() <= 180) and (pts['y_theo'].abs().max() <= 90):
    input_crs = "EPSG:4326"
else:
    input_crs = "EPSG:2154"

gdf_pts = gpd.GeoDataFrame(
    pts,
    geometry=[Point(x, y) for x, y in zip(pts['x_theo'], pts['y_theo'])],
    crs=input_crs,
)

# convert to lon/lat for plotting with Natural Earth
if gdf_pts.crs.to_string() != "EPSG:4326":
    gdf_pts = gdf_pts.to_crs("EPSG:4326")

# load France geometry (Natural Earth low-res provided by geopandas)
world = gpd.read_file("https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson")
france = world[world["name"] == "France"]

# plot
fig, ax = plt.subplots(figsize=(8, 10))
france.plot(ax=ax, color="#f0f0f0", edgecolor="k")
gdf_pts.plot(ax=ax, markersize=15, color="tab:red", alpha=0.7, linewidth=0)

ax.set_title("Sample sites (x_theo, y_theo) — France")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# zoom to France extent with small margin
xmin, ymin, xmax, ymax = france.total_bounds
pad_x = (xmax - xmin) * 0.05
pad_y = (ymax - ymin) * 0.05
ax.set_xlim(xmin - pad_x, xmax + pad_x)
ax.set_ylim(ymin - pad_y, ymax + pad_y)

plt.tight_layout()
out = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\results\sample_sites_france.png")
fig.savefig(out, dpi=300)