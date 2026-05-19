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
    Builds the end-to-end preprocessing pipeline (15 steps).

    Step order and rationale
    ────────────────────────
    Member 1 — Numeric Processing (Steps 1-4)
      1.  Row filtering      : keep labeller_confidence_score ≥ 0.5, then drop column later
      2.  IQR trimming       : remove measurement-error outliers in Group C
      3.  Drop leakage/ID    : disease_category, cytodiffusion_*, cell_id, …
      4.  Physical units     : cell_area_px → true_cell_area, perimeter_px → true_perimeter

    Member 2 — Categorical & Feature Engineering (Steps 5-9)
      5.  Protocol shifting  : normalise mean_r/g/b BEFORE computing chromaticity ratios
                               so ratios are derived from bias-free color values
      6.  Feature engineering: NC ratio, form factor, chromaticity (from shifted colors),
                               size anomaly
      7.  Drop source columns: remove features now encoded by engineered ones to prevent
                               multicollinearity (nucleus_area_pct → nc_ratio, etc.)
      8.  Categorical encoding
      9.  Drop utility columns (magnification_x, image_resolution_px, labeller_confidence)
     10.  Numeric scaling — ColumnTransformer per group
     11.  GMM clustering
     12.  Gaussian noise augmentation
     13.  Covariate shift augmentation

    Member 3 — Feature Selection & Validation (Steps 14-15)
     14.  Feature selection (VIF → Correlation → Mutual Information → RFECV)
     15.  SMOTE-Tomek (class imbalance handling)
    """

    # ── Feature group definitions (post-engineering drops already excluded) ──────
    # Group A: Pathology Signals — critical, keep outliers via capping
    group_a_features = [
        "eccentricity", "lobularity_score", "chromatin_density",
        # nucleus_area_pct REMOVED → replaced by nc_ratio (monotonic bijection)
        "circularity",
    ]

    # Group B: Morphology — multi-modal distributions, no raw pixel cols
    group_b_features = [
        # cell_diameter_um REMOVED → encoded by size_anomaly (ratio with mcv_fl); keeping
        #   both would give VIF > 10 since size_anomaly is a direct function of cell_diameter_um
        # cell_area_px     REMOVED → replaced by true_cell_area (physical units)
        # perimeter_px     REMOVED → replaced by true_perimeter then dropped (see below)
        "cytoplasm_ratio", "membrane_smoothness", "granularity_score",
    ]

    # Group C: Hematology / Technical noise — symmetric, low separability
    group_c_features = [
        "wbc_count_per_ul", "rbc_count_millions_per_ul", "hemoglobin_g_dl",
        "hematocrit_pct", "platelet_count_per_ul",
        # mcv_fl        REMOVED → encoded by size_anomaly (ratio with cell_diameter_um); keeping
        #   both would give VIF > 10 since size_anomaly is a direct function of mcv_fl
        "mchc_g_dl",
        # mean_r/g/b    REMOVED → replaced by r_ratio, g_ratio (chromaticity)
        # stain_intensity REMOVED → after protocol shifting, stain_intensity = f(mean_r+mean_g+mean_b)
        #   whose components are already dropped; retaining the sum adds no independent signal
        #   and is flagged by VIF (high collinearity with r_ratio + g_ratio).
    ]

    # Engineered features: NC ratio, shape, color ratios, size, physical units
    engineered_features = [
        "nc_ratio", "form_factor",
        "r_ratio", "g_ratio",
        # b_ratio       REMOVED → r_ratio + g_ratio + b_ratio ≡ 1 (perfect linear dependency)
        "size_anomaly",
        "true_cell_area",
        # true_perimeter REMOVED → form_factor is computed directly as
        #   4π·true_cell_area / true_perimeter² (Step 6 uses physical-unit columns);
        #   keeping true_perimeter alongside true_cell_area + form_factor gives VIF = ∞
    ]

    # ── Numeric sub-pipelines for ColumnTransformer (Step 10) ────────────────────
    # Group A: Capping [1,99] → Yeo-Johnson → RobustScaler
    #   Rationale: heavy skew + critical outliers; RobustScaler protects against them
    group_a_pipe = Pipeline([
        ('capper', OutlierCapper(percentiles=(1, 99))),
        ('yeo_johnson', PowerTransformer(method='yeo-johnson')),
        ('scaler', RobustScaler()),
    ])

    # Group B: Capping [1,99] → QuantileTransformer(uniform) → StandardScaler
    #   Rationale: multi-modal distributions; quantile transform flattens peaks
    group_b_pipe = Pipeline([
        ('capper', OutlierCapper(percentiles=(1, 99))),
        ('quantile', QuantileTransformer(output_distribution='uniform', random_state=42)),
        ('scaler', StandardScaler()),
    ])

    # Group C: MinMaxScaler only
    #   Rationale: already Gaussian after IQR trimming; simplest appropriate scaler
    group_c_pipe = Pipeline([
        ('scaler', MinMaxScaler()),
    ])

    # Engineered features: StandardScaler
    engineered_pipe = Pipeline([
        ('scaler', StandardScaler()),
    ])

    numeric_ct = ColumnTransformer(
        transformers=[
            ('group_a',    group_a_pipe,    group_a_features),
            ('group_b',    group_b_pipe,    group_b_features),
            ('group_c',    group_c_pipe,    group_c_features),
            ('engineered', engineered_pipe, engineered_features),
        ],
        remainder='passthrough',
        verbose_feature_names_out=False,
    )
    numeric_ct.set_output(transform="pandas")

    # ── Full pipeline ─────────────────────────────────────────────────────────────
    full_pipeline = ImbPipeline([

        # Step 1: Filter low-confidence rows
        ('conf_filter', FunctionSampler(
            func=confidence_filter_sampler,
            kw_args={"threshold": 0.5},
            validate=False,
        )),

        # Step 2: IQR trimming for Group C outliers (measurement errors)
        ('iqr_trimmer', FunctionSampler(
            func=iqr_trimming_sampler,
            kw_args={"features": group_c_features + ["mean_r", "mean_g", "mean_b"],
                     "iqr_multiplier": 1.5},
            validate=False,
        )),

        # Step 3: Drop leakage & ID columns
        ('drop_leakage', ColumnDropper(columns=[
            "cell_id",
            "cell_type",
            "disease_category",
            "dataset_source",
            "microscope_model",
            "cytodiffusion_anomaly_score",
            "cytodiffusion_classification_confidence",
        ])),

        # Step 4: Physical unit normalization (needs magnification_x)
        ('phys_norm', PhysicalUnitNormalizer()),

        # Step 5: Protocol shifting — MUST run before chromaticity ratios
        #   Normalises mean_r/g/b across staining protocols so that chromaticity
        #   ratios computed next reflect true hue, not staining-protocol bias.
        ('protocol_shift', ProtocolShifter(
            target_features=["mean_r", "mean_g", "mean_b", "stain_intensity"],
            protocol_col="staining_protocol",
        )),

        # Step 6: Feature engineering (chromaticity uses already-shifted colors)
        ('feature_eng', FeatureEngineer()),

        # Step 7: Drop source features that are now encoded by engineered ones
        #   Avoids multicollinearity before scaling & selection:
        #   nucleus_area_pct → nc_ratio          (monotonic bijection, VIF = ∞)
        #   cell_area_px     → true_cell_area + form_factor
        #   perimeter_px     → true_perimeter, then true_perimeter itself dropped below
        #   mean_r/g/b       → r_ratio, g_ratio  (chromaticity, post-shift)
        #   b_ratio          → 1 - r_ratio - g_ratio (perfect linear dependency, VIF = ∞)
        #   stain_intensity  → dropped: = f(mean_r+mean_g+mean_b) whose components are already
        #                      removed; retaining the sum inflates VIF with r_ratio + g_ratio.
        #   cell_diameter_um → size_anomaly      (direct divisor, elevated VIF)
        #   mcv_fl           → size_anomaly      (direct divisor, elevated VIF)
        #   true_perimeter   → form_factor = 4π·true_cell_area/true_perimeter² (VIF = ∞)
        ('drop_engineered_sources', ColumnDropper(columns=[
            "nucleus_area_pct",
            "cell_area_px",
            "perimeter_px",
            "mean_r", "mean_g", "mean_b",
            "b_ratio",
            "stain_intensity",
            "cell_diameter_um",
            "mcv_fl",
            "true_perimeter",
        ])),

        # Step 8: Categorical encoding
        ('categorical_proc', CategoricalProcessor(config=config)),

        # Step 9: Drop utility columns no longer needed
        ('drop_utility', ColumnDropper(columns=[
            "magnification_x",
            "image_resolution_px",
            "labeller_confidence_score",
        ])),

        # Step 10: Numeric scaling per group (ColumnTransformer)
        ('numeric_ct', numeric_ct),

        # Step 11: GMM clustering — adds cell_subpopulation feature
        ('gmm_cluster', GMMClusterer(n_components_range=(3, 5))),

        # Step 12: Gaussian noise on Group B + physical engineered features
        #   cell_diameter_um / true_perimeter / stain_intensity dropped in Step 7; targets updated
        ('gaussian_noise', FunctionSampler(
            func=gaussian_noise_sampler,
            kw_args={
                "target_features": [
                    # cell_diameter_um  REMOVED — dropped in Step 7
                    "cytoplasm_ratio", "membrane_smoothness", "granularity_score",
                    "true_cell_area",
                    # true_perimeter    REMOVED — dropped in Step 7
                    # stain_intensity   REMOVED — dropped in Step 7 (VIF with r_ratio/g_ratio)
                ],
                "sigma_percentage": 0.01,
            },
            validate=False,
        )),

        # Step 13: Covariate shift on Group C hematology features
        ('covariate_shift', FunctionSampler(
            func=covariate_shift_sampler,
            kw_args={
                "target_features": [
                    "wbc_count_per_ul", "rbc_count_millions_per_ul", "hemoglobin_g_dl",
                    "hematocrit_pct", "platelet_count_per_ul",
                    # mcv_fl REMOVED — dropped in Step 7
                    "mchc_g_dl",
                ],
                "factor_range": (0.98, 1.02),
            },
            validate=False,
        )),

        # Step 14: Feature selection (VIF → Correlation → MI → RFECV)
        ('feature_select', FeatureSelector(config=config)),

        # Step 15: Imbalance handling
        ('smote_tomek', get_smote_tomek()),
    ])

    return full_pipeline


def build_full_pipeline(classifier, config=None):
    """Combines preprocessing pipeline with a classifier (flat, no nesting)."""
    preprocessor = build_preprocessing_pipeline(config=config)
    steps = preprocessor.steps + [('classifier', classifier)]
    return ImbPipeline(steps)
