import rasterio
import rasterio.mask as rmask
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Polygon, MultiPolygon
import numpy as np

import GLOBALS

def from_gdf_to_list_polygons(gdf: gpd.GeoDataFrame) -> list[Polygon]:
    """ Adapted to fr.geojson having only one geometry that is a multipolygon"""
    geometries: MultiPolygon = gdf.loc[0, "geometry"]
    return [geom for geom in geometries.geoms]

def mask_raster_to_vector(
    raster_path: Path, 
    vector_path: Path,
    ) -> tuple[np.ndarray, dict]:
    vector = gpd.read_file(vector_path)
    with rasterio.open(raster_path, 'r') as raster:
        vector.to_crs(raster.crs, inplace=True) #reproject vector to raster crs
        shapes = from_gdf_to_list_polygons(vector)
        out_image, out_transform = rmask.mask(raster, shapes)
        out_meta: dict = raster.meta

    out_meta.update({"driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform})
    return out_image, out_meta

def write_raster(image: np.ndarray, meta: dict, outfile: Path):
    with rasterio.open(outfile, "w", **meta) as dest:
        print(f"Writing {outfile}")
        dest.write(image)
    return None


if __name__ == '__main__':
    #perform for wrb on france
    image, meta = mask_raster_to_vector(
        raster_path = GLOBALS.WRB_LVL1_PATH,
        vector_path = GLOBALS.FRANCE_BORDERS_PATH
    )
    write_raster(image, meta, GLOBALS.WRB_LV1_FRANCE_PATH)