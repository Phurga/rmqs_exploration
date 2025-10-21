import pandas as pd
from pathlib import Path
from GLOBALS import SOIL_PATH, DEFAULT_META, DEFAULT_OTU_RICH, LAND_USE_SIMPLE_MAPPING, OUT_DIR, BIOREGION_PATH


def build_land_use_from_desc(meta: pd.DataFrame):
    """
    Recreate the custom 'land_use' classification:
    - keep desc_code_occupation1 except for 'surfaces boisees'
    - for 'surfaces boisees' use desc_code_occupation3 but only keep allowed subclasses
    - rows with other forest subclasses are set to NaN (dropped later)
    """

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
    meta["land_use"] = meta["land_use"].map(LAND_USE_SIMPLE_MAPPING)
    return meta

def add_soil_data(metadata_df: pd.DataFrame):
    mapping = pd.read_csv(SOIL_PATH)
    merge = metadata_df.merge(
        mapping, left_on="signific_ger_95", right_on="name", how="left"
    )
    merge.set_index(metadata_df.index, inplace=True)
    return merge


def load_data(
    otu_path: Path = DEFAULT_OTU_RICH,
    meta_path: Path = DEFAULT_META,
    top_n: int = None,
    top_column: str = None,
    filter_columns: list = None,
):
    """
    Loads OTU counts and metadata, merges them, and applies optional filtering and relabeling.

    Args:
        otu_path (Path, optional): Path to OTU counts CSV. Defaults to DEFAULT_OTU_RICH.
        meta_path (Path, optional): Path to metadata CSV. Defaults to DEFAULT_META.
        top_n (int, optional): Number of top values to keep in the specified column. Defaults to None.
        column (str, optional): Column to relabel based on top N values. Defaults to None.
        filter_columns (list, optional): List of columns to keep in the metadata. Defaults to None.

    Returns:
        tuple: OTU counts and processed metadata DataFrames.
    """
    otu_counts = pd.read_csv(
        otu_path, sep=";", index_col="id_site", encoding="windows-1252"
    )
    otu_counts.index = otu_counts.index.astype(str)

    meta_df = pd.read_csv(meta_path, index_col="id_site", encoding="windows-1252").dropna()
    meta_df.index = meta_df.index.astype(str)

    meta_df = build_land_use_from_desc(meta_df)
    meta_df = add_soil_data(meta_df)
    meta_df = add_bioregion(meta_df)

    if filter_columns:
        meta_df = meta_df[filter_columns]

    if top_column:
        meta_df[top_column] = relabel_top_n(meta_df[top_column], top_n)

    return otu_counts, meta_df


def relabel_top_n(series: pd.Series, n: int) -> pd.Series:
    """Relabel values in a column to 'others' if they are not in the top N."""
    if n is not None and series.nunique() > n:
        top_values = series.value_counts().nlargest(n).index
        return series.where(series.isin(top_values), 'others')
    return series

def save_fig(fig, folder, title):
    out_path = Path(OUT_DIR / f"{folder}/{folder}_{title}.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300)
    print(f"Saved figure to: {out_path}")

def add_bioregion(metadata_df: pd.DataFrame) -> pd.DataFrame:
    bioregions = pd.read_csv(BIOREGION_PATH, index_col="id_site", usecols=["id_site", "bioregion"], dtype=str)
    bioregions.index = bioregions.index.astype(str)
    metadata_df = metadata_df.merge(bioregions, left_index=True, right_index=True, how="left")
    return metadata_df