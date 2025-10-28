import pandas as pd

from compute_otu_metrics import read_otu_table, read_taxonomy
from utilities import load_data, save_fig
from GLOBALS import LAND_USE_INTENSITY_MAPPING


def build_level_site_table(otu_taxonomy: pd.DataFrame, site_otu_table: pd.DataFrame, level: str) -> pd.DataFrame:
    """
    Build the table of level richness by site
    level can be KINGDOM, PHYLUM, CLASS, ORDER, FAMILY, GENUS
    """
    #clean otu_taxonomy level column
    otu_taxonomy[level] = otu_taxonomy[level].fillna(f"unclassified_{level}").astype(str)
    otu_taxonomy[level] = otu_taxonomy[level].replace("Unknown", f"unclassified_{level}")

    #convert site_otu_table from abundance to presence (richness)
    site_otu_table = site_otu_table.astype(bool) 

    #group otus (otu_table columns) by tax_labels
    level_site_table = site_otu_table.groupby(otu_taxonomy[level], axis=1).sum()

    return level_site_table

def build_level_land_use_table(level_site_table: pd.DataFrame, site_metadata: pd.DataFrame) -> pd.DataFrame:
    """Build the table of mean level richness by land use"""

    #group sites (otu_table rows) by land_use
    level_land_use_table = level_site_table.groupby(site_metadata['land_use'], axis=0).mean()
    
    #keep only taxa with more than 100 sites
    acceptable_levels = [col for col in level_site_table.columns if (level_site_table[col] > 0).sum() > 100]
    level_land_use_table = level_land_use_table[acceptable_levels]
    
    #convert to percentages of max land use value
    level_land_use_table = level_land_use_table.div(level_land_use_table.max(axis=0), axis=1) * 100
    
    #change land use display order based on land use intensity    
    mapping = pd.DataFrame(LAND_USE_INTENSITY_MAPPING.items(), columns=["land_use", "intensity_level"]).set_index("land_use")
    level_land_use_table = level_land_use_table.reindex(mapping.sort_values("intensity_level").index)
    
    #change level display order of columns based on value for "annual crops"
    level_land_use_table = level_land_use_table.reindex(level_land_use_table.loc["annual crops"].sort_values(ascending=False).index, axis=1)

    return level_land_use_table

def plot_level_land_use_table(level_land_use_table, level, site_metadata, level_site_table) -> None:
    """Plot the level_land_use_table as a heatmap with sorted axis"""
    
    import seaborn as sns
    import matplotlib.pyplot as plt
    plt.figure(figsize=(14, 8))
    # change index and column names to include counts
    level_land_use_table.index   = [f"{idx} ({len(site_metadata[site_metadata['land_use'] == idx].index)})" for idx in level_land_use_table.index]
    level_land_use_table.columns = [f"{col} ({(level_site_table[col] > 0).sum()})" for col in level_land_use_table.columns]

    #plot settings
    sns.heatmap(level_land_use_table.transpose(), cmap="viridis")
    plt.yticks(fontsize=8)
    plt.xlabel('Land use')
    plt.ylabel(f'{level}')
    plt.title(f'Mean {level} richness by land use relative to max land use')
    save_fig(plt.gcf(), 'taxonomy',f'taxonomy_{level}_land_use_heatmap')

    return None

def main():
    if False:
        otu_taxonomy = read_taxonomy()
        site_otu_table = read_otu_table()
        site_metadata = load_data()
        import pickle
        with open("./results/temp.pkl", "wb") as f:
            pickle.dump((otu_taxonomy, site_otu_table, site_metadata), f)
    else:
        import pickle
        with open("./results/temp.pkl", "rb") as f:
            otu_taxonomy, site_otu_table, site_metadata = pickle.load(f)
    
    level = "PHYLUM" #KINGDOM, PHYLUM, CLASS, ORDER, FAMILY, GENUS
    
    level_site_table = build_level_site_table(
        otu_taxonomy=otu_taxonomy, site_otu_table=site_otu_table, level=level)
    
    level_land_use_table = build_level_land_use_table(
        level_site_table=level_site_table, site_metadata=site_metadata)
    
    plot_level_land_use_table(
        level_land_use_table=level_land_use_table, level=level, site_metadata=site_metadata, level_site_table=level_site_table)
    
    return None

if __name__ == "__main__":
    main()