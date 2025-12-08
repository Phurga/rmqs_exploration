import rasterio
import rasterio.plot
import matplotlib.pyplot as plt
from shapely import total_bounds

from utilities import save_fig, generate_rmqs_geodataframe
import GLOBALS

def primary_from_corine():
    
    """Plot RMQS points over CORINE land use raster."""
    # Load RMQS and corine bound to france
    rmqs = generate_rmqs_geodataframe()
    corine = rasterio.open(GLOBALS.CORINE_PATH)
    if rmqs.crs != corine.crs: #convert rmqs to corine crs to get the right bounds in the window
        rmqs = rmqs.to_crs(corine.crs)
    
    # Plot RMQS points over CORINE land use raster
    def plot_geodf_on_raster(raster, geodf, column):
        geodf_window = rasterio.windows.from_bounds(*geodf.total_bounds, transform=raster.transform)
        band = raster.read(1, window=geodf_window)
        fig, ax = plt.subplots(figsize=(10,10))
        rasterio.plot.show(source=band, transform=raster.window_transform(geodf_window), ax=ax)
        geodf.plot(ax=ax, column=column, zorder=2, legend=True, markersize=15)
        return fig
    fig = plot_geodf_on_raster(raster=corine, geodf=rmqs, column="land_use")
    save_fig(fig, "map", "corine_with_rmqs")
    
    # Overlay RMQS points on CORINE raster to extract land use classes
    corine_attribute_name = "corine_land_use"
    rmqs[corine_attribute_name] = None
    for idx, row in rmqs.iterrows():
        coords = [(row.geometry.x, row.geometry.y)]
        for val in corine.sample(coords):
            rmqs.at[idx, corine_attribute_name] = val[0]
    
    # Convert land use codes to descriptive names
    import json
    corine_class_mapping = json.load(open(GLOBALS.CORINE_CLASS_MAPPING_PATH))
    rmqs[corine_attribute_name+"_code"] = rmqs[corine_attribute_name]
    rmqs[corine_attribute_name] = rmqs[corine_attribute_name].astype(str).map(corine_class_mapping)

    # Plot distribution of CORINE land use classes in RMQS points
    fig2, ax2 = plt.subplots(figsize=(10,10))
    data_plot = rmqs[corine_attribute_name].value_counts()
    ax2.barh(data_plot.index, data_plot.values)
    save_fig(fig2, "plot", "corine_with_rmqs")
    return None


if __name__ == "__main__":
    primary_from_corine()
