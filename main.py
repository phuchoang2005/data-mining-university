import os
import time
import pandas as pd
from sklearn.model_selection import train_test_split
from src.config import load_config
from src.data_loader import download_and_load_data
from src.pipeline import build_full_pipeline
from src.training import get_models, get_param_grids, train_and_tune, save_model
from src.evaluation import evaluate_model, save_metrics, plot_confusion_matrix, plot_roc_curve


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

    # Train and evaluate ALL 8 models
    for model_name, classifier in models.items():
        print(f"\n{'='*60}")
        print(f"--- Training {model_name} ---")
        print(f"{'='*60}")

        param_grid = param_grids.get(model_name, {})

        try:
            # Build fresh pipeline for each model
            full_pipeline = build_full_pipeline(classifier)

            # Train and tune
            start_time = time.time()
            grid_search = train_and_tune(full_pipeline, X_train, y_train, param_grid, cv=3)
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

        except Exception as e:
            print(f"ERROR training {model_name}: {e}")
            all_results[model_name] = {"error": str(e)}

    # --- Summary comparison table ---
    print(f"\n{'='*80}")
    print("MODEL COMPARISON SUMMARY")
    print(f"{'='*80}")

    results_df = pd.DataFrame(all_results).T
    print(results_df.to_string())

    # Save comparison
    save_metrics(all_results, config['output']['leader']['model_metrics'])

    # Find best model by F1
    valid_results = {k: v for k, v in all_results.items() if "error" not in v}
    if valid_results:
        best_name = max(valid_results, key=lambda k: valid_results[k].get("f1_score", 0))
        print(f"\nBest model by F1: {best_name} (F1={valid_results[best_name]['f1_score']:.4f})")

    print("\nPipeline execution completed successfully!")


if __name__ == "__main__":
    main()
