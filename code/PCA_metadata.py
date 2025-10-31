"""
PCA utilities for metadata.

This module prepares numeric metadata, standardizes it, fits PCA and produces
plots and selection reports.

Conceptual notes (brief):
- Scores: the coordinates of samples in the principal component space.
  Each row of `scores` corresponds to a sample; columns are PC axes (PC1, PC2,...).
  Scores tell you how samples relate to the axes (e.g. samples with high PC1 scores
  have high values on variables that load positively on PC1).

- Loadings: the contribution of each original variable to the PCs. Loadings are
  the eigenvectors of the covariance (or correlation) matrix and show how strongly
  each original variable correlates with a given PC. Large absolute loading means
  the variable strongly influences that PC. Signed loadings indicate direction.

Use `scores` to visualize sample structure (biplots, clustering) and `loadings`
to interpret which variables drive each principal component.
"""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV
from scipy.stats import pearsonr

from statsmodels.stats.outliers_influence import variance_inflation_factor

from utilities import load_data
from GLOBALS import OUT_DIR

def _prepare_metadata(metadata_df: pd.DataFrame, categorical: str):
    """
    Validate and extract numeric metadata for PCA.

    Parameters
    - metadata_df: full metadata DataFrame

    Returns
    - numeric: DataFrame of numeric columns with rows having no missing values
    - var_names: list of variable (column) names used for PCA

    Notes:
    - Requires 'otu_richness' present in numeric columns (used later for correlation checks).
    - Rows with any missing numeric values are dropped and a warning is issued.
    """
    if not isinstance(metadata_df, pd.DataFrame):
        raise TypeError("metadata_df must be a pandas DataFrame.")
    numeric = metadata_df.select_dtypes(include=[np.number]).copy()
    if "otu_richness" not in numeric.columns:
        raise KeyError("otu_richness must be a numeric column in metadata_df.")
    # drop columns with too many na values
    n = 50
    numeric.isna().sum().sort_values(ascending=False)
    drop_cols = numeric.isna().sum()[numeric.isna().sum() > n].index.tolist()
    drop_cols += ['occupation3', 'occupation1']
    numeric.drop(columns=drop_cols, inplace=True)
    pre_count = numeric.shape[0]
    numeric = numeric.dropna(axis=0, how="any")
    dropped = pre_count - numeric.shape[0]
    if dropped > 0:
        warnings.warn(f"Dropped {dropped} rows with missing numeric metadata for PCA/report.")
    var_names = list(numeric.columns)
    categorical = metadata_df.loc[numeric.index, categorical_str].squeeze()
    return numeric, var_names, categorical

def _standardize(X: pd.DataFrame):
    """
    Standardize numeric matrix (zero mean, unit variance).

    Parameters
    - X: numeric DataFrame (samples x features)

    Returns
    - Xs: standardized numpy array (samples x features)
    - scaler: fitted StandardScaler instance (useful to invert scaling if needed)
    """
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X.values)
    return Xs, scaler

def _fit_pca(Xs, n_components=None):
    """
    Fit PCA on standardized data.

    Parameters
    - Xs: standardized data array (samples x features)
    - n_components: number of principal components to compute (defaults to min(10, n_features))

    Returns
    - pca: fitted sklearn PCA object
    - scores: numpy array of sample scores (samples x n_components)
    - loadings: numpy array of component loadings (features x n_components)
    """
    if n_components is None:
        n_components = min(10, Xs.shape[1])
    pca = PCA(n_components=n_components)
    scores = pca.fit_transform(Xs)
    loadings = pca.components_.T  # shape: (n_features, n_components)
    return pca, scores, loadings

def _ensure_outdir():
    """
    Ensure the PCA output directory exists and return its Path.

    Returns
    - Path to output directory for PCA artifacts
    """
    p = Path(OUT_DIR) / "PCA"
    p.mkdir(parents=True, exist_ok=True)
    return p

def _plot_scree(pca, outdir: Path):
    """
    Plot scree and cumulative variance explained by PCs and save figure.

    Parameters
    - pca: fitted PCA object
    - outdir: output Path to write the figure

    Returns
    - filepath of saved scree plot
    """
    fig, ax = plt.subplots(figsize=(6,4))
    evr = pca.explained_variance_ratio_
    ax.plot(np.arange(1, len(evr)+1), evr.cumsum(), marker='o', label='Cumulative')
    ax.bar(np.arange(1, len(evr)+1), evr, alpha=0.6, label='Per PC')
    ax.set_xlabel("Principal Component")
    ax.set_ylabel("Variance explained")
    ax.set_xticks(np.arange(1, len(evr)+1))
    ax.legend()
    fig.tight_layout()
    fp = outdir / "scree.png"
    fig.savefig(fp, dpi=150)
    plt.close(fig)
    return fp

