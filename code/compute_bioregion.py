from pathlib import Path
import geopandas as gpd

import GLOBALS
from utilities import load_rmqs_data

def add_region_to_rmqs(
    rmqs_gdf: gpd.GeoDataFrame,
    shp_path: Path,
    shp_col: str,
    region_name: str,
    out_file: Path,
    ) -> gpd.GeoDataFrame:
    """Assign a region to RMQS sample sites based on a shapefile."""
    # load polygons and reproject points to polygon CRS
    regions_gdf = gpd.read_file(shp_path)
    if rmqs_gdf.crs != regions_gdf.crs:
        regions_gdf = regions_gdf.to_crs(rmqs_gdf.crs)

    regions_gdf[region_name] = regions_gdf[shp_col] # renaming
    
    # spatial join to assign regions
    rmqs_gdf = gpd.sjoin(rmqs_gdf, regions_gdf[[region_name, "geometry"]], how="left", rsuffix = None)
    failed_values = rmqs_gdf[rmqs_gdf[region_name].isna()]
    print(f"Removing {len(failed_values)} points falling outside bioregion boundaries.")
    rmqs_gdf.drop(failed_values.index, inplace=True) #remove points without regions found (fell in beaches and sea)
    
    # Writing and returning
    print(f"Writing: {out_file}")
    rmqs_gdf[region_name].to_csv(out_file)
    return rmqs_gdf

def compute_bioregion(data):
    data = add_region_to_rmqs(data, GLOBALS.EEA_BIOREGION_BORDERS_PATH, shp_col="code", region_name="bioregion", out_file = GLOBALS.RMQS_BIOREGION_CSV_PATH)
    return data

if __name__ == "__main__":
    data = load_rmqs_data()
    add_region_to_rmqs(data, GLOBALS.EEA_BIOREGION_BORDERS_PATH, shp_col="code", region_name="bioregion", out_file = GLOBALS.RMQS_BIOREGION_CSV_PATH)
    add_region_to_rmqs(data, GLOBALS.WWF_ECOREGIONS_BORDERS_PATH, shp_col="ECO_NAME", region_name="ecoregion", out_file = GLOBALS.RMQS_ECOREGION_CSV_PATH)