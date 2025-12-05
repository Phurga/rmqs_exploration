from utilities import load_data
from plot_distribution import plot_distribution
from plot_map import plot_map
from plot_heatmap import plot_heatmap

data = load_data()

plot_distribution(data, "otu_richness", "land_use", 'land_use')
plot_distribution(data, "otu_richness", "parent_material", 'parent_material')
plot_distribution(data, "otu_richness", "wrb_guess", 'wrb_class')
plot_distribution(data, "otu_richness", "signific_ger_95", 'soil_type')
plot_distribution(data, "otu_richness", "desc_code_occupation3", 'land_use_fine')

plot_map(data, "land_use", 'land_use')
plot_map(data, "parent_material", 'parent_material')
plot_map(data, "wrb_guess", 'soil_type_wrb')
plot_map(data, "signific_ger_95", 'soil_type')

plot_heatmap(data, "otu_richness", "land_use", "land_use", 'wrb_guess', "soil_class", top_n=10, func='median')
plot_heatmap(data, "otu_richness", "land_use", "land_use", "bioregion", "bioregion", top_n=10, func='median')