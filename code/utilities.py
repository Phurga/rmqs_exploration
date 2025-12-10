import pandas as pd
from pathlib import Path

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

def add_soil_metadata(metadata_df: pd.DataFrame):
    mapping = pd.read_csv(GLOBALS.SOIL_METADATA_PATH)
    
    for col in mapping.columns:
        if col in ["date_complete", "code_dept", "type_profil_rmqs"]:
            continue
        try:
            mapping[col] = pd.to_numeric(mapping[col], errors='raise')
        except ValueError:
            #print(f"{col} ({mapping[col].iloc[0]}) could not be converted to numeric and will be ignored.")
            pass  # Ignore columns that cannot be converted
    
    merge = metadata_df.merge(
        mapping, left_on="signific_ger_95", right_on="name", how="left"
    )
    merge.set_index(metadata_df.index, inplace=True)
    return merge

def add_soil_properties(metadata_df: pd.DataFrame) -> pd.DataFrame:
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

    metadata_df = metadata_df.merge(soil_props, left_index=True, right_index=True, how="left")
    return metadata_df


def add_otu(meta_df: pd.DataFrame) -> pd.DataFrame:
        otu_counts = pd.read_csv(GLOBALS.DEFAULT_OTU_RICH, sep=";", index_col="id_site", encoding="windows-1252")
        otu_counts.index = otu_counts.index.astype(str)
        meta_df = meta_df.merge(otu_counts, how="right", left_index=True, right_index=True)
        return meta_df

def load_data(skip = True, out_file = GLOBALS.FULL_DATASET_PATH):
    """ Either loads data from FULL_DATASET_PATH (skip = True) or builds it from raw files."""
    if skip:
        print(f"Reading {out_file}")
        return pd.read_csv(out_file, index_col="id_site", encoding="windows-1252")

    from os import remove
    try:
        remove(out_file)
    except FileNotFoundError:
        pass
    
    meta_df = pd.read_csv(GLOBALS.SAMPLE_METADATA_PATH, index_col="id_site", encoding="windows-1252").dropna()
    meta_df.index = meta_df.index.astype(str)

    meta_df = add_otu(meta_df)
    meta_df = build_land_use_from_desc(meta_df)
    meta_df = add_soil_metadata(meta_df)
    meta_df = add_bioregion(meta_df)
    meta_df = add_soil_properties(meta_df)

    with open(out_file, "w") as f:
        meta_df.to_csv(f)
        print(f"Saved csv to: {out_file}")
    return meta_df


def generate_rmqs_geodataframe(data = None):
    """Generate a GeoDataFrame from RMQS data, whose CRS is RGF93 (EPSG:2154)."""
    from geopandas import GeoDataFrame
    from shapely.geometry import Point
    if data is None:
        data = load_data()
    # Create GeoDataFrame
    gdf = GeoDataFrame(
        data,
        geometry=[Point(x, y) for x, y in zip(data['x_theo'], data['y_theo'])],
        crs="EPSG:2154", #defined in RMQS1_metadata...csv files
    )
    return gdf

def relabel_top_n(series: pd.Series, top_n: int) -> pd.Series:
    """Relabel values in a column to 'others' if they are not in the top N."""
    if top_n is not None and series.nunique() > top_n:
        top_values = series.value_counts().nlargest(top_n).index
        return series.where(series.isin(top_values), 'others')
    return series

def relabel_bottom(series: pd.Series, cutoff_quantile = 0.8, bottom_label = "others", top_n=None) -> pd.Series:
    """Relabel rare values in a column to 'others' if they are in the bottom quantile of datapoints."""
    if len(set(series.values)) < 10:
        return series
    if top_n is not None:
        return relabel_top_n(series, top_n)
    top_values = series.value_counts()/series.count()
    cumvalues = top_values.cumsum()
    others = top_values[cumvalues > cutoff_quantile]
    series[series.isin(others.index)] = bottom_label
    return series

def save_fig(fig, folder, title):
    from matplotlib.pyplot import tight_layout
    tight_layout()
    out_path = Path(GLOBALS.OUT_DIR / f"{folder}/{folder}_{title}.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300)
    print(f"Saved figure to: {out_path}")
    return None

def add_bioregion(metadata_df: pd.DataFrame) -> pd.DataFrame:
    bioregions = pd.read_csv(GLOBALS.RMQS_BIOREGION_CSV_PATH, index_col="id_site", usecols=["id_site", "bioregion"], dtype=str)
    bioregions.index = bioregions.index.astype(str)
    metadata_df = metadata_df.merge(bioregions, left_index=True, right_index=True, how="left")
    return metadata_df

if __name__ == "__main__":
    load_data(skip=False)