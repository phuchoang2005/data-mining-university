import os
import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier


from sklearn.model_selection import GridSearchCV


# ── Model name → sklearn class mapping ──────────────────────────────────────
MODEL_CLASS_MAP = {
    "Decision Tree": DecisionTreeClassifier,
    "Naive Bayes": GaussianNB,
    "K-Nearest Neighbors": KNeighborsClassifier,
    "Logistic Regression": LogisticRegression,
    "Random Forest": RandomForestClassifier,
    "XGBoost": XGBClassifier,


}

# Params in config that are metadata, NOT constructor arguments
_META_PARAMS = {"variant"}




def _coerce_value(v):
    """
    Fix YAML parsing edge cases:
    - String 'None' → Python None
    - String scientific notation '1e-9' → float
    """
    if isinstance(v, str):
        if v == "None":
            return None
        # Try parsing as number (handles '1e-9', '0.01', etc.)
        try:
            return float(v)
        except ValueError:
            pass
    return v


def _prepare_params(name, params):
    """
    Convert config params dict into constructor kwargs.
    Handles special type conversions (e.g., list→tuple for hidden_layer_sizes)
    and compatibility fixes (e.g., saga solver for Logistic Regression).
    """
    clean = {k: _coerce_value(v) for k, v in params.items() if k not in _META_PARAMS}





    # Logistic Regression: 'lbfgs' does not support l1 penalty.
    # Use 'saga' so GridSearchCV can search both l1 and l2 without errors.
    if name == "Logistic Regression" and clean.get("solver") == "lbfgs":
        clean["solver"] = "saga"

    return clean


def _prepare_hyperparams(name, hyperparams):
    """
    Convert config hyperparams dict into a GridSearchCV param_grid.
    - Prefixes every key with 'classifier__' (for Pipeline compatibility).
    - Converts nested lists to tuples where needed (hidden_layer_sizes).
    - Coerces values to correct Python types (None, float).
    """
    grid = {}
    for key, values in hyperparams.items():
        prefixed = f"classifier__{key}"

        # Coerce each value in the list
        values = [_coerce_value(v) for v in values]





        grid[prefixed] = values
    return grid


# ── Public API ───────────────────────────────────────────────────────────────

def get_models(config):
    """
    Build model instances dynamically from config['model_training']['models'].
    Each model's constructor params are read from its 'params' dict in config.yml.
    """
    models = {}
    for model_cfg in config["model_training"]["models"]:
        name = model_cfg["name"]
        cls = MODEL_CLASS_MAP.get(name)
        if cls is None:
            print(f"Warning: Unknown model '{name}' in config, skipping.")
            continue

        raw_params = model_cfg.get("params", {})
        constructor_kwargs = _prepare_params(name, raw_params)
        models[name] = cls(**constructor_kwargs)

    return models


def get_param_grids(config):
    """
    Build GridSearchCV param grids dynamically from config['model_training']['models'].
    Each model's search space is read from its 'hyperparams' dict in config.yml.
    """
    grids = {}
    for model_cfg in config["model_training"]["models"]:
        name = model_cfg["name"]
        hyperparams = model_cfg.get("hyperparams", {})
        grids[name] = _prepare_hyperparams(name, hyperparams)

    return grids


def train_and_tune(pipeline, X_train, y_train, param_grid, config):
    """
    Perform GridSearchCV using settings from config['model_training']['hyperparameter_tuning'].
    Reads cv_folds, scoring, and n_jobs from config.yml.
    """
    tuning_cfg = config["model_training"]["hyperparameter_tuning"]

    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=tuning_cfg.get("cv_folds", 5),
        scoring=tuning_cfg.get("scoring", "f1"),
        n_jobs=tuning_cfg.get("n_jobs", -1),
        verbose=1,
        error_score="raise",
    )
    grid_search.fit(X_train, y_train)
    return grid_search


def save_model(model, filepath):
    """Save the trained model to disk."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(model, filepath)
    print(f"Model saved to {filepath}")
