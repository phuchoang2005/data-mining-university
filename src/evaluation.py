import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, roc_curve
)
import shap
from sklearn.inspection import permutation_importance
import joblib
import pandas as pd
from .utils import save_figure, save_json

def evaluate_model(model, X_test, y_test):
    """
    Evaluate the trained model and return metrics.
    """
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0),
    }
    
    if y_prob is not None:
        try:
            metrics["roc_auc"] = roc_auc_score(y_test, y_prob)
        except ValueError:
            metrics["roc_auc"] = None
            
    return metrics, y_pred, y_prob

def plot_confusion_matrix(y_test, y_pred, filepath):
    """Plot and save confusion matrix."""
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    save_figure(plt.gcf(), filepath)

def plot_roc_curve(y_test, y_prob, filepath):
    """Plot and save ROC curve."""
    if y_prob is None:
        return
        
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)
    
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    
    save_figure(plt.gcf(), filepath)

def save_metrics(metrics, filepath):
    """Save metrics to JSON."""
    save_json(metrics, filepath)

def plot_shap_summary(model, X_test, filepath):
    """Plot SHAP summary plot."""
    try:
        # If it's a pipeline, extract the classifier and transform X_test
        classifier = model
        X_transformed = X_test
        
        if hasattr(model, 'named_steps'):
            classifier = model.named_steps['classifier']
            # Transform X_test using all transformer steps before the classifier
            X_transformed = X_test
            for name, step in model.steps:
                if name == 'classifier':
                    break
                # Only apply steps that have a transform method (skip samplers)
                if hasattr(step, 'transform'):
                    X_transformed = step.transform(X_transformed)
            
            # Ensure it's a DataFrame for SHAP consistency
            if not isinstance(X_transformed, pd.DataFrame):
                # Try to get feature names from the last transformer that has them
                feature_names = None
                for name, step in reversed(model.steps):
                    if name == 'classifier': continue
                    if hasattr(step, 'get_feature_names_out'):
                        try:
                            feature_names = step.get_feature_names_out()
                            break
                        except:
                            continue
                X_transformed = pd.DataFrame(X_transformed, columns=feature_names)
        
        if hasattr(classifier, 'feature_importances_'):  # Tree-based
            explainer = shap.TreeExplainer(classifier)
        else:
            explainer = shap.Explainer(classifier, X_transformed)
            
        shap_values = explainer(X_transformed)
        
        plt.figure(figsize=(10, 8))
        if isinstance(shap_values, shap.Explanation):
            if len(shap_values.shape) == 3:
                # Multi-class: slice to positive class if binary (2 classes), else plot bar
                if shap_values.shape[2] == 2:
                    shap.summary_plot(shap_values[:, :, 1], show=False)
                else:
                    shap.summary_plot(shap_values, show=False)
            else:
                shap.summary_plot(shap_values, show=False)
        else:
            # Old format (list of arrays)
            if isinstance(shap_values, list) and len(shap_values) == 2:
                shap.summary_plot(shap_values[1], X_transformed, show=False)
            else:
                shap.summary_plot(shap_values, X_transformed, show=False)
                
        save_figure(plt.gcf(), filepath)
    except Exception as e:
        print(f"SHAP summary plot failed: {e}")

def plot_permutation_importance(model, X_test, y_test, filepath):
    """Plot permutation importance."""
    try:
        perm_importance = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42, scoring='f1')
        sorted_idx = perm_importance.importances_mean.argsort()
        plt.figure(figsize=(10, 6))
        plt.barh(range(len(sorted_idx)), perm_importance.importances_mean[sorted_idx])
        plt.yticks(range(len(sorted_idx)), X_test.columns[sorted_idx])
        plt.xlabel("Permutation Importance")
        plt.title("Permutation Importance (F1 Score)")
        save_figure(plt.gcf(), filepath)
    except Exception as e:
        print(f"Permutation importance plot failed: {e}")

def plot_feature_importance(model_path, X_test, filepath):
    """Plot feature importance for tree-based models."""
    try:
        model = joblib.load(model_path)
        classifier = model.named_steps['classifier']
        if hasattr(classifier, 'feature_importances_'):
            importances = classifier.feature_importances_
            indices = importances.argsort()[::-1]
            plt.figure(figsize=(10, 6))
            plt.barh(range(len(indices)), importances[indices])
            plt.yticks(range(len(indices)), X_test.columns[indices])
            plt.xlabel("Feature Importance")
            plt.title("Feature Importance")
            save_figure(plt.gcf(), filepath)
    except Exception as e:
        print(f"Feature importance plot failed: {e}")
