import rasterio
import matplotlib.pyplot as plt
from shapely import total_bounds

from utilities import (
    save_fig, generate_rmqs_geodataframe, 
    plot_geodf_on_raster, sample_raster_to_geodataframe)
import GLOBALS

def primary_from_corine():
    """Generate a csv containing the identified land use from corine for the rmqs dataset"""
    # Load RMQS and corine bound to france
    rmqs = generate_rmqs_geodataframe()
    with rasterio.open(GLOBALS.CORINE_PATH) as corine:
        rmqs = rmqs.to_crs(corine.crs) #RMQS: EPSG2154, CORINE: EPSG3035
        
        # Plot RMQS points over CORINE land use raster
        plot_geodf_on_raster(raster=corine, geodf=rmqs, filename="corine_rmqs", attribute="land_use")
        
        # Overlay RMQS points on CORINE raster to extract land use classes
        corine_attribute_name = 'corine_land_use'
        rmqs[corine_attribute_name] = sample_raster_to_geodataframe(rmqs, corine)

        
        # Convert land use codes to descriptive names
        import json
        with open(GLOBALS.CORINE_CLASS_MAPPING_PATH) as f:
            corine_class_mapping = json.load(f)
            rmqs[corine_attribute_name] = rmqs[corine_attribute_name].astype(str).map(corine_class_mapping)

            # Plot distribution of CORINE land use classes in RMQS points
            fig2, ax2 = plt.subplots(figsize=(10,10))
            data_plot = rmqs[corine_attribute_name].value_counts()
            ax2.barh(data_plot.index, data_plot.values)
            save_fig(fig2, "plot", "corine_with_rmqs")
        return None


if __name__ == "__main__":
    primary_from_corine()