def _plot_biplot(scores, loadings, var_names, outdir: Path, categorical: pd.Series):
    """
    Create and save a biplot of PC1 vs PC2 with variable loadings as arrows.

    Parameters
    - scores: sample scores array (samples x components)
    - loadings: loadings array (features x components)
    - var_names: list of feature names
    - outdir: Path where to save the biplot
    - scale_arrows: multiplier for arrow lengths (visual scaling)
    """
    fig, axs = plt.subplots(ncols=2, figsize=(14,6))
    #lim = max(np.abs(np.concatenate([pc1, pc2]))) * 0.9
    #plot PC1 vs PC2 features
    axs[0].set_xlabel("PC1")
    axs[0].set_ylabel("PC2")
    # arrows for loadings
    for i, v in enumerate(var_names):
        x = loadings[i,0]
        y = loadings[i,1]
        #alpha is calculated based on vector length
        alpha = np.sqrt(x**2 + y**2) / np.sqrt(2)
        axs[0].arrow(0, 0, x, y, color='red', alpha=0.4, head_width=0.015)
        axs[0].text(x, y, v, color='red', alpha=alpha)
    axs[0].axhline(0, color='grey', linewidth=0.5)
    axs[0].axvline(0, color='grey', linewidth=0.5)
    axs[0].set_title("PCA Biplot (PC1 vs PC2)")

    # plot sample result in PC space
    pc1 = scores[:,0]
    pc2 = scores[:,1]
    #colormap scatter based on categorical variable
    unique_cats = categorical.unique()
    colors = plt.cm.get_cmap('tab10', len(unique_cats))
    for i, uc in enumerate(unique_cats):
        axs[1].scatter(pc1[categorical == uc], pc2[categorical == uc], alpha=0.4, label=uc, color=colors(i), s=20, linewidths=0)
    axs[1].legend(alpha=1.0, title=categorical.name)
    #axs[1].scatter(pc1, pc2, alpha=0.6, label=var_names)
    axs[1].set_xlabel("PC1")
    axs[1].set_ylabel("PC2")
    axs[1].axhline(0, color='grey', linewidth=0.5)
    axs[1].axvline(0, color='grey', linewidth=0.5)
    axs[1].set_title("Samples in PC Space (PC1 vs PC2)")

    fig.tight_layout()
    fp = outdir / "PCA_plot.png"
    fig.savefig(fp, dpi=150)
    plt.close(fig)
    return fp

def _plot_loadings_heatmap(loadings, var_names, outdir: Path):
    """
    Create heatmap of loadings for features x PCs and save it.

    Parameters
    - loadings: numpy array (features x components)
    - var_names: list of feature names
    - outdir: output Path

    Returns
    - filepath of saved heatmap and the DataFrame used for plotting
    """
    df = pd.DataFrame(loadings, index=var_names, columns=[f"PC{i+1}" for i in range(loadings.shape[1])])
    fig, ax = plt.subplots(figsize=(max(6, len(var_names)*0.2), 8))
    sns.heatmap(df, cmap="coolwarm", center=0, annot=False, ax=ax)
    ax.set_ylabel("")
    fig.tight_layout()
    fp = outdir / "loadings_heatmap.png"
    fig.savefig(fp, dpi=150)
    plt.close(fig)
    return fp, df

def _importance_from_loadings(loadings, explained_variance):
    """
    Compute a single importance score per variable from weighted absolute loadings.

    Parameters
    - loadings: array (features x components)
    - explained_variance: array of variance ratios per PC

    Returns
    - importance: 1D array of importance scores per feature
    """
    # Weighted absolute loadings across PCs -> single importance score per variable
    abs_load = np.abs(loadings)
    weights = explained_variance[:abs_load.shape[1]]
    importance = abs_load.dot(weights)
    return importance

