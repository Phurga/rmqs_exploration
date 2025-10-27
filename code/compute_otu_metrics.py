import warnings
from pathlib import Path
import pandas as pd

from GLOBALS import OTU_TABLE_PATH, OUT_DIR, TAXONOMY_PATH

# globally silence FutureWarning messages
warnings.filterwarnings("ignore", category=FutureWarning)

def compute_otu_richness(otu_df: pd.DataFrame, out_dir: Path = OUT_DIR):
    # presence/absence richness per sample (rows = samples)
    otu_counts = (otu_df > 0).sum(axis=1).astype(int)
    otu_counts.name = "otu_richness"
    otu_counts = otu_counts.to_frame()
    return otu_counts

def compute_total_otu_abundance(otu_df: pd.DataFrame):    # ensure index is string and trimmed
    # total abundance per sample (rows = samples)
    otu_abundance = otu_df.sum(axis=1).astype(int)
    otu_abundance.name = "total_otu_abundance"
    otu_abundance = otu_abundance.to_frame()
    return otu_abundance

def read_otu_table(otu_path: Path = OTU_TABLE_PATH):
    otu_df = pd.read_csv(
        otu_path,
        sep="\t",
        index_col="id_site",
        compression="gzip",
        low_memory=False,
        encoding="windows-1252",
    )
    otu_df.index = otu_df.index.astype(str).str.strip()
    return otu_df

def compute_mean_level_abundance(otu_table: pd.DataFrame, taxonomy: pd.DataFrame, level: str = "ORDER") -> pd.DataFrame:
    """
    Aggregate OTU abundances to a taxonomic level.

    - otu_table: samples x OTU_IDs (columns are OTU IDs).
    - taxonomy: index = OTU_ID, columns include taxonomic ranks (in KINGDOM, PHYLUM, CLASS, ORDER, FAMILY, GENUS).
    - level: taxonomic column to aggregate by.

    Returns a DataFrame samples x taxa with aggregated abundances.
    """
    # fill missing taxon labels with 'unclassified_<level>'
    tax_labels = taxonomy[level].fillna(f"unclassified_{level}").astype(str)
    tax_labels = tax_labels.replace("Unknown", f"unclassified_{level}")

    try:
        taxonomy.loc[otu_table.columns]
    except KeyError:
        print("Warning: Some OTU IDs in the OTU table are missing from the taxonomy data.")
        taxonomy = taxonomy.reindex(otu_table.columns)

    # group OTU columns by taxon label and aggregate across columns (axis=1 groups columns)
    taxon_abundance = otu_table.groupby(tax_labels, axis=1).mean()
    mean_level_abundance = taxon_abundance.mean().to_frame(name=f"mean_{level}_abundance")
    return mean_level_abundance

def read_taxonomy(taxonomy_path: Path = TAXONOMY_PATH):
    taxonomy = pd.read_csv(
        taxonomy_path,
        sep="\t",
        index_col="SEQUENCE",
        low_memory=False,
        encoding="windows-1252"
    )
    taxonomy.index = taxonomy.index.astype(str).str.strip()
    # unify missing labels
    for level in ["KINGDOM", "PHYLUM", "CLASS", "ORDER", "FAMILY", "GENUS"]:
        taxonomy[level] = taxonomy[level].fillna(f"unclassified_{level}").astype(str)
        taxonomy[level] = taxonomy[level].replace("Unknown", f"unclassified_{level}")
    return taxonomy

def write_otu_metrics(otu_metrics: pd.DataFrame, out_dir: Path = OUT_DIR):
    csv_out = out_dir / f"otu_metrics.csv"
    otu_metrics.to_csv(csv_out, sep=";", index=True)
    print(f"Wrote {otu_metrics.columns} to: {csv_out}")
    return None

def main():
    otu_df = read_otu_table()
    otu_richness = compute_otu_richness(otu_df)
    otu_abundance = compute_total_otu_abundance(otu_df)
    level = "ORDER"
    mean_level_abundance = compute_mean_level_abundance(otu_df, read_taxonomy(), level=level)
    otu_metrics = pd.concat([otu_richness, otu_abundance, mean_level_abundance], axis=1)
    write_otu_metrics(otu_metrics)

if __name__ == "__main__":
    main()
