import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class OutlierCapper(BaseEstimator, TransformerMixin):
    """Cap outliers at specified percentiles (e.g., 1st and 99th)."""

    def __init__(self, features=None, percentiles=(1, 99)):
        self.features = features
        self.percentiles = percentiles
        self.lower_bounds_ = {}
        self.upper_bounds_ = {}

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        cols = self.features if self.features is not None else X_df.columns
        for col in cols:
            if col in X_df.columns:
                self.lower_bounds_[col] = np.percentile(X_df[col].dropna(), self.percentiles[0])
                self.upper_bounds_[col] = np.percentile(X_df[col].dropna(), self.percentiles[1])
        return self

    def transform(self, X):
        X_copy = pd.DataFrame(X).copy()
        for col, lower in self.lower_bounds_.items():
            upper = self.upper_bounds_[col]
            if col in X_copy.columns:
                X_copy[col] = np.clip(X_copy[col], lower, upper)
        return X_copy

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return np.array(list(self.lower_bounds_.keys()))
        return input_features


def iqr_trimming_sampler(X, y, features=None, iqr_multiplier=1.5):
    """Remove outlier rows based on IQR for specified features."""
    X_df = pd.DataFrame(X).reset_index(drop=True)
    y_s = pd.Series(y).reset_index(drop=True) if y is not None else None
    cols = features if features is not None else X_df.select_dtypes(include=[np.number]).columns

    mask = pd.Series(True, index=X_df.index)
    for col in cols:
        if col in X_df.columns:
            Q1 = X_df[col].quantile(0.25)
            Q3 = X_df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - iqr_multiplier * IQR
            upper_bound = Q3 + iqr_multiplier * IQR
            col_mask = (X_df[col] >= lower_bound) & (X_df[col] <= upper_bound)
            mask = mask & col_mask

    X_out = X_df[mask].reset_index(drop=True)
    y_out = y_s[mask].reset_index(drop=True) if y_s is not None else None
    return X_out, y_out


def confidence_filter_sampler(X, y, confidence_col="labeller_confidence_score", threshold=0.5):
    """Filter rows where confidence score is below threshold."""
    X_df = pd.DataFrame(X).reset_index(drop=True)
    y_s = pd.Series(y).reset_index(drop=True) if y is not None else None

    if confidence_col in X_df.columns:
        mask = X_df[confidence_col] >= threshold
        X_out = X_df[mask].reset_index(drop=True)
        y_out = y_s[mask].reset_index(drop=True) if y_s is not None else None
        return X_out, y_out
    return X_df, y_s


class PhysicalUnitNormalizer(BaseEstimator, TransformerMixin):
    """Normalize pixel-based features to real units based on magnification."""

    def __init__(self, area_col="cell_area_px", perimeter_col="perimeter_px", mag_col="magnification_x"):
        self.area_col = area_col
        self.perimeter_col = perimeter_col
        self.mag_col = mag_col

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_copy = pd.DataFrame(X).copy()
        mag = X_copy[self.mag_col] if self.mag_col in X_copy.columns else 1.0

        if self.area_col in X_copy.columns:
            X_copy['true_cell_area'] = X_copy[self.area_col] / (mag ** 2)
        if self.perimeter_col in X_copy.columns:
            X_copy['true_perimeter'] = X_copy[self.perimeter_col] / mag

        return X_copy

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return None
        return input_features
