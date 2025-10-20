from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OTU_RICH = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\results\otu_richness.csv")
DEFAULT_META = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\data\RMQS1_occupation_nommatp_nomsol_23_03_2022.csv")
OUT_DIR = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\results")
OUT_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_OTU = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\data\rmqs1_16S_otu_abundance.tsv.gz")
WORLD_PATH = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\data\world.geojson")
SOIL_PATH = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\data\soil_data.csv")