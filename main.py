import os
import time
import shutil
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from src.config import load_config
from src.data_loader import download_and_load_data
from src.pipeline import build_full_pipeline
from src.training import get_models, get_param_grids, train_and_tune, save_model
from src.evaluation import evaluate_model, save_metrics, plot_confusion_matrix, plot_roc_curve, plot_shap_summary, plot_permutation_importance, plot_feature_importance


def generate_training_report(all_results, filepath):
    """Generate training report in Markdown."""
    report = "# Training Report\n\n"
    report += "## Model Training Summary\n\n"
    report += "| Model | Training Time (s) | Best Parameters |\n"
    report += "|-------|-------------------|----------------|\n"
    for model, metrics in all_results.items():
        if "error" not in metrics:
            time = metrics.get("training_time_seconds", "N/A")
            params = metrics.get("best_params", "N/A")
            report += f"| {model} | {time} | {params} |\n"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(report)

def generate_evaluation_report(all_results, best_model, filepath):
    """Generate evaluation report in Markdown."""
    report = "# Evaluation Report\n\n"
    report += f"## Best Model: {best_model}\n\n"
    report += "## Model Performance Comparison\n\n"
    report += "| Model | Accuracy | Precision | Recall | F1 Score | ROC AUC |\n"
    report += "|-------|----------|-----------|--------|----------|---------|\n"
    for model, metrics in all_results.items():
        if "error" not in metrics:
            acc = metrics.get("accuracy", "N/A")
            prec = metrics.get("precision", "N/A")
            rec = metrics.get("recall", "N/A")
            f1 = metrics.get("f1_score", "N/A")
            auc = metrics.get("roc_auc", "N/A")
            report += f"| {model} | {acc} | {prec} | {rec} | {f1} | {auc} |\n"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(report)


def main():
    print("Loading configuration...")
    config = load_config("config.yml")

    # 1. Download and load data
    df = download_and_load_data(config)

    target_col = config['data']['input']['target_column']
    if target_col not in df.columns:
        print(f"Target column '{target_col}' not found. Using the last column as target.")
        target_col = df.columns[-1]

    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Stratified Split
    print("Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=config['data']['output']['train_test_split']['test_size'],
        stratify=y,
        random_state=config['data']['output']['train_test_split']['random_state']
    )

    models = get_models(config)
    param_grids = get_param_grids(config)

    all_results = {}

    # Train and evaluate ALL 6 models
    for model_name, classifier in models.items():
        print(f"\n{'='*60}")
        print(f"--- Training {model_name} ---")
        print(f"{'='*60}")

        param_grid = param_grids.get(model_name, {})

        try:
            # Build fresh pipeline for each model
            full_pipeline = build_full_pipeline(classifier, config)

            # Train and tune
            start_time = time.time()
            grid_search = train_and_tune(full_pipeline, X_train, y_train, param_grid, config)
            training_time = time.time() - start_time

            best_pipeline = grid_search.best_estimator_
            print(f"Best parameters: {grid_search.best_params_}")
            print(f"Training time: {training_time:.2f}s")

            # Evaluate on test set
            metrics, y_pred, y_prob = evaluate_model(best_pipeline, X_test, y_test)
            metrics["training_time_seconds"] = round(training_time, 2)
            metrics["best_params"] = str(grid_search.best_params_)

            print(f"Metrics: {metrics}")
            all_results[model_name] = metrics

            # Save model
            model_path = os.path.join(
                config['output']['leader']['saved_models'],
                f"{model_name.replace(' ', '_')}.pkl"
            )
            save_model(best_pipeline, model_path)

            # Save plots for each model
            plot_confusion_matrix(
                y_test, y_pred,
                f"reports/{model_name.replace(' ', '_')}_confusion_matrix.png"
            )
            if y_prob is not None:
                plot_roc_curve(
                    y_test, y_prob,
                    f"reports/{model_name.replace(' ', '_')}_roc_curve.png"
                )

            # SHAP Summary Plot
            plot_shap_summary(
                best_pipeline, X_test,
                f"reports/{model_name.replace(' ', '_')}_shap_summary.png"
            )

            # Permutation Importance
            plot_permutation_importance(
                best_pipeline, X_test, y_test,
                f"reports/{model_name.replace(' ', '_')}_permutation_importance.png"
            )

        except Exception as e:
            print(f"ERROR training {model_name}: {e}")
            all_results[model_name] = {"error": str(e)}

    # --- Summary comparison table ---
    print(f"\n{'='*80}")
    print("MODEL COMPARISON SUMMARY")
    print(f"{'='*80}")

    results_df = pd.DataFrame(all_results).T
    # Export and report the summary in JSON format
    json_summary = results_df.to_json(orient="index", indent=4)
    print(json_summary)
    
    summary_report_path = "reports/model_comparison_summary.json"
    os.makedirs(os.path.dirname(summary_report_path), exist_ok=True)
    with open(summary_report_path, "w") as f:
        f.write(json_summary)
    print(f"\nExported model comparison summary to {summary_report_path}")

    # Save comparison
    save_metrics(all_results, config['output']['leader']['model_metrics'])

    # Find best model by F1, then ROC-AUC
    valid_results = {k: v for k, v in all_results.items() if "error" not in v}
    if valid_results:
        # Sort by f1_score desc, then roc_auc desc
        best_name = max(valid_results, key=lambda k: (valid_results[k].get("f1_score", 0), valid_results[k].get("roc_auc", 0)))
        print(f"\nBest model: {best_name} (F1={valid_results[best_name]['f1_score']:.4f}, ROC-AUC={valid_results[best_name].get('roc_auc', 'N/A')})")

        # Save best model
        best_model_path = os.path.join(
            config['output']['leader']['saved_models'],
            f"{best_name.replace(' ', '_')}.pkl"
        )
        best_output_path = config['output']['leader']['best_model']
        shutil.copy(best_model_path, best_output_path)
        print(f"Best model saved to {best_output_path}")

        # Feature importance for best model (if tree-based)
        if hasattr(joblib.load(best_model_path).named_steps['classifier'], 'feature_importances_'):
            plot_feature_importance(best_model_path, X_test, f"reports/feature_importance.png")

        # Generate reports
        generate_training_report(all_results, config['output']['leader']['training_report'])
        generate_evaluation_report(all_results, best_name, config['output']['leader']['evaluation_report'])

    print("\nPipeline execution completed successfully!")


if __name__ == "__main__":
    main()
