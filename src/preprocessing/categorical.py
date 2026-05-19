import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder


class CategoricalProcessor(BaseEstimator, TransformerMixin):
    """
    Handle categorical features: one-hot encode staining_protocol and patient_sex,
    ordinal encode patient_age_group, and preserve remaining numerical features.

    Drop strategy for OHE:
      - staining_protocol (3 categories): drop='first' → k-1=2 dummies (avoids dummy trap)
      - patient_sex       (2 categories): drop='if_binary' → 1 dummy

    NOTE: sklearn's drop parameter, when given a list, treats each element as a
    *literal category value* to drop — not a strategy string. Two separate
    OneHotEncoder instances are therefore used so each can carry its own string strategy.
    """

    def __init__(self, config=None):
        self.config = config
        # Two separate OHE instances — one per feature — so each can use its own
        # drop strategy string ('first' vs 'if_binary') without sklearn
        # misinterpreting them as literal category labels.
        self.ohe_staining = None   # staining_protocol → drop='first'
        self.ohe_sex = None        # patient_sex       → drop='if_binary'
        self.ordinal_encoder = None
        self.ohe_cols = ["staining_protocol", "patient_sex"]
        self.ordinal_cols = ["patient_age_group"]

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X).copy()

        # ── staining_protocol: drop first category (3-class → 2 dummies) ─────────
        if "staining_protocol" in X_df.columns:
            self.ohe_staining = OneHotEncoder(
                handle_unknown='ignore', sparse_output=False, drop='first'
            )
            self.ohe_staining.fit(X_df[["staining_protocol"]])

        # ── patient_sex: drop if binary (2-class → 1 dummy) ──────────────────────
        if "patient_sex" in X_df.columns:
            self.ohe_sex = OneHotEncoder(
                handle_unknown='ignore', sparse_output=False, drop='if_binary'
            )
            self.ohe_sex.fit(X_df[["patient_sex"]])

        # ── patient_age_group: ordinal encoding ───────────────────────────────────
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

        # ── staining_protocol ─────────────────────────────────────────────────────
        if self.ohe_staining is not None and "staining_protocol" in X_df.columns:
            staining_vals = self.ohe_staining.transform(X_df[["staining_protocol"]])
            staining_df = pd.DataFrame(
                staining_vals,
                columns=self.ohe_staining.get_feature_names_out(["staining_protocol"]),
                index=X_df.index,
            )
            X_df = pd.concat([X_df.drop(columns=["staining_protocol"]), staining_df], axis=1)

        # ── patient_sex ───────────────────────────────────────────────────────────
        if self.ohe_sex is not None and "patient_sex" in X_df.columns:
            sex_vals = self.ohe_sex.transform(X_df[["patient_sex"]])
            sex_df = pd.DataFrame(
                sex_vals,
                columns=self.ohe_sex.get_feature_names_out(["patient_sex"]),
                index=X_df.index,
            )
            X_df = pd.concat([X_df.drop(columns=["patient_sex"]), sex_df], axis=1)

        # ── patient_age_group ─────────────────────────────────────────────────────
        if self.ordinal_encoder is not None:
            cols_to_ord = [c for c in self.ordinal_cols if c in X_df.columns]
            if cols_to_ord:
                X_df[cols_to_ord] = self.ordinal_encoder.transform(X_df[cols_to_ord])

        return X_df

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return None
        return input_features
