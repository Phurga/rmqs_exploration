from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

from GLOBALS import SAMPLE_METADATA_PATH, BIOREGION_RMQS_PATH, EEA_SHP_BIOREGION_PATH
from utilities import load_data

def _guess_points_crs(df: pd.DataFrame, x_col="x_theo", y_col="y_theo") -> str:
    xmax, ymax = df[x_col].abs().max(), df[y_col].abs().max()
    if xmax <= 180 and ymax <= 90:
        return "EPSG:4326"      # lon/lat
    return "EPSG:2154"          # Lambert-93 (RMQS coords)


def _pick_region_column(gdf: gpd.GeoDataFrame) -> str:
    for col in ["BIOREGION", "NAME", "Region", "region", "BIO_NAME", "LEGEND", "legend"]:
        if col in gdf.columns:
            return col
    # fallback: first object dtype column
    obj_cols = [c for c in gdf.columns if gdf[c].dtype == "object" and c != "geometry"]
    if not obj_cols:
        raise ValueError("Could not find a suitable name column in the EEA layer")
    return obj_cols[0]

def add_bioregion(
    metadata_df: pd.DataFrame,
    shp_path: Path | None = EEA_SHP_BIOREGION_PATH,
    x_col: str = "x_theo",
    y_col: str = "y_theo",
    out_col: str = "biogeo_region",
) -> pd.DataFrame:
    
    # clean coords
    pts = metadata_df[[x_col, y_col]].copy()
    pts[x_col] = pd.to_numeric(pts[x_col], errors="coerce")
    pts[y_col] = pd.to_numeric(pts[y_col], errors="coerce")
    pts = pts.dropna()
    pts.index = metadata_df.loc[pts.index].index  # keep id_site

    # build points GDF
    crs_pts = _guess_points_crs(pts, x_col, y_col)
    gdf_pts = gpd.GeoDataFrame(
        pts,
        geometry=[Point(x, y) for x, y in zip(pts[x_col], pts[y_col])],
        crs=crs_pts,
    )

    # load polygons and reproject points to polygon CRS
    regions = gpd.read_file(shp_path)
    if gdf_pts.crs != regions.crs:
        gdf_pts = gdf_pts.to_crs(regions.crs)

    region_col = _pick_region_column(regions)
    regions = regions[[region_col, "geometry"]].copy()

    joined = gpd.sjoin(gdf_pts, regions, how="left", predicate="within")
    out = metadata_df.copy()
    out[out_col] = joined[region_col].reindex(out.index)

    return out

def main():
    df = load_data(filter_columns=["x_theo", "y_theo"])
    df = add_bioregion(df)
    out_csv = BIOREGION_RMQS_PATH
    df[[ "x_theo", "y_theo", "bioregion"]].to_csv(out_csv, encoding="utf-8")
    print(f"Wrote: {out_csv}")

if __name__ == "__main__":
    main()