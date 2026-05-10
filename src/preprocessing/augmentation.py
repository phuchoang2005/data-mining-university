import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from imblearn.combine import SMOTETomek


def gaussian_noise_sampler(X, y, target_features=None, sigma_percentage=0.01):
    """
    Inject Gaussian noise to simulate measurement errors (FunctionSampler).
    Config: data_augmentation.gaussian_noise
    - target_groups: group_b + group_c (specific features)
    - sigma_percentage: 0.01 (1% of standard deviation)
    """
    X_df = pd.DataFrame(X).reset_index(drop=True)
    y_s = pd.Series(y).reset_index(drop=True) if y is not None else None

    # Default target features from config
    if target_features is None:
        target_features = [
            "cell_diameter_um", "cell_area_px", "perimeter_px", "cytoplasm_ratio",
            "membrane_smoothness", "granularity_score", "mean_r", "mean_g", "mean_b",
            "cell_type"
        ]

    cols_to_noise = [c for c in target_features if c in X_df.columns]

    if not cols_to_noise:
        return X_df, y_s

    noisy_X = X_df.copy()
    for col in cols_to_noise:
        std_dev = noisy_X[col].std()
        noise = np.random.normal(0, sigma_percentage * std_dev, size=len(noisy_X))
        noisy_X[col] = noisy_X[col] + noise

    # Combine original and noisy data
    X_combined = pd.concat([X_df, noisy_X], axis=0, ignore_index=True)

    if y_s is not None:
        y_combined = pd.concat([y_s, y_s], axis=0, ignore_index=True)
    else:
        y_combined = None

    return X_combined, y_combined


class ProtocolShifter(BaseEstimator, TransformerMixin):
    """
    Normalize color features across different staining protocols via group-wise normalization.
    Config: data_augmentation.protocol_shifting
    - target_features: ["mean_r", "mean_g", "mean_b", "stain_intensity"]
    - method: group_wise_normalization
    - Shifts each protocol group's mean to the global mean.
    """

    def __init__(self, target_features=None, protocol_col="staining_protocol"):
        self.target_features = target_features or [
            "mean_r", "mean_g", "mean_b", "stain_intensity"
        ]
        self.protocol_col = protocol_col
        self.global_means_ = {}
        self.group_means_ = {}

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        if self.protocol_col not in X_df.columns:
            return self

        cols = [c for c in self.target_features if c in X_df.columns]
        for col in cols:
            self.global_means_[col] = X_df[col].mean()
            self.group_means_[col] = X_df.groupby(self.protocol_col)[col].mean().to_dict()
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()
        if self.protocol_col not in X_df.columns:
            return X_df

        cols = [c for c in self.target_features if c in X_df.columns]
        # Cast target columns to float64 upfront to avoid int64/float64 dtype conflict
        for col in cols:
            if col in X_df.columns:
                X_df[col] = X_df[col].astype(np.float64)
        for col in cols:
            if col in self.global_means_ and col in self.group_means_:
                global_mean = self.global_means_[col]
                for protocol, group_mean in self.group_means_[col].items():
                    mask = X_df[self.protocol_col] == protocol
                    X_df.loc[mask, col] = X_df.loc[mask, col] + (global_mean - group_mean)
        return X_df

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return None
        return input_features


def covariate_shift_sampler(X, y, target_features=None, factor_range=(0.98, 1.02)):
    """
    Simulate variation between different hospitals by scaling hematology features.
    Config: data_augmentation.covariate_shift
    - target_groups: group_c (hematology features only, not color)
    - factor_range: [0.98, 1.02]
    """
    X_df = pd.DataFrame(X).reset_index(drop=True)
    y_s = pd.Series(y).reset_index(drop=True) if y is not None else None

    # Default target features from config (Group C hematology, excluding color features)
    if target_features is None:
        target_features = [
            "wbc_count_per_ul", "rbc_count_millions_per_ul", "hemoglobin_g_dl",
            "hematocrit_pct", "platelet_count_per_ul", "mcv_fl", "mchc_g_dl"
        ]

    cols_to_shift = [c for c in target_features if c in X_df.columns]
    if not cols_to_shift:
        return X_df, y_s

    shifted_X = X_df.copy()
    for col in cols_to_shift:
        factor = np.random.uniform(factor_range[0], factor_range[1], size=len(shifted_X))
        shifted_X[col] = shifted_X[col] * factor

    # Combine original and shifted data
    X_combined = pd.concat([X_df, shifted_X], axis=0, ignore_index=True)

    if y_s is not None:
        y_combined = pd.concat([y_s, y_s], axis=0, ignore_index=True)
    else:
        y_combined = None

    return X_combined, y_combined


def get_smote_tomek(random_state=42):
    """
    Get SMOTETomek object for class imbalance handling.
    Config: data_augmentation.smote / imbalance_handling
    - method: SMOTE-Tomek Links
    """
    return SMOTETomek(random_state=random_state)
