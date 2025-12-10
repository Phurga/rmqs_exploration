import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
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

def build_land_use_from_desc(meta: pd.DataFrame):
    """
    Recreate the custom 'land_use' classification:
    - keep desc_code_occupation1 except for 'surfaces boisees'
    - for 'surfaces boisees' use desc_code_occupation3 but only keep allowed subclasses
    - rows with other forest subclasses are set to NaN (dropped later)
    """
    #build custom land use classes
    def make_custom(row):
        keep1 = "surfaces boisees"
        keep3 = "forets caducifoliees"
        other3 = "forets de coniferes"
        if row["desc_code_occupation1"] == keep1:
            if row["desc_code_occupation3"] == keep3:
                return keep3
            return other3
        return row["desc_code_occupation1"]

    meta["land_use"] = meta.apply(make_custom, axis=1)
    meta["land_use"] = meta["land_use"].map(GLOBALS.LAND_USE_SIMPLE_MAPPING)

    #add land use intensity levels
    meta["land_use_intensity"] = meta["land_use"].map(GLOBALS.LAND_USE_INTENSITY_MAPPING)
    return meta

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
    soil_props = pd.read_csv(GLOBALS.SOIL_PROPERTIES_PATH, index_col="id_site", encoding="windows-1252", na_values=["ND"])
    soil_props.index = soil_props.index.astype(str)
    # Keep only the first row for any duplicated index
    soil_props = soil_props[~soil_props.index.duplicated(keep='first')]
    
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


def add_otu(data: pd.DataFrame) -> pd.DataFrame:
        otu_counts = pd.read_csv(GLOBALS.DEFAULT_OTU_RICH, sep=";", index_col="id_site", encoding="windows-1252")
        otu_counts.index = otu_counts.index.astype(str)
        data = data.merge(otu_counts, how="right", left_index=True, right_index=True)
        return data

def add_from_csv(data: pd.DataFrame, csv_path: str):
    csv_data = pd.read_csv(csv_path, index_col='id_site', dtype=str)
    csv_data.index = csv_data.index.astype(str)
    data = data.merge(csv_data, left_index=True, right_index=True, how="left")
    return data

def load_data(skip = True, out_file = GLOBALS.FULL_DATASET_PATH):
    """ Either loads data from FULL_DATASET_PATH (skip = True) or builds it from raw files."""
    if skip and out_file.is_file():
        print(f"Reading {out_file}")
        return pd.read_csv(out_file, index_col="id_site", encoding="windows-1252")

    from os import remove
    try:
        remove(out_file)
    except FileNotFoundError:
        pass
    
    data = pd.read_csv(GLOBALS.SAMPLE_METADATA_PATH, index_col="id_site", encoding="windows-1252").dropna()
    data.index = data.index.astype(str)

    data = add_otu(data)
    data = build_land_use_from_desc(data)
    data = add_soil_metadata(data)
    data = add_from_csv(data, GLOBALS.RMQS_BIOREGION_CSV_PATH) #add bioregion
    data = add_soil_properties(data)
    data = generate_rmqs_geodataframe(data)
    data = add_from_csv(data, GLOBALS.WRB_CLASS_RMQS_PATH) #add wrb lvl 1 class

    with open(out_file, "w") as f:
        data.to_csv(f)
        print(f"Saved csv to: {out_file}")
    return data


def generate_rmqs_geodataframe(data = None):
    """Generate a GeoDataFrame from RMQS data, whose CRS is RGF93 (EPSG:2154)."""
    from geopandas import GeoDataFrame
    from shapely.geometry import Point

    if data is None: data = load_data()
    
    gdf = GeoDataFrame(
        data,
        geometry=[Point(x, y) for x, y in zip(data['x_theo'], data['y_theo'])],
        crs="EPSG:2154" #defined in RMQS1_metadata...csv files
    )
    return gdf

def relabel_top_n(series: pd.Series, top_n: int) -> pd.Series:
    """Relabel values in a column to 'others' if they are not in the top N most populous."""


def relabel_bottom(series: pd.Series, approach = "quantile", cutoff_quantile = 0.8, bottom_label = "Others", top_n=None, val_count = None) -> pd.Series:
    """
    Relabel some values of a series to "bottom_label" if they are considered rare considering the approach chosen.
    - 'quantile' keeps only categories below a "cutoff_quantile" (default to 0.8)
    - 'n_cats' keeps only the "top_n" most populous values based on value counts
    - 'val_count' keeps only values appearing more than val_count times in the series.
    """
    if len(set(series.values)) < 10:
        print("Relabelling was skipped since series has less than 10 categories")
        return series
    match approach:
        case "cat_num":
            if top_n is not None and series.nunique() > top_n:
                top_values = series.value_counts().nlargest(top_n).index
                return series.where(series.isin(top_values), 'others')
        case "quantile":
            top_values = series.value_counts(normalize=True)
            cumvalues = top_values.cumsum()
            others = top_values[cumvalues > cutoff_quantile].index
        case 'val_count':
            top_values = series.value_counts()
            others = top_values[top_values > val_count].index
    print(f"Relabelling {len(series[series.isin(others)])} values from {others}to {bottom_label} in {series.name}.")
    series.replace(to_replace=others, value=bottom_label, inplace=True)
    return series

def save_fig(fig, folder, title):
    from matplotlib.pyplot import tight_layout
    tight_layout()
    out_path = Path(GLOBALS.OUT_DIR / f"{folder}/{folder}_{title}.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300)
    print(f"Saved figure to: {out_path}")
    return None

import rasterio
import rasterio.plot
import geopandas

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

if __name__ == "__main__":
    load_data(skip=False)