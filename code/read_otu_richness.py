import warnings
from pathlib import Path
import pandas as pd

from code.GLOBALS import DEFAULT_OTU, OUT_DIR

# globally silence FutureWarning messages
warnings.filterwarnings("ignore", category=FutureWarning)

def read_and_write_richness(otu_path: Path = DEFAULT_OTU, out_dir: Path = OUT_DIR):
    otu_df = pd.read_csv(
        otu_path,
        sep="\t",
        index_col="id_site",
        compression="gzip",
        low_memory=False,
        encoding="windows-1252",
    )
    # ensure index is string and trimmed
    otu_df.index = otu_df.index.astype(str).str.strip()

    # presence/absence richness per sample (rows = samples)
    otu_counts = (otu_df > 0).sum(axis=1).astype(int)
    otu_counts.name = "otu_richness"
    otu_counts = otu_counts.to_frame()

    csv_out = out_dir / "otu_richness.csv"
    #pq_out = out_dir / "otu_richness.parquet"
    otu_counts.to_csv(csv_out, sep=";", index=True)
    #otu_counts.to_parquet(pq_out)

    print(f"Wrote richness to: {csv_out}")
    #print(f"Wrote parquet copy to: {pq_out}")
    return otu_counts


if __name__ == "__main__":
    read_and_write_richness()