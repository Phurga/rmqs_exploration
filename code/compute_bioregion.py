from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

from GLOBALS import BIOREGION_RMQS_PATH, EEA_SHP_BIOREGION_PATH
from utilities import load_data

def add_bioregion(
    metadata_df: pd.DataFrame,
    shp_path: Path | None = EEA_SHP_BIOREGION_PATH,
    x_col: str = "x_theo",
    y_col: str = "y_theo",
    out_col: str = "bioregion",
) -> pd.DataFrame:
    
    # build points GDF
    rmqs_pts = gpd.GeoDataFrame(
        metadata_df.index,
        geometry=[Point(x, y) for x, y in zip(metadata_df[x_col], metadata_df[y_col])],
        crs="EPSG:2154"  #RGF93 from metadata file
    )

    # load polygons and reproject points to polygon CRS
    regions = gpd.read_file(shp_path)
    if rmqs_pts.crs != regions.crs:
        regions = regions.to_crs(rmqs_pts.crs)

    region_col = "code"
    regions = regions[[region_col, "geometry"]].copy()

    joined = gpd.sjoin(rmqs_pts, regions, how="left")
    joined = joined.set_index("id_site")
    metadata_df[out_col] = joined[region_col]
    return metadata_df

def main():
    df = load_data()
    df = add_bioregion(df)
    out_csv = BIOREGION_RMQS_PATH
    df[[ "x_theo", "y_theo", "bioregion"]].to_csv(out_csv, encoding="utf-8")
    print(f"Wrote: {out_csv}")

if __name__ == "__main__":
    main()