import numpy as np
import pandas as pd
from imblearn.combine import SMOTETomek

def gaussian_noise_sampler(X, y, target_groups=None, sigma_percentage=0.01):
    """
    Inject Gaussian noise to simulate measurement errors (FunctionSampler).
    Note: For a simple pipeline, it might just augment the minority class.
    We return the original data combined with noisy data.
    """
    X_df = pd.DataFrame(X)
    
    # Default target features based on config
    if target_groups is None:
        target_groups = [
            "cell_diameter_um", "cell_area_px", "perimeter_px", "cytoplasm_ratio", 
            "membrane_smoothness", "granularity_score", "mean_r", "mean_g", "mean_b"
        ]
        
    cols_to_noise = [c for c in target_groups if c in X_df.columns]
    
    if not cols_to_noise:
        return X, y
        
    noisy_X = X_df.copy()
    for col in cols_to_noise:
        std_dev = noisy_X[col].std()
        noise = np.random.normal(0, sigma_percentage * std_dev, size=len(noisy_X))
        noisy_X[col] = noisy_X[col] + noise
        
    # Combine original and noisy data
    X_combined = pd.concat([X_df, noisy_X], axis=0, ignore_index=True)
    
    if y is not None:
        if isinstance(y, pd.Series):
            y_combined = pd.concat([y, y], axis=0, ignore_index=True)
        else:
            y_combined = np.concatenate([y, y], axis=0)
    else:
        y_combined = None
        
    return X_combined, y_combined

def get_smote_tomek(random_state=42):
    """
    Get SMOTETomek object for class imbalance handling.
    """
    return SMOTETomek(random_state=random_state)
