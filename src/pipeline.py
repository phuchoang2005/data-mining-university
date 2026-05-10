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
from .preprocessing.augmentation import (
    get_smote_tomek, gaussian_noise_sampler, ProtocolShifter, covariate_shift_sampler
)
from .selection import FeatureSelector
from .utils import ColumnDropper


def build_preprocessing_pipeline(config=None):
    """
    Builds the end-to-end preprocessing pipeline.
    Matches config.yml pipeline_order (steps 1-14):

      Member 1 - Numeric Processing:
        1. Row filtering (confidence >= 0.5, then drop column later)
        2. IQR trimming for Group C outliers
        3. Drop leakage/ID columns
        4. Physical unit normalization

      Member 2 - Categorical & Feature Engineering:
        5. Feature engineering (needs raw unscaled values)
        6. Protocol shifting (normalize colors across staining protocols)
        7. Categorical encoding
        8. Drop utility columns (no longer needed)
        9. Numeric scaling (ColumnTransformer per group)
       10. GMM clustering
       11. Gaussian noise augmentation (Group B & C features)
       12. Covariate shift augmentation (Group C hematology features)

      Member 3 - Feature Selection & Validation:
       13. Feature selection (Correlation + Mutual Information)
       14. SMOTE-Tomek (class imbalance handling)
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
    # Group A: Capping [1,99] → Yeo-Johnson → RobustScaler (config: numeric_groups.group_a)
    group_a_pipe = Pipeline([
        ('capper', OutlierCapper(percentiles=(1, 99))),
        ('yeo_johnson', PowerTransformer(method='yeo-johnson')),
        ('scaler', RobustScaler())
    ])
    # Group B: Capping [1,99] → QuantileTransformer(uniform) → StandardScaler (config: numeric_groups.group_b)
    group_b_pipe = Pipeline([
        ('capper', OutlierCapper(percentiles=(1, 99))),
        ('quantile', QuantileTransformer(output_distribution='uniform', random_state=42)),
        ('scaler', StandardScaler())
    ])
    # Group C: MinMaxScaler only (config: numeric_groups.group_c)
    group_c_pipe = Pipeline([
        ('scaler', MinMaxScaler())
    ])
    # Engineered features: StandardScaler
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
        # Config: group_d.labeller_confidence_score.threshold = 0.5
        ('conf_filter', FunctionSampler(
            func=confidence_filter_sampler,
            kw_args={"threshold": 0.5},
            validate=False
        )),

        # Step 2: IQR trimming for Group C outliers
        # Config: numeric_groups.group_c.outlier_strategy = trimming, iqr_multiplier = 1.5
        ('iqr_trimmer', FunctionSampler(
            func=iqr_trimming_sampler,
            kw_args={"features": group_c_features, "iqr_multiplier": 1.5},
            validate=False
        )),

        # Step 3: Drop leakage & ID columns
        # Config: categorical_features (cell_id, disease_category, dataset_source, microscope_model)
        # Config: group_d (cytodiffusion_anomaly_score, cytodiffusion_classification_confidence)
        ('drop_leakage', ColumnDropper(columns=[
            "cell_id",                           # ID column
            "disease_category",                  # data leakage
            "dataset_source",                    # no significance (p=0.520)
            "microscope_model",                  # no significance (p=0.408)
            "cytodiffusion_anomaly_score",       # data leakage per config
            "cytodiffusion_classification_confidence",  # data leakage - same cytodiffusion system
        ])),

        # Step 4: Physical unit normalization (needs magnification_x)
        # Config: feature_engineering.physical_units
        ('phys_norm', PhysicalUnitNormalizer()),

        # Step 5: Feature engineering (needs raw unscaled values)
        # Config: feature_engineering (nc_ratio, form_factor, chromaticity, size_anomaly)
        ('feature_eng', FeatureEngineer()),

        # Step 6: Protocol shifting (normalize colors across staining protocols)
        # Config: data_augmentation.protocol_shifting
        # Must run BEFORE categorical encoding (needs raw staining_protocol column)
        ('protocol_shift', ProtocolShifter(
            target_features=["mean_r", "mean_g", "mean_b", "stain_intensity"],
            protocol_col="staining_protocol"
        )),

        # Step 7: Categorical encoding
        # Config: categorical_features (Target: cell_type; OHE: staining_protocol, patient_sex;
        #         Ordinal: patient_age_group; Drop handled in step 3)
        ('categorical_proc', CategoricalProcessor(config=config)),

        # Step 8: Drop utility columns no longer needed
        ('drop_utility', ColumnDropper(columns=[
            "magnification_x",                   # used by PhysicalUnitNormalizer
            "image_resolution_px",               # not in any feature group
            "labeller_confidence_score",          # used for row filtering only
        ])),

        # Step 9: Numeric scaling per group
        ('numeric_ct', numeric_ct),

        # Step 10: GMM clustering
        # Config: clustering (GMM, optimal in [3,5] via BIC)
        ('gmm_cluster', GMMClusterer(n_components_range=(3, 5))),

        # Step 11: Gaussian noise augmentation
        # Config: data_augmentation.gaussian_noise (Group B & C features, sigma 1%)
        ('gaussian_noise', FunctionSampler(
            func=gaussian_noise_sampler,
            kw_args={
                "target_features": [
                    "cell_diameter_um", "cell_area_px", "perimeter_px",
                    "cytoplasm_ratio", "membrane_smoothness", "granularity_score",
                    "mean_r", "mean_g", "mean_b", "cell_type"
                ],
                "sigma_percentage": 0.01
            },
            validate=False
        )),

        # Step 12: Covariate shift augmentation
        # Config: data_augmentation.covariate_shift (Group C hematology, factor [0.98, 1.02])
        ('covariate_shift', FunctionSampler(
            func=covariate_shift_sampler,
            kw_args={
                "target_features": [
                    "wbc_count_per_ul", "rbc_count_millions_per_ul", "hemoglobin_g_dl",
                    "hematocrit_pct", "platelet_count_per_ul", "mcv_fl", "mchc_g_dl"
                ],
                "factor_range": (0.98, 1.02)
            },
            validate=False
        )),

        # Step 13: Feature selection (VIF + Correlation + Mutual Information + RFE)
        # Config: feature_selection (parameters imported from config.yml)
        ('feature_select', FeatureSelector(config=config)),

        # Step 14: Imbalance handling
        # Config: imbalance_handling / data_augmentation.smote (SMOTE-Tomek Links)
        ('smote_tomek', get_smote_tomek())
    ])

    return full_pipeline


def build_full_pipeline(classifier, config=None):
    """Combines preprocessing pipeline with a classifier (flat, no nesting)."""
    preprocessor = build_preprocessing_pipeline(config=config)
    steps = preprocessor.steps + [('classifier', classifier)]
    return ImbPipeline(steps)
