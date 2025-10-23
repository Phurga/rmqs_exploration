import geopandas as gpd
import rasterio
from rasterio import mask
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np  # Import numpy

from GLOBALS import HILDA_LAND_USE_PATH, FRANCE_BORDERS_PATH, FRANCE_HILDA_LAND_USE_PATH
from utilities import save_fig


def clip_to_france():
    # Load the raster data
    hilda_raster = rasterio.open(HILDA_LAND_USE_PATH)
    hilda_crs = hilda_raster.crs

    # Load the world borders
    france = gpd.read_file(FRANCE_BORDERS_PATH).to_crs(hilda_crs)

    # Clip the raster data to France's borders
    try:
        hilda_image, hilda_transform = mask.mask(hilda_raster, france.geometry, crop=True)
        hilda_image = hilda_image[0]  # Remove the extra dimension
    except ValueError as e:
        print(f"Error during clipping: {e}")
        return
    
    profile = hilda_raster.profile
    profile.update(
        driver="GTiff",
        dtype=hilda_image.dtype,
        height=hilda_image.shape[0],
        width=hilda_image.shape[1],
        transform=hilda_transform,
        count=1  # Ensure the count is 1
    )

    with rasterio.open(r"results\land_use_france.tif", "w", **profile) as dest:
        dest.write(hilda_image, 1)

    return hilda_image, hilda_transform

def plot_hilda_land_use_with_france():
    # Load the world borders
    hilda_image = rasterio.open(FRANCE_HILDA_LAND_USE_PATH)
    
    # Define color map for land use classes
    cmap = {
        11: 'forestgreen',  # Naturally regenerating forest without human activities
        20: 'darkgreen',     # Naturally regenerating forest with human activities
        31: 'lightgreen',    # Planted forest
        32: 'yellowgreen',   # Short rotation plantations
        40: 'darkkhaki',      # Oil palm plantations
        53: 'saddlebrown'     # Agroforestry
    }

    # Convert land use IDs to colors
    color_image = np.zeros((hilda_image.shape[0], hilda_image.shape[1], 3), dtype=np.uint8)
    for land_use_id, color in cmap.items():
        color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))  # Convert hex to RGB
        color_image[hilda_image == land_use_id] = color_rgb

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 12))

    # Set plot title and labels
    ax.set_title('HILDA Land Use with France Borders')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # Show the plot
    save_fig(fig, "map", "france_hilda_land_use")

if __name__ == "__main__":
    #hilda_image, hilda_transform = clip_to_france()
    plot_hilda_land_use_with_france()