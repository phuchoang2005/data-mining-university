import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder


class CategoricalProcessor(BaseEstimator, TransformerMixin):
    """
    Handle categorical features: encoding with Target Encoding for cell_type.
    
    WHY Target Encoding with Smoothing for cell_type:
    ─────────────────────────────────────────────────────────────
    Although cell_type has a near-deterministic relationship with anomaly_label 
    (p_value = 0.0), Target Encoding with smoothing can be used to encode it 
    without severe overfitting. Smoothing blends the category-specific mean 
    with the global mean, reducing the risk of memorizing the target.
    
    Formula: smoothed_mean = (count * category_mean + alpha * global_mean) / (count + alpha)
    Higher alpha provides more regularization.
    """

    def __init__(self, config=None, rare_threshold=0.02, smoothing_alpha=None):
        self.config = config
        self.rare_threshold = rare_threshold
        if smoothing_alpha is None:
            if config and 'categorical_features' in config and 'cell_type' in config['categorical_features']:
                self.smoothing_alpha = config['categorical_features']['cell_type'].get('smoothing_alpha', 10)
            else:
                self.smoothing_alpha = 10
        else:
            self.smoothing_alpha = smoothing_alpha
        self.ohe = None
        self.ordinal_encoder = None
        self.target_encoder_map = {}
        self.global_mean = None
        self.rare_categories_ = None

        # cell_type uses Target Encoding with smoothing
        self.target_cols = ["cell_type"]
        self.ohe_cols = ["staining_protocol", "patient_sex"]
        self.ordinal_cols = ["patient_age_group"]

    def _group_rare_types(self, X_df):
        """Group rare cell types (< threshold %) into 'Other_Rare_Types'."""
        X_out = X_df.copy()
        if 'cell_type' in X_out.columns and self.rare_categories_ is not None:
            X_out['cell_type'] = X_out['cell_type'].where(
                ~X_out['cell_type'].isin(self.rare_categories_),
                'Other_Rare_Types'
            )
        return X_out

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X).copy()
        if y is None:
            raise ValueError("y is required for target encoding")

        # Compute global mean
        self.global_mean = y.mean()

        # Learn rare cell type categories
        if 'cell_type' in X_df.columns:
            freq = X_df['cell_type'].value_counts(normalize=True)
            self.rare_categories_ = freq[freq < self.rare_threshold].index.tolist()

        # Group rare types before computing target encoding
        X_df = self._group_rare_types(X_df)

        # Compute target encoding for cell_type
        if 'cell_type' in X_df.columns:
            grouped = pd.DataFrame({'cell_type': X_df['cell_type'], 'target': y}).groupby('cell_type')
            stats = grouped.agg(count=('target', 'size'), mean=('target', 'mean'))
            stats['smoothed'] = (stats['count'] * stats['mean'] + self.smoothing_alpha * self.global_mean) / (stats['count'] + self.smoothing_alpha)
            self.target_encoder_map = stats['smoothed'].to_dict()

        # Fit One Hot Encoder for other columns
        cols_to_ohe = [c for c in self.ohe_cols if c in X_df.columns]
        if cols_to_ohe:
            self.ohe = OneHotEncoder(
                handle_unknown='ignore', sparse_output=False, drop='if_binary'
            )
            self.ohe.fit(X_df[cols_to_ohe])
            self.ohe_feature_names_ = self.ohe.get_feature_names_out(cols_to_ohe)

        # Fit Ordinal Encoder
        cols_to_ord = [c for c in self.ordinal_cols if c in X_df.columns]
        if cols_to_ord:
            categories = [['Pediatric', 'Adult', 'Elderly']]
            self.ordinal_encoder = OrdinalEncoder(
                categories=categories, handle_unknown='use_encoded_value', unknown_value=-1
            )
            self.ordinal_encoder.fit(X_df[cols_to_ord])

        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()

        # Group rare types
        X_df = self._group_rare_types(X_df)

        # Apply Target Encoding for cell_type
        if 'cell_type' in X_df.columns and self.target_encoder_map:
            X_df['cell_type'] = X_df['cell_type'].map(self.target_encoder_map).fillna(self.global_mean)

        # Apply One Hot Encoding for other columns
        if self.ohe is not None:
            cols_to_ohe = [c for c in self.ohe_cols if c in X_df.columns]
            if cols_to_ohe:
                ohe_vals = self.ohe.transform(X_df[cols_to_ohe])
                ohe_df = pd.DataFrame(
                    ohe_vals, columns=self.ohe_feature_names_, index=X_df.index
                )
                X_df = pd.concat([X_df.drop(columns=cols_to_ohe), ohe_df], axis=1)

        # Apply Ordinal Encoding
        if self.ordinal_encoder is not None:
            cols_to_ord = [c for c in self.ordinal_cols if c in X_df.columns]
            if cols_to_ord:
                X_df[cols_to_ord] = self.ordinal_encoder.transform(X_df[cols_to_ord])

        return X_df

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return None
        return input_features
