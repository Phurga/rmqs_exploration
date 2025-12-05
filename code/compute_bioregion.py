from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

from GLOBALS import BIOREGION_RMQS_PATH, EEA_SHP_BIOREGION_PATH, ECOREGIONS_PATH
from utilities import load_data, save_fig, box_to_france, generate_rmqs_geodataframe

def add_bioregion(
    data: pd.DataFrame,
    shp_path: Path | None = EEA_SHP_BIOREGION_PATH,
    out_col: str = "bioregion") -> pd.DataFrame:
    
    rmqs_pts = generate_rmqs_geodataframe(data)

    # load polygons and reproject points to polygon CRS
    regions = gpd.read_file(shp_path)
    if rmqs_pts.crs != regions.crs:
        regions = regions.to_crs(rmqs_pts.crs)

    region_col = "code"
    regions = regions[[region_col, "geometry"]].copy()

    joined = gpd.sjoin(rmqs_pts, regions, how="left")
    data[out_col] = joined[region_col]

    return data
    


def main():
    df = load_data()
    df = add_bioregion(df)
    out_csv = BIOREGION_RMQS_PATH
    df[[ "x_theo", "y_theo", "bioregion"]].to_csv(out_csv, encoding="utf-8")
    print(f"Wrote: {out_csv}")

if __name__ == "__main__":
    main()