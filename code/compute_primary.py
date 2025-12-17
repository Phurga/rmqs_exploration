import rasterio
import rasterio.io as rio
import rasterio.windows as rwindows
import rasterstats 
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd

from utilities import save_fig, load_rmqs_data, write_csv
from geo_utilities import plot_geodataframe_on_raster, sample_raster_to_geodataframe
import GLOBALS

def get_class_from_code(series: pd.Series, mapping_file: str):
    import json
    with open(mapping_file) as f:
        mapping = json.load(f)
        return series.astype(str).map(mapping)

def plot_bar_stat_raster(data: pd.DataFrame, outfile: str):
    fig, ax = plt.subplots(figsize=(10,10))
    ax.barh(data.index, data.values)
    save_fig(fig, "bar", outfile)
    return fig

def compute_primary_from_corine(data: pd.DataFrame) -> pd.DataFrame:
    """Generate a csv containing the identified land use from corine for the rmqs dataset"""
    # Load RMQS and corine bound to france
    with rasterio.open(GLOBALS.CORINE_LANDUSE_PATH, 'r') as corine:
        data = data.to_crs(corine.crs) #RMQS: EPSG2154, CORINE: EPSG3035
        
        plot_geodataframe_on_raster(raster=corine, geodf=data, filename="corine_rmqs", attribute="land_use")
        
        # Overlay RMQS points on CORINE raster to extract land use classes
        corine_attribute = 'corine_land_use'
        data[corine_attribute] = sample_raster_to_geodataframe(data, corine)
        data[corine_attribute] = get_class_from_code(data[corine_attribute], GLOBALS.CORINE_CLASS_MAPPING_PATH) #relabel values
        # Plot distribution of CORINE land use classes in RMQS points
        summary_data = data[corine_attribute].value_counts()
        plot_bar_stat_raster(summary_data, "corine_with_rmqs")
        write_csv(summary_data, "corine_land_use.csv")
    return data

def get_france_corine_stats():
    """
    Get the land use cover over france from Corine.
    
    :param data: RMQS sample sites dataframe, with retrieved and computed attributes
    :type data: DataFrame
    """
    france_borders = gpd.read_file(GLOBALS.FRANCE_BORDERS_PATH)
    france_geometry = france_borders['geometry']
    with rasterio.open(GLOBALS.CORINE_LANDUSE_PATH, 'r') as corine:
        france_borders.to_crs(corine.crs, inplace=True)
        france_window = rwindows.from_bounds(*france_borders.total_bounds, transform=corine.transform)
        france_transform = corine.window_transform(france_window)
        rastervalues = corine.read(
            indexes=1,
            window=france_window)
        
    stats = rasterstats.zonal_stats(
        vectors=france_geometry,
        raster=rastervalues,
        affine=france_transform,
        categorical=True,
        stats='count')
        
    return stats
        


if __name__ == "__main__":
    #data = load_rmqs_data()
    #compute_primary_from_corine(data)
    print(get_france_corine_stats())
