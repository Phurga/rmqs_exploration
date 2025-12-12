import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import rasterio
import rasterio.plot
import geopandas

import GLOBALS

def box_to_france(ax, crs):
    """Bound a ax to France extent"""
    match crs:
        case "EPSG:2154":  
            bounds = GLOBALS.FRANCE_BOX_EPSG_2154
        case "EPSG:3035":
            bounds = GLOBALS.FRANCE_BOX_EPSG_3035
        case "IGNF:ETRS89LAEA":
            bounds = GLOBALS.FRANCE_BOX_EPSG_3035
    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])
    return ax

def rename_land_use(data: pd.DataFrame):
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

def add_soil_metadata(data: pd.DataFrame):
    mapping = pd.read_csv(GLOBALS.SOIL_METADATA_PATH)
    
    for col in mapping.columns:
        if col in ["date_complete", "code_dept", "type_profil_rmqs"]:
            continue
        try:
            mapping[col] = pd.to_numeric(mapping[col], errors='raise')
        except ValueError:
            #print(f"{col} ({mapping[col].iloc[0]}) could not be converted to numeric and will be ignored.")
            pass  # Ignore columns that cannot be converted
    
    merge = data.merge(
        mapping, left_on="signific_ger_95", right_on="name", how="left"
    )
    merge.set_index(data.index, inplace=True)
    return merge

def add_soil_properties(data: pd.DataFrame) -> pd.DataFrame:
    """Adding soil properties requires some work because :
    1. there are multiple observations for one site, one for each depth (no_couche),
    2. not all attributes are interesting
    3. many attributes are numeric and need their own type conversion"""
    soil_props = pd.read_csv(GLOBALS.RMQS_SOIL_PROPERTIES_PATH, index_col="id_site", encoding=GLOBALS.ENCODING_RMQS, na_values=["ND"])
    soil_props.index = soil_props.index.astype(str)
    # Keep only the first row for any duplicated index, because there are several rows of soil properties (one for each depth, see no_couche).
    soil_props = soil_props[~soil_props.index.duplicated(keep='first')]
    
    #selection of some columns to extract
    first_column = "type_profil_rmqs"
    soil_props = soil_props.loc[:, first_column : ]
    
    # Attempt to convert columns to numeric types
    for col in soil_props.columns:
        if col in ["date_complete", "code_dept", "type_profil_rmqs"]:
            continue
        try:
            soil_props[col] = pd.to_numeric(soil_props[col], errors='raise')
        except ValueError:
            print(f"{col} ({soil_props[col].iloc[0]}) could not be converted to numeric and will be ignored.")
            pass  # Ignore columns that cannot be converted

    data = data.merge(soil_props, left_index=True, right_index=True, how="left")
    return data

def add_geometries(data: pd.DataFrame, x_col = 'x_theo', y_col = 'y_theo', crs=GLOBALS.CRS_RMQS) -> geopandas.GeoDataFrame:
    """
    Generate a GeoDataFrame from a dataframe containing x and y coordinates
    default settings are adapted to RMQS, whose CRS is RGF93 (EPSG:2154)."""
    from shapely.geometry import Point

    gdf = geopandas.GeoDataFrame(
        data,
        geometry=[Point(x, y) for x, y in zip(data[x_col], data[y_col])],
        crs=crs #defined in RMQS1_metadata...csv files
    )
    return gdf

def relabel_bottom(series: pd.Series, approach = "quantile", param = 0.8, bottom_label = "Others") -> pd.Series:
    """
    Relabel some values of a series to "bottom_label" if they are considered rare considering the approach chosen.
    - 'top_cats' keeps only the "top_n" most populous values based on value counts
    - 'quantile' keeps only categories below a "cutoff_quantile" (default to 0.8)
    - 'min_val_count' keeps only values appearing more than val_count times in the series.
    """
    match approach:
        case "top_cats":
            if type(param) is not int:
                raise ValueError("For 'top_cats' approach, param must be an integer.")
            top_n = param
            if top_n is not None and series.nunique() > top_n:
                top_values = series.value_counts().nlargest(top_n).index
                others = series[~series.isin(top_values)].unique()
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

def write_csv(df: pd.DataFrame, outfile):
    print(f"Writing {outfile}")
    df.to_csv(outfile)

def save_fig(fig, folder, title):
    from matplotlib.pyplot import tight_layout
    tight_layout()
    out_path = Path(GLOBALS.OUT_DIR / f"{folder}/{folder}_{title}.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300)
    print(f"Saved figure to: {out_path}")
    return None

def check_crs(item1, item2):
    """items can be rasters or geodataframes, .crs works the same"""
    if item1.crs != item2.crs: 
        raise ValueError("Combination of geographical elements with different crs.")
    return None

def plot_geodf_on_raster(raster: rasterio.io.DatasetReader,
                         geodf: geopandas.geodataframe.GeoDataFrame,
                         filename: str,
                         attribute: str = None,
                         band_index: int = 1):
    """
    Creates a figure overlapping a raster and a geodataframe.
    Geometry will be plotted with an attribute.
    
    :param raster: rasterio.io.Datasetreader
    :param geodf: geopandas.geodataframe.GeodataFrame
    :param attribute: attribute identifier (column name)
    """
    check_crs(raster, geodf)
    geodf_window = rasterio.windows.from_bounds(*geodf.total_bounds, transform=raster.transform)
    band = raster.read(band_index, window=geodf_window)
    fig, ax = plt.subplots(figsize=(10,10))
    rasterio.plot.show(source=band, transform=raster.window_transform(geodf_window), ax=ax)
    geodf.plot(ax=ax, column=attribute, zorder=2, legend=True, markersize=15)
    save_fig(fig, "map", filename)
    return fig, band

def load_data():
    data_file = GLOBALS.FULL_DATASET_PATH
    print(f"Reading {data_file}")
    data =  pd.read_csv(data_file, index_col="id_site", encoding=GLOBALS.ENCODING_RMQS)
    # cannot import geodataframe directly, needs to regenerate it again
    data.drop('geometry', inplace=True)
    geodata = add_geometries(data)
    return geodata

def sample_raster_to_geodataframe(geodf: geopandas.geodataframe.GeoDataFrame,
                                  raster: rasterio.io.DatasetReader,
                                  band_index: int = 0) -> pd.Series:
    """
    Takes in a geodf and a raster, 
    returns a series aligned with the geodf,
    Retrieves an information stored in the raster at each point in the geodf.
    rasterio.sample does not take geometry object and needs work.
    """
    check_crs(raster, geodf)
    series = pd.Series()
    for idx, row in geodf.iterrows():
        coords = [(row.geometry.x, row.geometry.y)]
        for val in raster.sample(coords):
            series.at[idx] = val[band_index]
    return series