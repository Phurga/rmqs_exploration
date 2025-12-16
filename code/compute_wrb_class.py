import rasterio
import geopandas as gpd 
import pandas as pd

import utilities
import geo_utilities
import GLOBALS

def get_WRB_numeric_to_text_mapping():
        """
        Read the WRB text file and return a dict mapping code to name.
        Lines that do not contain a code name pair are ignored.
        """
        from numpy import nan
        #get number to code (7 > AB)
        WRB_number_to_code = dict(
                gpd.read_file(GLOBALS.WRB_LVL1_MAPPING_PATH).set_index('VALUE')['WRBLV1'])
        # get code to txt (AB > Albeluvisol)
        WRB_code_to_txt = {}
        with open(GLOBALS.WRB_LVL1_NAMES_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("-") or line.startswith("WRB"):
                    continue
                parts = line.split(None, 1)  # split on first whitespace
                if len(parts) == 2:
                    code, name = parts
                    WRB_code_to_txt[code] = name
        #merge to get number to txt (7 > Albeluvisol)
        WRB_number_to_txt = {
            key:WRB_code_to_txt[value] 
            if len(value) < 3 
            else nan 
            for key, value in WRB_number_to_code.items()}
        # storing the mapping in disk
        with open(GLOBALS.WRB_FINAL_MAPPING_PATH, "w") as f:
            print(f"Writing {GLOBALS.WRB_FINAL_MAPPING_PATH}")
            from json import dump
            dump(WRB_number_to_txt, f)
        return WRB_number_to_txt

def compute_WRB_class(data: gpd.GeoDataFrame):
    """
    Docstring for compute_WRB_class
    
    :param data: Description
    """
    WRB_col_name = 'WRB_LVL1'
    with rasterio.open(GLOBALS.WRB_LVL1_PATH) as wrb: #EPSG3035
        data = data.to_crs(wrb.crs) #reproject the points rather than the raster because reprojecting raster is tricky
        geo_utilities.plot_geodataframe_on_raster(wrb, data, "wrb_rmqs")
        data[WRB_col_name] = geo_utilities.sample_raster_to_geodataframe(data, wrb)

    # convert raster numeric values to text classes
    wrb_mapping = get_WRB_numeric_to_text_mapping()
    data[WRB_col_name] = data[WRB_col_name].map(wrb_mapping)
    data[WRB_col_name] = utilities.relabel_bottom(data["WRB_LVL1"], approach='min_val_count', param=50) #group all soil types together if there are less than 50 sampled points

    with open(GLOBALS.RMQS_WRB_PATH, "w") as f:
        print(f"Writing {GLOBALS.RMQS_WRB_PATH}")
        data[WRB_col_name].to_csv(f)
    return data

if __name__ == '__main__':
    data = utilities.load_rmqs_data()
    compute_WRB_class(data)

"""
>>> print(rmqs['WRB_LVL1'].value_counts().cumsum())
Cambisol       898
Luvisol        255
Leptosol       222
Fluvisol       160
Albeluvisol    108
Podzol          97
Andosol         18
Regosol         13
Town            12
Arenosol        10
Solonchak        7
Water body       4
Histosol         3
Gleysol          3
Planosol         3
Glacier          2
Vertisol         1

>>> print(rmqs['WRB_LVL1'].value_counts(normalize=True).cumsum())
Cambisol       0.494493
Luvisol        0.634912
Leptosol       0.757159
Fluvisol       0.845264
Albeluvisol    0.904736
Podzol         0.958150
Andosol        0.968062
Regosol        0.975220
Town           0.981828
Arenosol       0.987335
Solonchak      0.991189
Water body     0.993392
Histosol       0.995044
Gleysol        0.996696

"""