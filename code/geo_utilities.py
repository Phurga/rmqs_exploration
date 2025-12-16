import matplotlib.pyplot as plt
import rasterio.io as rio
import rasterio.plot as rplot
import rasterio.windows as rwindows
import geopandas as gpd
import numpy as np
import pandas as pd

import GLOBALS
from utilities import save_fig

def check_crs(item1, item2):
    """items can be rasters or gpd.DataFrames, .crs works the same"""
    if item1.crs != item2.crs: 
        raise ValueError("Combination of geographical elements with different crs.")
    return None

def read_corine_on_window(window: rwindows.Window) -> np.ndarray:
    with open(GLOBALS.CORINE_LANDUSE_PATH) as corine:
        return corine.read(1, window=window)

def box_to_france(ax, crs):
    """Bound a ax to France extent"""
    match crs:
        case "EPSG:2154":  
            bounds = GLOBALS.FRANCE_BOX_EPSG_2154
        case "EPSG:3035":
            bounds = GLOBALS.FRANCE_BOX_EPSG_3035
        case "IGNF:ETRS89LAEA":
            bounds = GLOBALS.FRANCE_BOX_EPSG_3035
    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    return ax

def plot_geodataframe_on_raster(raster: rio.DatasetReader,
                         geodf: gpd.GeoDataFrame,
                         filename: str,
                         attribute: str = None,
                         band_index: int = 1) -> plt.Figure:
    """
    Creates a figure overlapping a raster and a gpd.DataFrame.
    Geometry will be plotted with an attribute.
    
    :param raster: rasterio.io.Datasetreader, used instead of a band because thus i can test the crs and define the window based on the geodf
    :param geodf: gpd.DataFrame.gpd.DataFrame
    :param attribute: attribute identifier (column name)
    """
    check_crs(raster, geodf)
    geodf_window = rwindows.from_bounds(*geodf.total_bounds, transform=raster.transform)
    band = raster.read(band_index, window=geodf_window)
    fig, ax = plt.subplots(figsize=(10,10))
    rplot.show(source=band, transform=raster.window_transform(geodf_window), ax=ax)
    geodf.plot(ax=ax, column=attribute, zorder=2, legend=True, markersize=15)
    save_fig(fig, "map", filename)
    return fig

def get_rmqs_gdf_from_df(data: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Generate a gpd.DataFrame from a pd.DataFrame containing x and y coordinates
    default settings are adapted to RMQS, whose CRS is RGF93 (EPSG:2154)."""
    return gpd.GeoDataFrame(
        data, 
        geometry=gpd.points_from_xy(data['x_theo'], data['y_theo']), 
        crs=GLOBALS.CRS_RMQS)

def sample_raster_to_geodataframe(geodf: gpd.GeoDataFrame,
                                  raster: rio.DatasetReader,
                                  band_index: int = 0) -> pd.Series:
    """
    Takes in a geodf and a raster, 
    returns a pd.Series aligned with the geodf,
    Retrieves an information stored in the raster at each point in the geodf.
    rasterio.sample does not take geometry object and needs work.
    """
    check_crs(raster, geodf)
    series = pd.Series()
    for idx, geometry in zip(geodf.index, geodf.geometry):
        coords = [(geometry.x, geometry.y)]
        for val in raster.sample(coords):
            series.at[idx] = val[band_index]
    return series