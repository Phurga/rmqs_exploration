from pathlib import Path

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

import GLOBALS

def add_soil_properties(data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Adding RMQS soil properties to the current sample observation dataframe.
    At each site, several physico chemical analsyses are performed for different soil layers (no_couche), 
    for simplicity we only keep the 2nd layer (sub-surface layer, corresponding to eDNA sampling depth).
    """
    soil_props = pd.read_csv(GLOBALS.RMQS_SOIL_PROPERTIES_PATH, index_col="id_site", 
                             encoding=GLOBALS.ENCODING_RMQS, na_values=["ND"])
    soil_props.drop(data.columns, axis=1, errors="ignore", inplace=True) # ignore attributes already in data
    soil_props = soil_props[soil_props['no_couche'] == 2]
    data = data.merge(soil_props, on='id_site', how="left", validate="1:1")
    return data

def rename_land_use(data: gpd.GeoDataFrame):
    """
    Recreate the custom 'land_use' classification:
    - keep desc_code_occupation1 except for 'surfaces boisees'
    - for 'surfaces boisees' use desc_code_occupation3 but only keep allowed subclasses
    - rows with other forest subclasses are set to NaN (dropped later)
    """
    # renommer toutes les forets qui ne sont pas caducifoliees en coniferes (eg mixte > coniferes)
    def make_custom(row):
        keep1 = "surfaces boisees"
        keep3 = "forets caducifoliees"
        other3 = "forets de coniferes"
        if row["desc_code_occupation1"] == keep1:
            if row["desc_code_occupation3"] == keep3:
                return keep3
            return other3
        return row["desc_code_occupation1"]

    data["land_use"] = data.apply(make_custom, axis=1)
    data["land_use"] = data["land_use"].map(GLOBALS.LAND_USE_SIMPLE_MAPPING)

    #add land use intensity levels
    data["land_use_intensity"] = data["land_use"].map(GLOBALS.LAND_USE_INTENSITY_MAPPING)
    return data

def relabel_bottom(series: pd.Series, 
                   approach: str = "quantile", 
                   param = 0.8, 
                   bottom_label = "Others"
                   ) -> pd.Series:
    """
    Relabel rare values of a series to a grouping label 
    following a given grouping approach.
    Returns the modified series.
    
    
    :param series: Series that will be modified
    :type series: pd.Series
    :param approach: Choice of the approach used to classify rare values among top_cats, quantile, min_val_count
     - 'top_cats' keeps only the "top_n" most populous values based on value counts
     - 'quantile' keeps only categories below a "cutoff_quantile" (default to 0.8)
     - 'min_val_count' keeps only values appearing more than val_count times in the pd.Series.
    :type approach str
    :param param: value of the parameter used in the grouping approach
    :param bottom_label: Name of the new value for rare values
    :return: Modified input series
    :rtype: Series[Any]
    """
    match approach:
        case "top_cats":
            if type(param) is not int:
                raise ValueError("For 'top_cats' approach, param must be an integer.")
            top_n = param
            if series.nunique() > top_n:
                top_values = series.value_counts()
                others = top_values[top_n:].index
            else:
                return series
        case "quantile":
            if type(param) is not float:
                raise ValueError("For 'quantile' approach, param must be a float.")
            cutoff_quantile = param
            top_values = series.value_counts(normalize=True)
            cumvalues = top_values.cumsum()
            others = top_values[cumvalues > cutoff_quantile].index
        case 'min_val_count':
            if type(param) is not int:
                raise ValueError("For 'min_val_count' approach, param must be an integer.")
            val_count = param
            top_values = series.value_counts()
            others = top_values[top_values <= val_count].index
        case None:
            return series
        case _:
            raise ValueError("approach has an invalid value.")
    
    print(f"Relabelling {len(series[series.isin(others)])} values from {list(others)} to {bottom_label} in {series.name}.")
    return series.replace(to_replace=others, value=bottom_label)

def write_csv(df: pd.DataFrame, outfile: str | Path):
    print(f"Writing {outfile}")
    df.to_csv(outfile)

def save_fig(fig: plt.Figure, folder: str, title: str):
    plt.tight_layout()
    out_path = Path(GLOBALS.OUT_DIR / f"{folder}/{folder}_{title}.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300)
    print(f"Saved figure to: {out_path}")
    return None

def load_rmqs_data() -> gpd.GeoDataFrame:
    """
    Loads the rmqs data with all calculated attributes from a generated csv file
    """
    data_file = GLOBALS.RMQS_FINAL_GEO_PATH
    print(f"Reading {data_file}")
    data =  gpd.read_file(data_file)
    data.set_index('id_site', inplace=True)
    return data