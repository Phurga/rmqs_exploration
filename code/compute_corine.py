import rasterio
import rasterstats 
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import json

from utilities import save_fig, write_csv, load_rmqs_data
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

def map_rmqs_to_corine_land_use(data: pd.DataFrame) -> pd.DataFrame:
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


if __name__ == "__main__":
    data = load_rmqs_data()
    map_rmqs_to_corine_land_use(data)