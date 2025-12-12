from pathlib import Path

#Global variables
ENCODING_RMQS = 'windows-1252'
CRS_RMQS = "EPSG:2154"

PROJECT_ROOT = Path(__file__).resolve().parents[1]

#input data
RMQS_LANDUSE_PATH = PROJECT_ROOT / "data_sm/RMQS/sample_site_metadata/RMQS1_occupation_nommatp_nomsol_23_03_2022.csv"
RMQS_SOIL_PROPERTIES_PATH = PROJECT_ROOT / "data_sm/RMQS/sample_site_metadata/RMQS1_analyses_composites_18_11_2021_virgule.csv"
RMQS_OTU_TABLE_PATH = PROJECT_ROOT / "data_sm/RMQS/16S/rmqs1_16S_otu_abundance.tsv.gz"
SOIL_METADATA_PATH = PROJECT_ROOT / "data_sm/RMQS/soil_data.csv" #generated with chatgpt
WORLD_BORDERS_PATH = PROJECT_ROOT / "data_sm/geopandas_world/world.geojson"
EEA_BIOREGION_BORDERS_PATH = PROJECT_ROOT / "data_sm/eea2016_biogeographical_regions/eea_v_3035_1_mio_biogeo-regions_p_2016_v01_r00/BiogeoRegions2016.shp"
HILDA_LAND_USE_PATH = PROJECT_ROOT / "data_sm/hildap_vGLOB-1.0_geotiff/hildap_vGLOB-1.0_geotiff_wgs84/hildap_GLOB-v1.0_lulc-states/hilda_plus_2009_states_GLOB-v1-0_wgs84-nn.tif"
#FRANCE_BORDERS_PATH = PROJECT_ROOT / "data_sm/geopandas_world/France_shapefile/fr_10km.shp"
FRANCE_BORDERS_PATH = PROJECT_ROOT / "data_sm/geopandas_world/fr.json"
RMQS_TAXONOMY_PATH = PROJECT_ROOT / "data_sm/RMQS/16S/rmqs1_16S_otu_taxonomy.tsv"
WWF_ECOREGIONS_BORDERS_PATH = PROJECT_ROOT / "data_sm/wwf_terr_ecos/wwf_terr_ecos.shp"
CORINE_LANDUSE_PATH = PROJECT_ROOT / "data_sm/CORINE_land_cover/u2018_clc2018_v2020_20u1_raster100m/DATA/U2018_CLC2018_V2020_20u1.tif" #https://land.copernicus.eu/en/products/corine-land-cover/clc2018#download
WRB_LVL1_PATH = PROJECT_ROOT / r"data_sm\ESDB-Raster-Library-1k-GeoTIFF-20240507\WRBLV1\WRBLV1.tif"
WRB_LVL1_MAPPING_PATH = PROJECT_ROOT / r"data_sm\ESDB-Raster-Library-1k-GeoTIFF-20240507\WRBLV1\WRBLV1.vat.dbf"
WRB_LVL1_NAMES_PATH = PROJECT_ROOT / r"data_sm\ESDB-Raster-Library-1k-GeoTIFF-20240507\WRBLV1\WRBLV1.txt"

# results
OUT_DIR = PROJECT_ROOT / "results"

RMQS_OTU_STATS = OUT_DIR / "otu_metrics.csv"
BIOREGION_RMQS_PATH = OUT_DIR / "biogeo_assignment.csv"
FRANCE_HILDA_LAND_USE_PATH = OUT_DIR / "land_use_france.tif"
LAND_USE_INTENSITY_PATH = OUT_DIR / "land_use_intensity.csv"
FULL_DATASET_PATH = OUT_DIR / "full_dataset.csv" #rmqs with all metadata
SAMPLE_DATASET_PATH = OUT_DIR / "metadata_sample.csv"
RMQS_BIOREGION_CSV_PATH = OUT_DIR / "bioregion_assignment.csv"
RMQS_ECOREGION_CSV_PATH = OUT_DIR / "ecoregion_assignment.csv"
CORINE_CLASS_MAPPING_PATH = OUT_DIR / "CORINE_mapping.json"
WRB_FINAL_MAPPING_PATH = OUT_DIR / "WRB_mapping.json"
RMQS_WRB_PATH = OUT_DIR / "wrb_assignment.csv"
RMQS_CF_PATH = OUT_DIR / "rmqs_cf_sites.csv"
RMQS_CF_SUMMARY_PATH = OUT_DIR / "rmqs_cf_summary.csv"

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
# EPSG to box to window in plots
FRANCE_BOX_EPSG_2154 = (0e6, 6.0e6, 1.1e6, 7.25e6)
FRANCE_BOX_EPSG_3035 = (2e6, 2.2e6 , 4.2e6, 3.2e6)
AQUITAINE_BOX_EPSG_3035 = (3.3e6, 2.2e6 , 3.6e6, 2.7e6)
