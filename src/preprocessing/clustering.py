import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.mixture import GaussianMixture

class GMMClusterer(BaseEstimator, TransformerMixin):
    """
    Apply GMM Clustering on specified features and add cluster ID as a new feature.
    """
    def __init__(self, features=None, n_components=4, random_state=42):
        # Default features based on config
        self.features = features if features is not None else [
            "cell_diameter_um", "nucleus_area_pct", "chromatin_density", 
            "cell_area_px", "cytoplasm_ratio", "granularity_score"
        ]
        self.n_components = n_components
        self.random_state = random_state
        self.gmm = GaussianMixture(n_components=self.n_components, random_state=self.random_state)
        
    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        cols_to_cluster = [c for c in self.features if c in X_df.columns]
        if cols_to_cluster:
            # Handle NaNs before fitting
            data = X_df[cols_to_cluster].fillna(0)
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
