import plotly.express as px

from utilities import load_data
import pandas as pd

def data_preparation(metadata_df):
    # Columns to process
    columns = ['argile', 'limon_grossier', 'limon_fin', 'sable_grossier', 'sable_fin']

    # Replace 'ND' with NaN and convert to numeric
    metadata_df[columns] = metadata_df[columns].replace('ND', pd.NA)
    metadata_df[columns] = metadata_df[columns].apply(pd.to_numeric, errors='coerce')

    # Remove rows with NaN in the specified columns
    metadata_df.dropna(subset=columns, inplace=True)

    # Extract argile, limon, and sable from the metadata
    metadata_df["limon"] = (metadata_df['limon_grossier'] + metadata_df['limon_fin']) / 1000
    metadata_df["sable"] = (metadata_df['sable_grossier'] + metadata_df['sable_fin']) / 1000
    metadata_df["argile"] = metadata_df["argile"] / 1000
    return metadata_df

def plot_ternary_plot(metadata_df, value_col):
    metadata_df = data_preparation(metadata_df)
    figure = px.scatter_ternary(metadata_df, a="argile", b="sable", c="limon", size_max=10, opacity=0.4)
    #add a color bar
    figure.update_traces(marker=dict(color=metadata_df[value_col], colorscale='Viridis', colorbar=dict(title=value_col)))
    figure.write_image("results/ternary_plot/ternary_plot_soil_texture.png", scale=3)
    return None
    
if __name__ == "__main__":
    metadata_df = load_data()
    #merge otu richness to metadata
    plot_ternary_plot(metadata_df, value_col="otu_richness")
