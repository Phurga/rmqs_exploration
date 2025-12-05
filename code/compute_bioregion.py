from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

from GLOBALS import BIOREGION_RMQS_PATH, EEA_SHP_BIOREGION_PATH
from utilities import load_data, save_fig

def add_bioregion(
    metadata_df: pd.DataFrame,
    shp_path: Path | None = EEA_SHP_BIOREGION_PATH,
    x_col: str = "x_theo",
    y_col: str = "y_theo",
    out_col: str = "bioregion",
) -> pd.DataFrame:
    
    # build points GDF and include metadata (so we can color by attributes like 'land_use')
    rmqs_pts = metadata_df.copy()
    rmqs_pts["geometry"] = [Point(x, y) for x, y in zip(metadata_df[x_col], metadata_df[y_col])]
    rmqs_pts = gpd.GeoDataFrame(rmqs_pts, geometry="geometry", crs="EPSG:2154")  # RGF93 from metadata file

    # load polygons and reproject points to polygon CRS
    regions = gpd.read_file(shp_path)
    if rmqs_pts.crs != regions.crs:
        regions = regions.to_crs(rmqs_pts.crs)

    region_col = "code"
    regions = regions[[region_col, "geometry"]].copy()

    joined = gpd.sjoin(rmqs_pts, regions, how="left")
    metadata_df[out_col] = joined[region_col]

    #show a map with points and regions
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8,8))
    # create categorical color mapping for regions
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D

    region_vals = list(regions[region_col].dropna().unique())
    n_regions = len(region_vals)
    region_cmap = plt.cm.get_cmap("Pastel1", max(1, n_regions))
    region_color_map = {val: region_cmap(i) for i, val in enumerate(region_vals)}

    # apply colors to regions (NaN -> lightgrey)
    regions_colors = regions[region_col].map(lambda v: region_color_map.get(v, (0.9, 0.9, 0.9, 1.0)))
    regions.plot(ax=ax, facecolor=regions_colors, edgecolor="black", zorder=1)

    # build legend handles for regions
    region_handles = [Patch(facecolor=region_color_map[val], edgecolor="black", label=str(val)) for val in region_vals]

    # plot points on top, color-coded by 'land_use' when available
    land_vals = list(rmqs_pts["land_use"].fillna("Unknown").unique())
    n_land = len(land_vals)
    land_cmap = plt.cm.get_cmap("Dark2", max(1, n_land))
    land_color_map = {val: land_cmap(i) for i, val in enumerate(land_vals)}
    pts_colors = rmqs_pts["land_use"].fillna("Unknown").map(lambda v: land_color_map.get(v))
    rmqs_pts.plot(ax=ax, color=pts_colors.tolist(), markersize=20, edgecolor="black", alpha=0.9, zorder=5)

    # build legend handles for points (use Line2D for markers)
    point_handles = [Line2D([0], [0], marker='o', color='w', markerfacecolor=land_color_map[val], markeredgecolor='black', markersize=8, linestyle='None', label=str(val)) for val in land_vals]

    # add legends: points in upper right, regions in lower right
    leg_points = ax.legend(handles=point_handles, title='land_use', loc='upper right', fontsize=8)
    ax.add_artist(leg_points)
    ax.legend(handles=region_handles, title='bioregion', loc='lower right', fontsize=8)

    ax.set_title("RMQS points and biogeographical regions")
    #set limits to France
    ax.set_xlim(0e6, 1.1e6)
    ax.set_ylim(6.0e6, 7.25e6)
    save_fig(fig, "map", "rmqs_points_bioregions")

    return metadata_df

def main():
    df = load_data()
    df = add_bioregion(df)
    out_csv = BIOREGION_RMQS_PATH
    df[[ "x_theo", "y_theo", "bioregion"]].to_csv(out_csv, encoding="utf-8")
    print(f"Wrote: {out_csv}")

if __name__ == "__main__":
    main()