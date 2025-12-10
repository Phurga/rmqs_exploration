from pathlib import Path
import pandas as pd
import geopandas as gpd

import GLOBALS
from utilities import load_data, generate_rmqs_geodataframe

def add_region(shp_path: Path, shp_col: str, out_col: str, out_file: Path) -> pd.DataFrame:
    """Assign bioregions or ecoregions to RMQS sample sites based on a shapefile."""
    rmqs_pts = generate_rmqs_geodataframe(load_data())

    # load polygons and reproject points to polygon CRS
    regions = gpd.read_file(shp_path)
    if rmqs_pts.crs != regions.crs:
        regions = regions.to_crs(rmqs_pts.crs)

    regions[out_col] = regions[shp_col] # renaming
    
    # spatial join to assign regions
    joined = gpd.sjoin(rmqs_pts, regions[[out_col, "geometry"]], how="left", rsuffix = None)
    print(f"Removing {len(joined[joined[out_col].isna()])} points falling outside bioregion boundaries.")
    joined = joined[joined[out_col].isna() == False] #remove points without regions found (fell in beaches and sea)
    
    # save output
    joined[[ "x_theo", "y_theo", out_col]].to_csv(out_file, encoding="utf-8")
    print(f"Wrote: {GLOBALS.OUT_DIR / f'{out_col}_assignment.csv'}")
    return joined


if __name__ == "__main__":
    add_region(GLOBALS.EEA_SHP_BIOREGION_PATH, shp_col="code", out_col="bioregion", out_file = GLOBALS.RMQS_BIOREGION_CSV_PATH)
    add_region(GLOBALS.ECOREGIONS_PATH, shp_col="ECO_NAME", out_col="ecoregion", out_file = GLOBALS.RMQS_ECOREGION_CSV_PATH)