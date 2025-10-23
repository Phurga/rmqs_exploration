import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

from utilities import load_data, save_fig

def calculate_intact_rows(df, columns):
    """Calculates the number of intact (non-NA) rows for a given set of columns."""
    return df[columns].dropna().shape[0]

def is_pareto_efficient(points):
    """
    Finds the Pareto-efficient points from a set of points.
    :param points: An array of (x, y) points.
    :return: A boolean array indicating whether each point is Pareto-efficient.
    """
    is_efficient = np.ones(points.shape[0], dtype=bool)
    for i, point in enumerate(points):
        if is_efficient[i]:
            # Keep any point with a higher cost
            is_efficient[is_efficient] = np.any(points[is_efficient] > point, axis=1) | (points[is_efficient] == point).all(axis=1)
            is_efficient[i] = True  # And keep this point as well
    return is_efficient

def plot_pareto_front(metadata_df, attribute_columns):
    """
    Plots the Pareto front for maximizing the number of attribute columns and intact rows.

    :param metadata_df: DataFrame containing the metadata.
    :param attribute_columns: List of columns to consider as attributes.
    """

    results = []
    for k in range(1, len(attribute_columns) + 1):
        print(f"Processing combinations of size {k} over {len(attribute_columns)+1} attributes.")
        for column_subset in combinations(attribute_columns, k):
            num_columns = k
            num_intact_rows = calculate_intact_rows(metadata_df, list(column_subset))
            results.append((num_columns, num_intact_rows))

    # Convert results to a numpy array
    points = np.array(results)

    # Find Pareto-efficient points
    is_efficient = is_pareto_efficient(points)
    pareto_front = points[is_efficient]

    # Sort Pareto front for plotting
    pareto_front = pareto_front[np.argsort(pareto_front[:, 0])]

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.scatter(points[:, 0], points[:, 1], label='All Combinations', alpha=0.5)
    plt.plot(pareto_front[:, 0], pareto_front[:, 1], color='red', marker='o', linestyle='-', label='Pareto Front')

    plt.xlabel('Number of Attribute Columns')
    plt.ylabel('Number of Intact Rows')
    plt.title('Pareto Front: Maximizing Attribute Columns and Intact Rows')
    plt.legend()
    plt.grid(True)
    save_fig(plt.gcf(), "pareto_front", "attribute_count_vs_intact_rows")
    

if __name__ == '__main__':
    metadata_df = load_data()
    col_idx = [24, 27, 47] + list(range(73, 77)) + list(range(58, 63))
    metadata_df = metadata_df.iloc[:,col_idx]

    # Define attribute columns (replace with your actual column names)
    attribute_columns = metadata_df.columns.tolist()
    attribute_columns.remove('otu_richness')
    #attribute_columns = ["argile", "sable_grossier", 'carbone_16_5_1', 'ph_eau_6_1', "land_use", "wrb_guess", "bioregion"]
    plot_pareto_front(metadata_df, attribute_columns)
