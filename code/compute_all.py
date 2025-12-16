from geopandas import GeoDataFrame
import pandas as pd

import GLOBALS
import utilities
from geo_utilities import get_rmqs_gdf_from_df
from compute_otu_metrics import compute_otu_metrics
from compute_bioregion import compute_bioregion
from compute_wrb_class import compute_WRB_class
from compute_cf import compute_land_use_cf_median_context

def compute_all() -> GeoDataFrame:
    """ Either loads data from csv file or updates it from raw files."""
    #initial read of the RMQS sample database
    data = pd.read_csv(GLOBALS.RMQS_LANDUSE_PATH, index_col='id_site', encoding=GLOBALS.ENCODING_RMQS, na_values=['ND'])
    data = data[data['site_officiel']]
    data = utilities.rename_land_use(data)
    data = get_rmqs_gdf_from_df(data) # transforms the dataframe into a geodataframe (ie adds a geometry column and some attributes)
    #data = utilities.add_soil_metadata(data)

    # add self made data
    data = compute_otu_metrics(data)
    data = compute_bioregion(data) # add bioregion
    data = compute_WRB_class(data) # add wrb lvl 1 class
    data = compute_land_use_cf_median_context(data) # add cf

    utilities.write_csv(data, GLOBALS.RMQS_FINAL_CSV_PATH)
    data.to_file(GLOBALS.RMQS_FINAL_GEO_PATH)
    print(f"Wrinting {GLOBALS.RMQS_FINAL_GEO_PATH}")
    return data

if __name__ == '__main__':
    compute_all()