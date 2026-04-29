import os
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
    Returns a dictionary of un-fitted models with default params from config.yml.
    Config: model_training.models[].params
    """
    models = {
        # 1. Decision Tree (config: criterion=gini, max_depth=10, etc.)
        "Decision Tree": DecisionTreeClassifier(
            criterion='gini', max_depth=10, min_samples_split=5,
            min_samples_leaf=2, class_weight='balanced', random_state=42
        ),
        # 2. Naive Bayes (config: variant=GaussianNB)
        "Naive Bayes": GaussianNB(),
        # 3. KNN (config: n_neighbors=5, weights=distance, metric=minkowski, p=2)
        "K-Nearest Neighbors": KNeighborsClassifier(
            n_neighbors=5, weights='distance', metric='minkowski', p=2
        ),
        # 4. Logistic Regression (config: penalty=l2, C=1.0, solver=lbfgs, max_iter=1000)
        # Note: solver='saga' used instead of 'lbfgs' to support both l1 and l2 penalties
        # in GridSearchCV (lbfgs does not support l1 penalty)
        "Logistic Regression": LogisticRegression(
            penalty='l2', C=1.0, solver='saga', max_iter=1000,
            class_weight='balanced', random_state=42
        ),
        # 5. Random Forest (config: n_estimators=100, max_depth=10, etc.)
        "Random Forest": RandomForestClassifier(
            n_estimators=100, max_depth=10, min_samples_split=5,
            min_samples_leaf=2, class_weight='balanced', random_state=42
        ),
        # 6. XGBoost (config: scale_pos_weight=3 for class imbalance, etc.)
        "XGBoost": XGBClassifier(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8, scale_pos_weight=3,
            random_state=42, use_label_encoder=False, eval_metric='logloss'
        ),
        # 7. SVM (config: kernel=rbf, C=1.0, gamma=scale, class_weight=balanced)
        "SVM": SVC(
            kernel='rbf', C=1.0, gamma='scale',
            class_weight='balanced', probability=True, random_state=42
        ),
        # 8. MLP (config: early_stopping=true, learning_rate=adaptive, etc.)
        "MLP": MLPClassifier(
            hidden_layer_sizes=(64, 32), activation='relu', solver='adam',
            alpha=0.001, batch_size='auto', learning_rate='adaptive',
            learning_rate_init=0.001, max_iter=500, early_stopping=True,
            validation_fraction=0.1, random_state=42
        ),
    }
    return models


def get_param_grids(config=None):
    """
    Returns parameter grids for GridSearchCV matching config.yml model_training.models[].hyperparams.
    All values match config exactly.
    """
    param_grids = {
        # Config: max_depth [5,10,15,None], min_samples_split [2,5,10]
        "Decision Tree": {
            'classifier__max_depth': [5, 10, 15, None],
            'classifier__min_samples_split': [2, 5, 10],
        },
        # Config: var_smoothing [1e-9, 1e-8, 1e-7, 1e-6]
        "Naive Bayes": {
            'classifier__var_smoothing': [1e-9, 1e-8, 1e-7, 1e-6],
        },
        # Config: n_neighbors [3,5,7,9,11], weights [uniform,distance], metric [euclidean,manhattan,minkowski]
        "K-Nearest Neighbors": {
            'classifier__n_neighbors': [3, 5, 7, 9, 11],
            'classifier__weights': ['uniform', 'distance'],
            'classifier__metric': ['euclidean', 'manhattan', 'minkowski'],
        },
        # Config: C [0.01,0.1,1,10,100], penalty [l1,l2]
        "Logistic Regression": {
            'classifier__C': [0.01, 0.1, 1, 10, 100],
            'classifier__penalty': ['l1', 'l2'],
        },
        # Config: n_estimators [50,100,200], max_depth [5,10,15,None], min_samples_split [2,5,10]
        "Random Forest": {
            'classifier__n_estimators': [50, 100, 200],
            'classifier__max_depth': [5, 10, 15, None],
            'classifier__min_samples_split': [2, 5, 10],
        },
        # Config: n_estimators [50,100,200], max_depth [3,6,9], learning_rate [0.01,0.1,0.2], subsample [0.7,0.8,0.9]
        "XGBoost": {
            'classifier__n_estimators': [50, 100, 200],
            'classifier__max_depth': [3, 6, 9],
            'classifier__learning_rate': [0.01, 0.1, 0.2],
            'classifier__subsample': [0.7, 0.8, 0.9],
        },
        # Config: C [0.1,1,10,100], kernel [rbf,linear,poly], gamma [scale,auto,0.1,0.01]
        "SVM": {
            'classifier__C': [0.1, 1, 10, 100],
            'classifier__kernel': ['rbf', 'linear', 'poly'],
            'classifier__gamma': ['scale', 'auto', 0.1, 0.01],
        },
        # Config: hidden_layer_sizes [[64,32],[128,64],[64,32,16]], activation [relu,tanh], solver [adam,sgd], alpha [0.0001,0.001,0.01]
        "MLP": {
            'classifier__hidden_layer_sizes': [(64, 32), (128, 64), (64, 32, 16)],
            'classifier__activation': ['relu', 'tanh'],
            'classifier__solver': ['adam', 'sgd'],
            'classifier__alpha': [0.0001, 0.001, 0.01],
        },
    }
    return param_grids


def train_and_tune(pipeline, X_train, y_train, param_grid, cv=5, scoring='f1'):
    """
    Perform Grid Search with the given pipeline and parameter grid.
    Config: hyperparameter_tuning (method=grid_search, scoring=f1, n_jobs=-1)
    """
    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=cv,
        scoring=scoring,
        n_jobs=-1,
        verbose=1,
        error_score='raise'
    )
    grid_search.fit(X_train, y_train)
    return grid_search


def save_model(model, filepath):
    """Save the trained model to disk."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(model, filepath)
    print(f"Model saved to {filepath}")
