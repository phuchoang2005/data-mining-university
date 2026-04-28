import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import SelectKBest, mutual_info_classif

class FeatureSelector(BaseEstimator, TransformerMixin):
    """
    Feature Selection handling Correlation filter and Mutual Information.
    (VIF is computationally heavy for pipeline transform, so we use correlation).
    """
    def __init__(self, corr_threshold=0.9, k_best=20):
        self.corr_threshold = corr_threshold
        self.k_best = k_best
        self.features_to_drop_ = []
        self.selector_ = None
        self.selected_features_ = []

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        
        # 1. Correlation Filter
        corr_matrix = X_df.corr().abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        self.features_to_drop_ = [column for column in upper.columns if any(upper[column] > self.corr_threshold)]
        
        X_reduced = X_df.drop(columns=self.features_to_drop_)
        
        # 2. Mutual Information
        if y is not None:
            # Handle NaNs before selection
            X_reduced = X_reduced.fillna(0)
            
            # Select K Best
            k = min(self.k_best, X_reduced.shape[1])
            self.selector_ = SelectKBest(score_func=mutual_info_classif, k=k)
            self.selector_.fit(X_reduced, y)
            
            mask = self.selector_.get_support()
            self.selected_features_ = X_reduced.columns[mask].tolist()
        else:
            self.selected_features_ = X_reduced.columns.tolist()
            
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()
        
        # We only keep the selected features
        cols_to_keep = [c for c in self.selected_features_ if c in X_df.columns]
        
        # If transform is called with missing columns, we just return the available ones
        return X_df[cols_to_keep]

    def get_feature_names_out(self, input_features=None):
        return np.array(self.selected_features_)
