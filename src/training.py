import os
import json
import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import GridSearchCV

def get_models(config=None):
    """
    Returns a dictionary of un-fitted models defined in the config.
    """
    models = {
        "Decision Tree": DecisionTreeClassifier(random_state=42, class_weight='balanced'),
        "Naive Bayes": GaussianNB(),
        "K-Nearest Neighbors": KNeighborsClassifier(),
        "Logistic Regression": LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000),
        "Random Forest": RandomForestClassifier(random_state=42, class_weight='balanced'),
        "XGBoost": XGBClassifier(random_state=42, use_label_encoder=False, eval_metric="logloss"),
        "SVM": SVC(probability=True, random_state=42, class_weight='balanced'),
        "MLP": MLPClassifier(random_state=42, max_iter=500)
    }
    return models

def get_param_grids(config=None):
    """
    Returns parameter grids for GridSearchCV.
    """
    param_grids = {
        "Decision Tree": {'classifier__max_depth': [5, 10], 'classifier__min_samples_split': [2, 5]},
        "Naive Bayes": {'classifier__var_smoothing': [1e-9, 1e-8]},
        "K-Nearest Neighbors": {'classifier__n_neighbors': [3, 5], 'classifier__weights': ['uniform', 'distance']},
        "Logistic Regression": {'classifier__C': [0.1, 1, 10]},
        "Random Forest": {'classifier__n_estimators': [50, 100], 'classifier__max_depth': [5, 10]},
        "XGBoost": {'classifier__n_estimators': [50, 100], 'classifier__learning_rate': [0.01, 0.1]},
        "SVM": {'classifier__C': [0.1, 1], 'classifier__kernel': ['rbf']},
        "MLP": {'classifier__hidden_layer_sizes': [(64, 32), (128, 64)], 'classifier__alpha': [0.001]}
    }
    return param_grids

def train_and_tune(pipeline, X_train, y_train, param_grid, cv=5, scoring='f1'):
    """
    Perform Grid Search with the given pipeline and parameter grid.
    """
    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=cv,
        scoring=scoring,
        n_jobs=-1,
        verbose=1
    )
    grid_search.fit(X_train, y_train)
    return grid_search

def save_model(model, filepath):
    """Save the trained model to disk."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(model, filepath)
    print(f"Model saved to {filepath}")
