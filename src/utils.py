import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.base import BaseEstimator, TransformerMixin


def ensure_directory_for_file(filepath):
    """Create output directory for a target file path."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    return filepath


def save_dataframe(df, filepath, index=False):
    """Save a DataFrame to CSV and ensure the output folder exists."""
    ensure_directory_for_file(filepath)
    df.to_csv(filepath, index=index)
    return filepath


def save_figure(fig, filepath, tight_layout=True, bbox_inches='tight'):
    """Save a matplotlib figure to disk."""
    ensure_directory_for_file(filepath)
    if tight_layout:
        fig.tight_layout()
    fig.savefig(filepath, bbox_inches=bbox_inches)
    plt.close(fig)
    return filepath


def save_json(data, filepath, indent=4):
    """Save JSON data to disk."""
    ensure_directory_for_file(filepath)
    with open(filepath, 'w') as f:
        import json
        json.dump(data, f, indent=indent)
    return filepath


class ColumnDropper(BaseEstimator, TransformerMixin):
    """Drop specified columns from the DataFrame."""

    def __init__(self, columns=None):
        self.columns = columns if columns is not None else []

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()
        cols_to_drop = [c for c in self.columns if c in X_df.columns]
        return X_df.drop(columns=cols_to_drop)

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return None
        return np.array([f for f in input_features if f not in self.columns])
