import warnings
from pathlib import Path
import pandas as pd
import geopandas as gpd

import GLOBALS
# globally silence FutureWarning messages
#warnings.filterwarnings("ignore", category=FutureWarning)

def read_otu_table():
    return pd.read_csv(
        GLOBALS.RMQS_OTU_TABLE_PATH,
        sep="\t",
        index_col="id_site",
        compression="gzip",
        low_memory=False,
        encoding=GLOBALS.ENCODING_RMQS,
    )

def compute_otu_richness(otu_df: pd.DataFrame):
    # presence/absence richness per sample (rows = samples)
    otu_richness = (otu_df > 0).sum(axis=1).astype(int)
    otu_richness.name = "otu_richness"
    otu_richness = otu_richness.to_frame()
    return otu_richness

def compute_total_otu_abundance(otu_df: pd.DataFrame):    # ensure index is string and trimmed
    # total abundance per sample (rows = samples)
    otu_abundance = otu_df.sum(axis=1).astype(int)
    otu_abundance.name = "total_otu_abundance"
    otu_abundance = otu_abundance.to_frame()
    return otu_abundance

def compute_mean_level_abundance(otu_table: pd.DataFrame, taxonomy: pd.DataFrame, level: str = "ORDER") -> pd.DataFrame:
    """
    Aggregate OTU abundances to a taxonomic level.

    - otu_table: array, samples x OTU_IDs, values: sequence count
    - taxonomy: array, OTU_IDs x taxonomic level (level in KINGDOM, PHYLUM, CLASS, ORDER, FAMILY, GENUS), values: taxa name
    - level: str, taxonomic column to aggregate by.

    Returns a DataFrame samples x taxa, values: mean taxa abundance.
    """
    # for each otu, select its taxa at the selected taxonomic level
    otu_taxa = taxonomy[level].astype(str)
    
    #for each otu
    try:
        taxonomy.loc[otu_table.columns]
    except KeyError:
        print("Warning: Some OTU IDs in the OTU table are missing from the taxonomy data.")
        taxonomy = taxonomy.reindex(otu_table.columns)

    # group OTU columns by taxon label and aggregate across columns (axis=1 groups columns)
    taxon_abundance = otu_table.T.groupby(otu_taxa).mean()
    mean_level_abundance = taxon_abundance.mean(axis=1).to_frame(name=f"mean_{level}_abundance")
    return mean_level_abundance

def read_taxonomy(taxonomy_path: Path = GLOBALS.RMQS_TAXONOMY_PATH):
    taxonomy = pd.read_csv(
        taxonomy_path,
        sep="\t",
        index_col="SEQUENCE",
        low_memory=False,
        encoding=GLOBALS.ENCODING_RMQS
    )
    taxonomy.index = taxonomy.index.astype(str).str.strip()
    # unify missing labels
    for level in ["KINGDOM", "PHYLUM", "CLASS", "ORDER", "FAMILY", "GENUS"]:
        taxonomy[level] = taxonomy[level].fillna(f"unclassified_{level}").astype(str)
        taxonomy[level] = taxonomy[level].replace("Unknown", f"unclassified_{level}")
    return taxonomy

def compute_otu_metrics(data: gpd.GeoDataFrame):
    """
    Docstring for compute_otu_metrics
    """
    otu_table = read_otu_table()
    otu_richness = compute_otu_richness(otu_table)
    otu_abundance = compute_total_otu_abundance(otu_table)
    level = "ORDER"
    mean_level_abundance = compute_mean_level_abundance(otu_table, read_taxonomy(), level=level)
    otu_metrics = pd.concat([otu_richness, otu_abundance, mean_level_abundance], axis=1)
    
    # Writing and returning
    print(f"Writing {GLOBALS.RMQS_OTU_STATS}")
    otu_metrics.to_csv(GLOBALS.RMQS_OTU_STATS, index=True)
    data = data.merge(otu_metrics, left_index=True, right_index=True, how="left")
    return data

if __name__ == "__main__":
    compute_otu_metrics()
