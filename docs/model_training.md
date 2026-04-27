# Model Training & Evaluation Guide for Team Leader

This document provides a step-by-step guide for the Team Leader to train, tune, and evaluate classification models after pre-processing is complete. All pre-processing and feature engineering steps must be finished by Members 1-3 before starting.

---

## 1. Input Data

- **File:** `data/processed/model_input.csv`
- **Target column:** `anomaly_label`
- **Features:** All selected and engineered features from the pipeline

---

## 2. Models to Train

Train and compare the following 8 models:

- Decision Tree
- Naive Bayes (GaussianNB)
- K-Nearest Neighbors (KNN)
- Logistic Regression
- Random Forest
- XGBoost
- Support Vector Machine (SVM)
- Multi-Layer Perceptron (MLP)

---

## 3. Training & Validation

- Use **Stratified K-Fold Cross-Validation** (n_splits=5, shuffle=True, random_state=42)
- Use **Grid Search** for hyperparameter tuning (see config.yml for parameter grids)
- Optimize for **F1-score** (primary) and **ROC-AUC** (secondary)
- Use all CPU cores for parallel search (`n_jobs=-1`)

---

## 4. Evaluation Metrics

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Confusion Matrix
- Training time (seconds)

---

## 5. Model Selection

- Select the best model based on **F1-score** (handle class imbalance)
- Use ROC-AUC as a tiebreaker if needed
- Save all trained models to `models/saved/`
- Save the best model to `models/best_model.pkl`

---

## 6. Reporting

- Save evaluation metrics for all models to `models/metrics.json`
- Generate and save:
  - Training report: `reports/training_report.md`
  - Evaluation report: `reports/evaluation_report.md`
  - Confusion matrix: `reports/confusion_matrix.png`
  - ROC curve: `reports/roc_curve.png`
  - Feature importance plot: `reports/feature_importance.png`

---

## 7. Explainability

- Use **SHAP** or **Permutation Importance** to interpret the best model
- Summarize key features influencing predictions

---

## 8. Checklist Before Training

- [ ] Confirm `data/processed/model_input.csv` exists and is up-to-date
- [ ] Confirm all features and target column are present
- [ ] Confirm class imbalance handling is complete
- [ ] Confirm config.yml matches the latest pipeline and feature groups

---

## 9. Example Workflow (Python/pseudocode)

```python
import pandas as pd
from sklearn.model_selection import StratifiedKFold, GridSearchCV
# ... import all model classes ...

# 1. Load data
df = pd.read_csv('data/processed/model_input.csv')
X = df.drop('anomaly_label', axis=1)
y = df['anomaly_label']

# 2. Define models and parameter grids (see config.yml)
models = {...}
param_grids = {...}

# 3. Cross-validation and grid search
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for name, model in models.items():
    grid = GridSearchCV(model, param_grids[name], scoring='f1', cv=cv, n_jobs=-1)
    grid.fit(X, y)
    # Save best estimator, metrics, etc.
```

---

## 10. References

- See `config.yml` for all model parameters and pipeline details
- See `reports/` for generated outputs

---

**Note:** The Team Leader is responsible only for model training, tuning, evaluation, and reporting. All pre-processing must be completed by other team members before starting this workflow.
