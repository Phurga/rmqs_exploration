import geopandas as gpd
import rasterio
from rasterio import mask
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np  # Import numpy
import matplotlib.colors

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
    # Load the raster data
    with rasterio.open(FRANCE_HILDA_LAND_USE_PATH) as src:
        hilda_image = src.read(1)  # Read the first band
        hilda_transform = src.transform
        hilda_crs = src.crs
    
    # Define color map for land use classes
    cmap = {
        11: matplotlib.colors.to_rgb('forestgreen'),  # Naturally regenerating forest without human activities
        20: matplotlib.colors.to_rgb('darkgreen'),     # Naturally regenerating forest with human activities
        31: matplotlib.colors.to_rgb('lightgreen'),    # Planted forest
        32: matplotlib.colors.to_rgb('yellowgreen'),   # Short rotation plantations
        40: matplotlib.colors.to_rgb('darkkhaki'),      # Oil palm plantations
        53: matplotlib.colors.to_rgb('saddlebrown')     # Agroforestry
    }

    # Convert the image data to RGB using the color map
    hilda_rgb = np.zeros((hilda_image.shape[0], hilda_image.shape[1], 3), dtype=np.uint8)
    for value, color in cmap.items():
        hilda_rgb[hilda_image == value] = np.array(color)

    # Create a matplotlib figure and axes
    fig, ax = plt.subplots(figsize=(10, 10))

    # Display the RGB image
    ax.imshow(hilda_rgb, transform=hilda_transform)

    ax.set_title('HILDA Land Use in France')
    ax.axis('off')

    # Show the plot
    save_fig(fig, "map", "france_hilda_land_use")

if __name__ == "__main__":
    #hilda_image, hilda_transform = clip_to_france()
    plot_hilda_land_use_with_france()