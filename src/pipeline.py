from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn import FunctionSampler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import (
    PowerTransformer, RobustScaler, QuantileTransformer, StandardScaler, MinMaxScaler
)

from .preprocessing.numeric import (
    OutlierCapper, iqr_trimming_sampler, confidence_filter_sampler, PhysicalUnitNormalizer
)
from .preprocessing.categorical import CategoricalProcessor
from .preprocessing.feature_eng import FeatureEngineer
from .preprocessing.clustering import GMMClusterer
from .preprocessing.augmentation import get_smote_tomek
from .selection import FeatureSelector
from .utils import ColumnDropper


def build_preprocessing_pipeline():
    """
    Builds the end-to-end preprocessing pipeline.
    Correct order per config:
      1. Row filtering (confidence, IQR)
      2. Drop leakage/ID columns
      3. Physical unit normalization
      4. Feature engineering (needs raw values)
      5. Categorical encoding
      6. Drop utility columns (no longer needed)
      7. Numeric scaling (ColumnTransformer)
      8. Clustering
      9. Feature selection
     10. SMOTE-Tomek
    """
    # Feature group definitions from config
    group_a_features = [
        "eccentricity", "lobularity_score", "chromatin_density",
        "nucleus_area_pct", "circularity"
    ]
    group_b_features = [
        "cell_diameter_um", "cell_area_px", "perimeter_px",
        "cytoplasm_ratio", "membrane_smoothness", "granularity_score"
    ]
    group_c_features = [
        "wbc_count_per_ul", "rbc_count_millions_per_ul", "hemoglobin_g_dl",
        "hematocrit_pct", "platelet_count_per_ul", "mcv_fl", "mchc_g_dl",
        "mean_r", "mean_g", "mean_b", "stain_intensity"
    ]
    engineered_features = [
        "nc_ratio", "form_factor", "r_ratio", "g_ratio", "b_ratio",
        "size_anomaly", "true_cell_area", "true_perimeter"
    ]

    # --- Numeric group sub-pipelines (used inside ColumnTransformer) ---
    group_a_pipe = Pipeline([
        ('capper', OutlierCapper(percentiles=(1, 99))),
        ('yeo_johnson', PowerTransformer(method='yeo-johnson')),
        ('scaler', RobustScaler())
    ])
    group_b_pipe = Pipeline([
        ('capper', OutlierCapper(percentiles=(1, 99))),
        ('quantile', QuantileTransformer(output_distribution='uniform', random_state=42)),
        ('scaler', StandardScaler())
    ])
    group_c_pipe = Pipeline([
        ('scaler', MinMaxScaler())
    ])
    engineered_pipe = Pipeline([
        ('scaler', StandardScaler())
    ])

    # ColumnTransformer: scale each group differently, passthrough the rest
    numeric_ct = ColumnTransformer(
        transformers=[
            ('group_a', group_a_pipe, group_a_features),
            ('group_b', group_b_pipe, group_b_features),
            ('group_c', group_c_pipe, group_c_features),
            ('engineered', engineered_pipe, engineered_features),
        ],
        remainder='passthrough',
        verbose_feature_names_out=False
    )
    numeric_ct.set_output(transform="pandas")

    # --- Assemble full pipeline ---
    full_pipeline = ImbPipeline([
        # Step 1: Filter low-confidence rows (Group D)
        ('conf_filter', FunctionSampler(
            func=confidence_filter_sampler,
            kw_args={"threshold": 0.5},
            validate=False
        )),

        # Step 2: IQR trimming for Group C outliers
        ('iqr_trimmer', FunctionSampler(
            func=iqr_trimming_sampler,
            kw_args={"features": group_c_features, "iqr_multiplier": 1.5},
            validate=False
        )),

        # Step 3: Drop leakage & ID columns
        ('drop_leakage', ColumnDropper(columns=[
            "cell_id",                           # ID column
            "disease_category",                  # data leakage
            "dataset_source",                    # no significance (p=0.520)
            "microscope_model",                  # no significance (p=0.408)
            "cytodiffusion_anomaly_score",       # data leakage per config
            "cytodiffusion_classification_confidence",  # data leakage - same cytodiffusion system
        ])),

        # Step 4: Physical unit normalization (needs magnification_x)
        ('phys_norm', PhysicalUnitNormalizer()),

        # Step 5: Feature engineering (needs raw unscaled values)
        ('feature_eng', FeatureEngineer()),

        # Step 6: Categorical encoding
        ('categorical_proc', CategoricalProcessor()),

        # Step 7: Drop utility columns no longer needed
        ('drop_utility', ColumnDropper(columns=[
            "magnification_x",                   # used by PhysicalUnitNormalizer
            "image_resolution_px",               # not in any feature group
            "labeller_confidence_score",          # used for row filtering only
        ])),

        # Step 8: Numeric scaling per group
        ('numeric_ct', numeric_ct),

        # Step 9: GMM clustering
        ('gmm_cluster', GMMClusterer(n_components=4)),

        # Step 10: Feature selection
        ('feature_select', FeatureSelector(corr_threshold=0.9, k_best=20)),

        # Step 11: Imbalance handling
        ('smote_tomek', get_smote_tomek())
    ])

    return full_pipeline


def build_full_pipeline(classifier):
    """Combines preprocessing pipeline with a classifier (flat, no nesting)."""
    preprocessor = build_preprocessing_pipeline()
    steps = preprocessor.steps + [('classifier', classifier)]
    return ImbPipeline(steps)
