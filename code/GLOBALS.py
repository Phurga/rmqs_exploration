from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OTU_RICH = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\results\otu_richness.csv")
DEFAULT_META = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\data\RMQS1_occupation_nommatp_nomsol_23_03_2022.csv")
OUT_DIR = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\results")
DEFAULT_OTU = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\data\rmqs1_16S_otu_abundance.tsv.gz")
WORLD_PATH = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\data\world.geojson")
SOIL_PATH = Path(r"c:\Users\aburg\Documents\calculations\rmqs_exploration\data\soil_data.csv")
BIOREGION_PATH = Path(r"C:\Users\aburg\Documents\calculations\rmqs_exploration\results\biogeo_assignment.csv")

LAND_USE_SIMPLE_MAPPING = {
    "friches": "urban sites",                                    
    "milieux naturels particuliers": "natural sites",              
    "parcs et jardins": "urban sites",                         
    "successions culturales": "annual crops",                     
    "surfaces boisees": "woods",                          
    "surfaces toujours en herbe": "meadows",               
    "forets caducifoliees": "broadleaved forests",
    "forets de coniferes": "coniferous forests",
    "vignes vergers et cultures perennes arbustives": "permanent crops"
}

# Define color mapping for land use types
LAND_USE_COLOR_MAPPING = {
    "urban sites": "grey",
    "natural sites": "brown",
    "annual crops": "purple",
    "woods": "black",
    "meadows": "green",
    "broadleaved forests": "yellow",
    "coniferous forests": "red",
    "permanent crops": "blue",
}