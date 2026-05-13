import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder


class CategoricalProcessor(BaseEstimator, TransformerMixin):
    """
    Handle categorical features: one-hot encode staining_protocol and patient_sex,
    ordinal encode patient_age_group, and preserve remaining numerical features.
    """

    def __init__(self, config=None):
        self.config = config
        self.ohe = None
        self.ordinal_encoder = None
        self.ohe_cols = ["staining_protocol", "patient_sex"]
        self.ordinal_cols = ["patient_age_group"]

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X).copy()

        # Fit One Hot Encoder for selected columns
        cols_to_ohe = [c for c in self.ohe_cols if c in X_df.columns]
        if cols_to_ohe:
            self.ohe = OneHotEncoder(
                handle_unknown='ignore', sparse_output=False, drop='if_binary'
            )
            self.ohe.fit(X_df[cols_to_ohe])
            self.ohe_feature_names_ = self.ohe.get_feature_names_out(cols_to_ohe)

        # Fit Ordinal Encoder for patient_age_group
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

        # Apply One Hot Encoding for selected columns
        if self.ohe is not None:
            cols_to_ohe = [c for c in self.ohe_cols if c in X_df.columns]
            if cols_to_ohe:
                ohe_vals = self.ohe.transform(X_df[cols_to_ohe])
                ohe_df = pd.DataFrame(
                    ohe_vals, columns=self.ohe_feature_names_, index=X_df.index
                )
                X_df = pd.concat([X_df.drop(columns=cols_to_ohe), ohe_df], axis=1)

        # Apply Ordinal Encoding for patient_age_group
        if self.ordinal_encoder is not None:
            cols_to_ord = [c for c in self.ordinal_cols if c in X_df.columns]
            if cols_to_ord:
                X_df[cols_to_ord] = self.ordinal_encoder.transform(X_df[cols_to_ord])

        return X_df

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return None
        return input_features
