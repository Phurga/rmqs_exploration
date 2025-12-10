from utilities import (
    save_fig, generate_rmqs_geodataframe, 
    plot_geodf_on_raster, sample_raster_to_geodataframe,
    relabel_bottom)
import rasterio
import GLOBALS
import geopandas as gpd 
import pandas as pd

def get_WRB_mapping():
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
        return WRB_number_to_txt

def compute_WRB_class():
    rmqs = generate_rmqs_geodataframe()
    with rasterio.open(GLOBALS.WRB_LVL1_PATH) as wrb: #EPSG3035
        rmqs = rmqs.to_crs(wrb.crs)
        plot_geodf_on_raster(wrb, rmqs, "wrb_rmqs")
        
        rmqs['WRB_LVL1'] = sample_raster_to_geodataframe(rmqs, wrb)
        
        wrb_mapping = get_WRB_mapping()
        with open("results/WRB_mapping.json", "w") as f:
            print("Writing results/WRB_mapping.json")
            from json import dump
            dump(wrb_mapping, f)
        rmqs['WRB_LVL1'] = rmqs['WRB_LVL1'].map(wrb_mapping)
        rmqs["WRB_LVL1"] = relabel_bottom(rmqs["WRB_LVL1"], cutoff_quantile=0.97) #quantile defined to cutoff after Podzol (see below)
        with open(GLOBALS.WRB_CLASS_RMQS_PATH, "w") as f:
            print(f"Writing {GLOBALS.WRB_CLASS_RMQS_PATH}")
            rmqs["WRB_LVL1"].to_csv(f) 
    return rmqs

if __name__ == '__main__':
    compute_WRB_class()

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