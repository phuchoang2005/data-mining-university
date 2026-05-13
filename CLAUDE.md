# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Binary classification of blood cells (Normal vs. Abnormal) using a 5,880-sample dataset with 36 features (numerical + categorical). The primary optimization target is **F1-Score**. Dataset is downloaded from Kaggle via `kagglehub`.

## Commands

```bash
# Install dependencies
pip install -r requirement.txt

# Run the full pipeline (downloads data, trains all models, saves reports)
python main.py

# Run from a Jupyter notebook
# Open exec.ipynb and run all cells
```

There are no test files or linting configurations in this project.

## Architecture

The entry point is `main.py`, which orchestrates the full ML workflow:

1. Load config from `config.yml`
2. Download dataset from Kaggle → `data/raw/`
3. Stratified train/test split
4. For each model: build pipeline → train → evaluate → save to `models/saved/` and `reports/`
5. Select best model by F1 then ROC-AUC, copy to `best_model` path from config

**Key modules in `src/`:**

| Module | Role |
|---|---|
| `config.py` | Loads `config.yml` (single source of truth for all parameters) |
| `data_loader.py` | Downloads from Kaggle (`alitaqishah/blood-cell-anomaly-detection-2025`), copies CSV to `data/raw/` |
| `pipeline.py` | `build_full_pipeline()` — assembles the 14-step `ImbPipeline` |
| `training.py` | Reads model params from config, builds sklearn classifiers, trains pipeline |
| `evaluation.py` | Computes metrics (accuracy, precision, recall, F1, ROC-AUC), saves confusion matrices, ROC curves, SHAP plots |
| `selection.py` | `FeatureSelector` — VIF → Correlation filter → Mutual Information (SelectKBest) → RFECV |

**Preprocessing pipeline steps** (defined in `src/pipeline.py`, assembled in order):

1. Confidence filter — drop rows with `labeller_confidence_score < 0.5`
2. IQR trimming — remove outliers in Group C features (multiplier 1.5)
3. Drop leakage columns — `cell_id`, `disease_category`, `cytodiffusion_*`, etc.
4. Physical unit normalization — convert px measurements to µm using `magnification_x`
5. Feature engineering — NC ratio, form factor, chromaticity ratios, size anomaly
6. Protocol shifting — normalize `mean_r/g/b` across staining protocols
7. Categorical encoding — OHE for `staining_protocol`/`patient_sex`, ordinal for `patient_age_group`
8. Drop utility columns — `magnification_x`, `image_resolution_px`, `labeller_confidence_score`
9. Numeric scaling — `ColumnTransformer` per group (A: Yeo-Johnson+RobustScaler, B: Quantile+StandardScaler, C: MinMaxScaler, engineered: StandardScaler)
10. GMM clustering — adds cluster membership features (n_components in [3,5])
11. Gaussian noise augmentation — Group B & C features, σ=1%
12. Covariate shift augmentation — Group C hematology features, factor [0.98, 1.02]
13. Feature selection — VIF + Correlation + MI + RFECV
14. SMOTE-Tomek — handles class imbalance

**Feature groups** (all defined explicitly in `pipeline.py`, not read from config):
- **Group A** — pathology signals: `eccentricity`, `lobularity_score`, `chromatin_density`, `nucleus_area_pct`, `circularity`
- **Group B** — morphology: `cell_diameter_um`, `cell_area_px`, `perimeter_px`, `cytoplasm_ratio`, `membrane_smoothness`, `granularity_score`
- **Group C** — hematological indices: CBC counts, RGB color channels, `stain_intensity`
- **Group D** — governance/metadata: dropped to prevent leakage

**Models trained** (configured in `config.yml` under `model_training.models`):
Decision Tree, Naive Bayes, KNN, Logistic Regression, Random Forest, XGBoost

## Configuration

All pipeline parameters live in `config.yml` — model hyperparameters, output paths, feature selection thresholds, data augmentation settings. When adding or tuning a model, edit `config.yml`; `training.py` reads params dynamically.

Output paths for models and reports are also defined in `config.yml` under `output.leader.*`.

## Data & Output Layout

```
data/raw/          ← downloaded CSV lands here
data/intermediate/ ← intermediate processed data
data/processed/    ← final processed data
models/saved/      ← per-model .pkl files + best_model.pkl
reports/           ← confusion matrices, ROC curves, SHAP plots, JSON summary
reports/feature_selection/ ← VIF, correlation, MI, RFE CSV reports
```