def _pairwise_filter_by_corr(df_numeric, candidates, corr_threshold, importance_scores, corr_with_otu):
    """
    Reduce candidate features by removing highly correlated pairs.

    Strategy: for any pair with |corr| >= corr_threshold keep the variable with
    higher importance (tie broken by stronger correlation to otu_richness).

    Parameters
    - df_numeric: numeric DataFrame
    - candidates: ordered list of variable names
    - corr_threshold: threshold for absolute correlation to consider as redundant
    - importance_scores: dict mapping variable->importance
    - corr_with_otu: dict mapping variable->(r,p) with otu_richness

    Returns
    - filtered list of candidates preserving original order
    """
    # Remove one of any pair with absolute corr >= corr_threshold.
    keep = set(candidates)
    corrmat = df_numeric[candidates].corr().abs()
    for i in range(len(candidates)):
        vi = candidates[i]
        if vi not in keep:
            continue
        for j in range(i+1, len(candidates)):
            vj = candidates[j]
            if vj not in keep:
                continue
            if corrmat.loc[vi, vj] >= corr_threshold:
                # keep the one with higher importance, tie-breaker: higher |corr_with_otu|
                imp_i = importance_scores.get(vi, 0.0)
                imp_j = importance_scores.get(vj, 0.0)
                corr_i = abs(corr_with_otu.get(vi, (0.0,))[0]) if vi in corr_with_otu else 0.0
                corr_j = abs(corr_with_otu.get(vj, (0.0,))[0]) if vj in corr_with_otu else 0.0
                if imp_i > imp_j or (imp_i == imp_j and corr_i >= corr_j):
                    keep.discard(vj)
                else:
                    keep.discard(vi)
                    break
    return [v for v in candidates if v in keep]

def _compute_vif(df, features):
    """
    Compute Variance Inflation Factor (VIF) for a list of features.

    Parameters
    - df: DataFrame containing numeric features
    - features: list of column names to compute VIF for

    Returns
    - dict mapping feature name -> VIF value (may contain NaN if computation failed)
    """
    X = df[features].values
    vif = []
    for i in range(X.shape[1]):
        try:
            vif_val = variance_inflation_factor(X, i)
        except Exception:
            vif_val = np.nan
        vif.append(vif_val)
    return dict(zip(features, vif))

def _iterative_vif_filter(df, features, threshold=10.0, max_iter=10):
    """
    Iteratively remove the feature with highest VIF until all VIFs <= threshold.

    Parameters
    - df: numeric DataFrame
    - features: initial list of features
    - threshold: VIF cutoff
    - max_iter: maximum iterations to remove features

    Returns
    - (kept_features_list, last_vif_dict)
    """
    feats = list(features)
    for _ in range(max_iter):
        vif_dict = _compute_vif(df, feats)
        max_feat = max(vif_dict.items(), key=lambda kv: (np.nan_to_num(kv[1], nan=-1)) )
        if max_feat[1] <= threshold or np.isnan(max_feat[1]):
            break
        feats.remove(max_feat[0])
    return feats, vif_dict

def _lasso_select(df, features, target, cv=5, random_state=0):
    """
    Run LassoCV to select variables predictive of `target`.

    Returns (selected_features_list, Series of coefficients indexed by features).
    """
    X = df[features].values
    y = df[target].values
    try:
        lasso = LassoCV(cv=cv, random_state=random_state, n_jobs=-1).fit(X, y)
        coefs = pd.Series(lasso.coef_, index=features)
        selected = coefs[coefs.abs() > 1e-8].index.tolist()
        return selected, coefs
    except Exception:
        return [], pd.Series([], index=features)

def _correlations_with_otu(numeric, var_names):
    """
    Compute Pearson correlation of each variable with 'otu_richness'.

    Parameters
    - numeric: numeric DataFrame containing 'otu_richness'
    - var_names: list of variable names to compute correlations for

    Returns
    - dict variable -> (r, p)
    """
    otu = numeric["otu_richness"].values
    corr_with_otu = {}
    for v in var_names:
        if v == "otu_richness":
            corr_with_otu[v] = (1.0, 0.0)
            continue
        try:
            r, p = pearsonr(numeric[v].values, otu)
        except Exception:
            r, p = (np.nan, np.nan)
        corr_with_otu[v] = (r, p)
    return corr_with_otu

