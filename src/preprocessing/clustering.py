import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.mixture import GaussianMixture

class GMMClusterer(BaseEstimator, TransformerMixin):
    """
    Apply GMM Clustering on specified features and add cluster ID as a new feature.
    Dynamically selects optimal n_components using BIC in range [3, 5].
    """
    def __init__(self, features=None, n_components_range=(3, 5), random_state=42):
        # Default features based on config
        self.features = features if features is not None else [
            "cell_diameter_um", "nucleus_area_pct", "chromatin_density", 
            "cell_area_px", "cytoplasm_ratio", "granularity_score"
        ]
        self.n_components_range = n_components_range
        self.random_state = random_state
        self.gmm = None
        self.optimal_n_components_ = None
        
    def _find_optimal_components(self, data):
        """Find optimal n_components using BIC."""
        best_bic = float('inf')
        best_n = self.n_components_range[0]
        for n in range(self.n_components_range[0], self.n_components_range[1] + 1):
            gmm = GaussianMixture(n_components=n, random_state=self.random_state)
            gmm.fit(data)
            bic = gmm.bic(data)
            if bic < best_bic:
                best_bic = bic
                best_n = n
        return best_n
        
    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        cols_to_cluster = [c for c in self.features if c in X_df.columns]
        if cols_to_cluster:
            # Handle NaNs before fitting
            data = X_df[cols_to_cluster].fillna(0)
            self.optimal_n_components_ = self._find_optimal_components(data)
            self.gmm = GaussianMixture(n_components=self.optimal_n_components_, random_state=self.random_state)
            self.gmm.fit(data)
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()
        cols_to_cluster = [c for c in self.features if c in X_df.columns]
        if cols_to_cluster and hasattr(self.gmm, 'means_'):
            data = X_df[cols_to_cluster].fillna(0)
            clusters = self.gmm.predict(data)
            X_df['cell_subpopulation'] = clusters
        return X_df

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return None
        return input_features
