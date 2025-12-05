from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

#input data
SAMPLE_METADATA_PATH = PROJECT_ROOT / "data_sm/RMQS/sample_site_metadata/RMQS1_occupation_nommatp_nomsol_23_03_2022.csv"
OTU_TABLE_PATH = PROJECT_ROOT / "data_sm/RMQS/16S/rmqs1_16S_otu_abundance.tsv.gz"
WORLD_PATH = PROJECT_ROOT / "data_sm/geopandas_world/world.geojson"
SOIL_METADATA_PATH = PROJECT_ROOT / "data_sm/RMQS/soil_data.csv" #generated with chatgpt
SOIL_PROPERTIES_PATH = PROJECT_ROOT / "data_sm/RMQS/sample_site_metadata/RMQS1_analyses_composites_18_11_2021_virgule.csv"
EEA_SHP_BIOREGION_PATH = PROJECT_ROOT / "data_sm/eea2016_biogeographical_regions/eea_v_3035_1_mio_biogeo-regions_p_2016_v01_r00/BiogeoRegions2016.shp"
HILDA_LAND_USE_PATH = PROJECT_ROOT / "data_sm/hildap_vGLOB-1.0_geotiff/hildap_vGLOB-1.0_geotiff_wgs84/hildap_GLOB-v1.0_lulc-states/hilda_plus_2009_states_GLOB-v1-0_wgs84-nn.tif"
FRANCE_BORDERS_PATH = PROJECT_ROOT / "data_sm/geopandas_world/France_shapefile/fr_10km.shp"
FRANCE_BORDERS_PATH = PROJECT_ROOT / "data_sm/geopandas_world/fr.json"
TAXONOMY_PATH = PROJECT_ROOT / "data_sm/RMQS/16S/rmqs1_16S_otu_taxonomy.tsv"
# results
OUT_DIR = PROJECT_ROOT / "results"
DEFAULT_OTU_RICH = OUT_DIR / "otu_richness.csv"
BIOREGION_RMQS_PATH = OUT_DIR / "biogeo_assignment.csv"
FRANCE_HILDA_LAND_USE_PATH = OUT_DIR / "land_use_france.tif"
LAND_USE_INTENSITY_PATH = OUT_DIR / "land_use_intensity.csv"
FULL_DATASET_PATH = OUT_DIR / "full_dataset.csv"
SAMPLE_DATASET_PATH = OUT_DIR / "metadata_sample.csv"


LAND_USE_SIMPLE_MAPPING = {
    "friches": "urban sites",                                    
    "milieux naturels particuliers": "natural sites",              
    "parcs et jardins": "urban sites",                         
    "successions culturales": "annual crops",                     
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

LAND_USE_INTENSITY_MAPPING = {
        "urban sites": 100,
        "natural sites": 0,
        "annual crops": 80,
        "meadows": 50,
        "broadleaved forests": 40,
        "coniferous forests": 30,   
        "permanent crops": 90
    }