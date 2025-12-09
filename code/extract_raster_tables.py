import json
from osgeo import gdal # find gdal package here: https://github.com/cgohlke/geospatial-wheels/releases

import GLOBALS

def load_raster_attribute_table(input_raster_path):
    """Load the raster attribute table from a raster file."""
    raster = gdal.Open(input_raster_path)
    rat = raster.GetRasterBand(1).GetDefaultRAT()
    return rat

def extract_raster_table(rat, output_json_path, value_band, label_band):
    """Extract raster attribute table from a raster and save as JSON mapping."""
    mapping = {}
    for r in range(rat.GetRowCount()):
        val = rat.GetValueAsDouble(r, value_band)
        lab = rat.GetValueAsString(r, label_band)
        mapping[int(val)] = lab
    
    json.dump(mapping, open(output_json_path, "w"))
    return mapping


def print_raster_table(rat):
    """Print the raster attribute table.
    The CORINE raster RAT has the following structure (band index, name, type, usage):
    0 Value 0 5
    1 Count 1 0
    2 LABEL3 2 0
    3 Red 0 6
    4 Green 0 7
    5 Blue 0 8
    6 CODE_18 2 0
    """
    for i in range(rat.GetColumnCount()):
        name = rat.GetNameOfCol(i)
        col_type = rat.GetTypeOfCol(i)      
        usage = rat.GetUsageOfCol(i)
        print("index, nome, type, usage")
        print(i, name, col_type, usage)
    return None

if __name__ == "__main__":
    rat = load_raster_attribute_table(GLOBALS.CORINE_PATH)
    print_raster_table(rat)
    extract_raster_table(
        rat=rat,
        output_json_path=GLOBALS.CORINE_CLASS_MAPPING_PATH,
        value_band=0,
        label_band=2
    )