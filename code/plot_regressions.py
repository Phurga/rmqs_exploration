import pandas as pd
import statsmodels.formula.api as sm
import matplotlib.pyplot as plt

from utilities import load_data, save_fig

# Load the metadata
metadata_df = load_data()

# Define the dependent variable
dependent_variable = 'otu_richness'

# Get the list of independent variables from the metadata
independent_variables = metadata_df.columns.tolist()
independent_variables.remove(dependent_variable)

# Construct the regression formula
formula = f"{dependent_variable} ~ " + " + ".join(independent_variables)

# Perform the regression
model = sm.ols(formula=formula, data=metadata_df)
results = model.fit()

# Print the regression results
print(results.summary())

# Create a scatter plot of predicted vs. actual values
plt.figure(figsize=(10, 6))
plt.scatter(metadata_df[dependent_variable], results.fittedvalues, alpha=0.5)
plt.xlabel("Actual OTU Richness")
plt.ylabel("Predicted OTU Richness")
plt.title("Actual vs. Predicted OTU Richness")

# Add a diagonal line for reference
plt.plot([min(metadata_df[dependent_variable]), max(metadata_df[dependent_variable])],
         [min(metadata_df[dependent_variable]), max(metadata_df[dependent_variable])],
         color='red', linestyle='--')

save_fig(plt.gcf(), "regression", "otu_richness_regression")
