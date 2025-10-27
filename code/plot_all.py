from utilities import load_data
from plot_distribution import plot_distribution
from plot_map import plot_map
from plot_heatmap import plot_heatmap

rich, meta = load_data()

plot_distribution(rich, meta, "otu_richness", "land_use", 'land_use')
plot_distribution(rich, meta, "otu_richness", "parent_material", 'parent_material')
plot_distribution(rich, meta, "otu_richness", "wrb_guess", 'wrb_class')
plot_distribution(rich, meta, "otu_richness", "signific_ger_95", 'soil_type')
plot_distribution(rich, meta, "otu_richness", "desc_code_occupation3", 'land_use_fine')

plot_map(meta, "land_use", 'land_use')
plot_map(meta, "parent_material", 'parent_material')
plot_map(meta, "wrb_guess", 'soil_type_wrb')
plot_map(meta, "signific_ger_95", 'soil_type')

plot_heatmap(rich, meta, "otu_richness", "land_use", "land_use", 'wrb_guess', "soil_class", top_n=10, agg='median')
plot_heatmap(rich, meta, "otu_richness", "land_use", "land_use", "bioregion", "bioregion", top_n=10, agg='median')