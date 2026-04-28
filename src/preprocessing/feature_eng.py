import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class FeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Compute domain-based features: N/C Ratio, Form Factor, Chromaticity, Size Anomaly.
    """
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()
        
        # 1. N/C Ratio
        if 'nucleus_area_pct' in X_df.columns:
            # Add small epsilon to prevent division by zero
            denom = np.maximum(100 - X_df['nucleus_area_pct'], 1e-6)
            X_df['nc_ratio'] = X_df['nucleus_area_pct'] / denom
            
        # 3. Form Factor (Shape Complexity)
        if 'cell_area_px' in X_df.columns and 'perimeter_px' in X_df.columns:
            denom = np.maximum(X_df['perimeter_px'] ** 2, 1e-6)
            X_df['form_factor'] = (4 * np.pi * X_df['cell_area_px']) / denom
            
        # 4. Chromaticity
        if all(c in X_df.columns for c in ['mean_r', 'mean_g', 'mean_b']):
            total_color = X_df['mean_r'] + X_df['mean_g'] + X_df['mean_b']
            total_color = np.maximum(total_color, 1e-6)
            X_df['r_ratio'] = X_df['mean_r'] / total_color
            X_df['g_ratio'] = X_df['mean_g'] / total_color
            X_df['b_ratio'] = X_df['mean_b'] / total_color
            
        # 5. Global-Local Interaction (Size Anomaly)
        if 'cell_diameter_um' in X_df.columns and 'mcv_fl' in X_df.columns:
            denom = np.maximum(X_df['mcv_fl'], 1e-6)
            X_df['size_anomaly'] = X_df['cell_diameter_um'] / denom
            
        return X_df

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return None
        return input_features