def run_pca_metadata(metadata_df: pd.DataFrame,
                     categorical_str: str,
                     corr_threshold=0.85,
                     max_pcs=10,
                     top_frac=0.2,
                     vif_threshold=10.0,
                     use_lasso=True):
    """
    Full PCA-based variable selection pipeline.

    Parameters
    - metadata_df: DataFrame of metadata (must contain numeric columns and 'otu_richness')
    - corr_threshold: pairwise correlation cutoff for redundancy removal
    - max_pcs: maximum number of PCs to compute/consider
    - top_frac: fraction of top variables by importance to consider initially
    - vif_threshold: VIF threshold for iterative removal
    - use_lasso: whether to refine selection with LassoCV

    Returns
    - summary: dict containing output paths, selected variables, PCA objects and reports

    Notes on interpretation:
    - Examine `report_df` (variable importance + per-PC loadings) to see which
      variables drive each principal component. High absolute loading on PC1
      means the variable is strongly associated with PC1 direction.
    - Use biplots (samples colored by groups) and loadings heatmap to interpret
      multivariate patterns. Scores show where samples project on PCs; loadings
      show how variables align with those projections.
    """
    numeric, var_names, categorical = _prepare_metadata(metadata_df, categorical_str)
    Xs, scaler = _standardize(numeric)
    n_vars = len(var_names)
    n_components = min(max_pcs, n_vars)
    pca, scores, loadings = _fit_pca(Xs, n_components=n_components)
    explained_variance = pca.explained_variance_ratio_

    outdir = _ensure_outdir()
    _plot_scree(pca, outdir)
    if scores.shape[1] >= 2:
        _plot_biplot(scores, loadings, var_names, outdir, categorical)
    heatmap_fp, loadings_df = _plot_loadings_heatmap(loadings, var_names, outdir)

    # importance score and basic report
    importance = _importance_from_loadings(loadings, explained_variance)
    importance_dict = dict(zip(var_names, importance))
    corr_with_otu = _correlations_with_otu(numeric, var_names)

    report_rows = []
    for i, v in enumerate(var_names):
        r, p = corr_with_otu.get(v, (np.nan, np.nan))
        row = {
            "variable": v,
            "importance": importance_dict.get(v, 0.0),
            "corr_with_otu_r": r,
            "pval_with_otu": p,
        }
        for pc_idx in range(loadings.shape[1]):
            row[f"pc{pc_idx+1}_loading"] = loadings[i, pc_idx]
        report_rows.append(row)
    report_df = pd.DataFrame(report_rows).sort_values("importance", ascending=False)

    # initial candidate set: top fraction by importance, at least top 3
    k = max(3, int(np.ceil(len(var_names) * top_frac)))
    candidates = report_df["variable"].tolist()[:k]

    # remove pairwise-correlated variables
    candidates = _pairwise_filter_by_corr(numeric, candidates, corr_threshold, importance_dict, corr_with_otu)

    # iterative VIF filtering
    candidates_vif_filtered, vif_dict = _iterative_vif_filter(numeric, candidates, threshold=vif_threshold)
    # optional lasso refinement
    lasso_selected = []
    lasso_coefs = pd.Series(dtype=float)
    if use_lasso and len(candidates_vif_filtered) >= 1:
        lasso_selected, lasso_coefs = _lasso_select(numeric, candidates_vif_filtered, "otu_richness")
        if len(lasso_selected) > 0:
            # intersect Lasso selection with candidates (gives priority to Lasso)
            final_selected = [v for v in candidates_vif_filtered if v in lasso_selected]
            if len(final_selected) == 0:
                final_selected = candidates_vif_filtered
        else:
            final_selected = candidates_vif_filtered
    else:
        final_selected = candidates_vif_filtered

    # write reports
    report_df.to_csv(outdir / "pca_variable_importance_and_loadings.csv", index=False)

    vif_df = pd.DataFrame(list(vif_dict.items()), columns=["variable", "VIF"]) if vif_dict else pd.DataFrame(columns=["variable","VIF"])
    vif_df.to_csv(outdir / "vif_after_filtering.csv", index=False)

    pd.Series(final_selected, name="selected_variables").to_csv(outdir / "selected_variables.csv", index=False)
    if not lasso_coefs.empty:
        lasso_coefs.to_csv(outdir / "lasso_coefficients.csv")

    summary = {
        "outdir": outdir,
        "n_components": n_components,
        "explained_variance": explained_variance,
        "selected_variables": final_selected,
        "lasso_selected": lasso_selected,
        "report_df": report_df,
        "pca": pca,
        "loadings": loadings,
    }

    print(f"PCA outputs and selection results written to: {outdir}")
    return summary

if __name__ == "__main__":
    # quick-run for interactive usage
    categorical_str = 'land_use'
    df = load_data()
    summary = run_pca_metadata(df, categorical_str)
