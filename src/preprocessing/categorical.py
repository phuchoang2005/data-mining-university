import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder


class CategoricalProcessor(BaseEstimator, TransformerMixin):
    """
    Handle categorical features: encoding only.
    Column dropping is handled by ColumnDropper in the pipeline.

    WHY One-Hot Encoding for cell_type instead of Target Encoding:
    ─────────────────────────────────────────────────────────────
    In this dataset, cell_type has a near-deterministic relationship with
    anomaly_label (p_value = 0.0). Target Encoding replaces each cell type
    with a value derived from the target (mean of anomaly_label per type).

    Even with sklearn's internal CV and Bayesian smoothing, the encoded value
    is essentially the probability of being anomalous for that cell type.
    When the relationship is deterministic (each cell type maps 100% to 0 or 1),
    the encoded column becomes a near-perfect copy of the target — regardless
    of smoothing or CV folds — because the signal is too strong to regularize.

    One-Hot Encoding avoids this by encoding cell type IDENTITY (binary
    indicators) without embedding ANY target information. The model must then
    learn the cell_type → anomaly relationship from the other features in
    combination with the OHE indicators, which produces genuine generalization.
    """

    def __init__(self, config=None, rare_threshold=0.02):
        self.config = config
        self.rare_threshold = rare_threshold
        self.ohe = None
        self.ordinal_encoder = None
        self.rare_categories_ = None

        # cell_type uses OHE — see docstring for rationale
        self.ohe_cols = ["cell_type", "staining_protocol", "patient_sex"]
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

        # Learn rare cell type categories
        if 'cell_type' in X_df.columns:
            freq = X_df['cell_type'].value_counts(normalize=True)
            self.rare_categories_ = freq[freq < self.rare_threshold].index.tolist()

        # Group rare types before fitting OHE
        X_df = self._group_rare_types(X_df)

        # Fit One Hot Encoder
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

        # Apply One Hot Encoding
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
