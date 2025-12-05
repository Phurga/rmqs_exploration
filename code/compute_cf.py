import GLOBALS
from plot_heatmap import build_pivot
import pandas as pd

data = pd.read_csv(GLOBALS.FULL_DATASET_PATH, index_col="id_site", encoding="windows-1252")

pivot = build_pivot(data=data,
                    value_field="otu_richness",
                    line_field="land_use",
                    col_field="bioregion",
                    top_n=10,
                    func='median')


