# Guide to Clean Modular Programming for Scikit-Learn Pipelines

This guide will help your team write clean, modular, and maintainable code for building a full machine learning pipeline in Python using Scikit-Learn, based on your config.yml. It is designed for teams new to modular programming.

---

## 1. Why Modular Programming?

- **Separation of concerns:** Each file/function/class does one thing well.
- **Reusability:** Functions and classes can be reused in different projects or pipeline steps.
- **Collaboration:** Team members can work on different modules without conflicts.
- **Testing:** Easier to test and debug small, focused modules.

---

## 2. Recommended Project Structure

```text
project_root/
│
├── data/                  # Raw and processed data
├── models/                # Saved models
├── reports/               # Evaluation reports and plots
├── config.yml             # Your pipeline configuration
├── main.py                # Entry point to run the pipeline
├── requirements.txt       # Python dependencies
├── docs/                  # Documentation
│   └── modular_programming.md
└── src/                   # All source code modules
    ├── __init__.py
    ├── config.py          # Load and parse config.yml
    ├── data_loader.py     # Data loading and validation
    ├── preprocessing/     # Preprocessing steps
    │   ├── __init__.py
    │   ├── numeric.py     # Numeric feature processing
    │   ├── categorical.py # Categorical feature processing
    │   ├── feature_eng.py # Feature engineering
    │   ├── clustering.py  # Clustering for multi-modality
    │   └── augmentation.py# Data augmentation
    ├── selection.py       # Feature selection
    ├── imbalance.py       # Class imbalance handling
    ├── training.py        # Model training and tuning
    ├── evaluation.py      # Model evaluation and reporting
    └── utils.py           # Utility functions
```

---

## 3. How to Write Modular Code

### a. One Function = One Responsibility

- Each function should do one thing (e.g., `def cap_outliers(df, features, method, percentiles): ...`).
- Avoid long functions that mix multiple steps.

### b. Use Classes for Pipeline Steps

- For complex steps (e.g., custom transformers), use classes that inherit from `BaseEstimator` and `TransformerMixin`.
- Example:

```python
from sklearn.base import BaseEstimator, TransformerMixin

class OutlierCapper(BaseEstimator, TransformerMixin):
    def __init__(self, features, method='winsorization', percentiles=(1, 99)):
        ...
    def fit(self, X, y=None):
        ...
    def transform(self, X):
        ...
```

### c. Use Scikit-Learn Pipelines

- Chain steps using `Pipeline` and `ColumnTransformer`.
- Example:

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

numeric_pipeline = Pipeline([
    ('cap', OutlierCapper(...)),
    ('scale', RobustScaler()),
])

full_pipeline = ColumnTransformer([
    ('num', numeric_pipeline, numeric_features),
    ('cat', categorical_pipeline, categorical_features),
])
```

### d. Configuration-Driven Code

- Read parameters (features, thresholds, model settings) from `config.yml` using a loader (e.g., `pyyaml`).
- Avoid hardcoding feature names or parameters in your code.

### e. Keep Each Module Small

- Each file in `src/` should be <200 lines if possible.
- Split large logic into submodules (e.g., `preprocessing/` folder).

### f. Use Docstrings and Type Hints

- Every function/class should have a docstring explaining its purpose and arguments.
- Use type hints for clarity.

---

## 4. Example: Numeric Preprocessing Module (src/preprocessing/numeric.py)

```python
"""
Numeric feature processing: outlier capping, transformation, scaling
"""
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import RobustScaler, PowerTransformer

class NumericPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, config):
        self.config = config
    def fit(self, X, y=None):
        # Fit scalers/transformers as needed
        ...
    def transform(self, X):
        # Apply capping, transformation, scaling
        ...
```

---

## 5. Collaboration Tips

- **Agree on interfaces:** Document what each function/class expects and returns.
- **Write tests:** Use `pytest` or similar to test each module.
- **Use version control:** Commit often, use branches for features.
- **Document everything:** Keep `README.md` and module docstrings up to date.

---

## 6. Final Pipeline Assembly (main.py)

- Import all modules and assemble the pipeline using Scikit-Learn's `Pipeline` and `ColumnTransformer`.
- Load config, run each step, and save outputs as specified in `config.yml`.

---

## 7. References

- [Scikit-Learn Pipeline Documentation](https://scikit-learn.org/stable/modules/compose.html)
- [Scikit-Learn Custom Transformers](https://scikit-learn.org/stable/developers/develop.html)
- [PyYAML for config loading](https://pyyaml.org/wiki/PyYAMLDocumentation)

---

**By following this structure, your team will be able to work in parallel, keep code clean, and easily assemble a robust, reproducible pipeline.**
