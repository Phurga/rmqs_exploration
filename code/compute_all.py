from geopandas import GeoDataFrame
from pandas import read_csv

import GLOBALS
from utilities import add_geometries, rename_land_use, write_csv
from compute_otu_metrics import compute_otu_metrics
from compute_bioregion import compute_bioregion
from compute_wrb_class import compute_WRB_class
from compute_cf import compute_land_use_cf_median_context

def compute_all() -> GeoDataFrame:
    """ Either loads data from csv file or updates it from raw files."""
    data_file = GLOBALS.FULL_DATASET_PATH

    #initial read of the RMQS sample database
    data = read_csv(GLOBALS.RMQS_LANDUSE_PATH, index_col='id_site', encoding=GLOBALS.ENCODING_RMQS, na_values=['ND'])
    data = data[data['site_officiel']]
    data = rename_land_use(data)
    data = add_geometries(data) # transforms the dataframe into a geodataframe (ie adds a geometry column and some attributes)
    #data = add_soil_properties(data)
    #data = add_soil_metadata(data)

    # add self made data
    data = compute_otu_metrics(data)
    data = compute_bioregion(data) # add bioregion
    data = compute_WRB_class(data) # add wrb lvl 1 class
    data= compute_land_use_cf_median_context(data) # add cf

    write_csv(data, data_file)
    return data

if __name__ == '__main__':
    compute_all()