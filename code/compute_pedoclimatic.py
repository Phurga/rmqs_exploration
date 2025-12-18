import GLOBALS
import json
import geopandas as gpd
import rasterstats
import pandas as pd
from pathlib import Path
        
def compute_pedoclimatic_mix_france() -> pd.DataFrame:
    """
    Get the mix of pedoclimatic in France from a climatic region vector map and a soil class raster map
    """
    # prepare bioregion vector file into a geodataframe containing only climate zone name and its geometries
    bioregions_france = gpd.read_file(GLOBALS.BIOREGION_FRANCE_PATH).set_index(keys='code')
    bioregions_france = bioregions_france["geometry"]
    
    # prepare soil class raster file
    with open(GLOBALS.WRB_FINAL_MAPPING_PATH) as file:
        mapping = json.load(file)
        mapping = {int(key): mapping[key] for key in mapping}
    
    # compute zonal stastics, here a zonal histogram
    # stats returns a list of geojson, one element corresponds to one climate zone
    # one element contains a properties item containing the histogram of soil classes
    stats = rasterstats.zonal_stats(
        vectors=bioregions_france,
        raster=GLOBALS.WRB_LV1_FRANCE_PATH,
        categorical=True,
        category_map=mapping,
        geojson_out=True)
    
    # convert the stats geojsons into tabular data with index being climate and soil_class, i.e. the pedoclimatic region 
    pedoclimatic_data = []
    for climate_mix in stats:
        climate = climate_mix['id']
        for soil_class, pixelcount in climate_mix['properties'].items():
            pedoclimatic_data.append([climate, soil_class, pixelcount])
    pedoclimatic_data = pd.DataFrame(pedoclimatic_data, columns=['climate', 'soil_class', 'pixel_count']).set_index(['climate', 'soil_class'])
    pedoclimatic_data['relative_pixel_count'] = pedoclimatic_data['pixel_count'] / pedoclimatic_data['pixel_count'].sum()
    pedoclimatic_data.sort_values(by='relative_pixel_count', ascending=False, inplace=True)

    # write in disk
    outfile = GLOBALS.PEDOCLIM_STATS_PATH
    print(f'Writing {outfile}')
    pedoclimatic_data.to_csv(outfile)

    return pedoclimatic_data

if __name__ == "__main__":
    compute_pedoclimatic_mix_france()
    