from utilities import load_data
from plot_distribution import plot_land_use_distribution
from plot_map import plot_rmqs_with_attribute
from plot_heatmap import plot_heatmap
from plot_map import plot_rmqs_with_regions
import GLOBALS

data = load_data()

plot_land_use_distribution(data, "otu_richness", "land_use", 'land_use')
plot_land_use_distribution(data, "otu_richness", "parent_material", 'parent_material')
plot_land_use_distribution(data, "otu_richness", "wrb_guess", 'wrb_class')
plot_land_use_distribution(data, "otu_richness", "signific_ger_95", 'soil_type')
plot_land_use_distribution(data, "otu_richness", "desc_code_occupation3", 'land_use_fine')

plot_rmqs_with_attribute(data, "land_use", 'land_use')
plot_rmqs_with_attribute(data, "parent_material", 'parent_material')
plot_rmqs_with_attribute(data, "wrb_guess", 'soil_type_wrb')
plot_rmqs_with_attribute(data, "signific_ger_95", 'soil_type')

plot_heatmap(data, "otu_richness", "land_use", "land_use", 'wrb_guess', "soil_class", top_n=10, func='median')
plot_heatmap(data, "otu_richness", "land_use", "land_use", "bioregion", "bioregion", top_n=10, func='median')

plot_rmqs_with_regions(data, GLOBALS.EEA_BIOREGION_BORDERS_PATH, 'code', 'bioregion')
