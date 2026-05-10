import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import SelectKBest, mutual_info_classif, RFECV
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from statsmodels.stats.outliers_influence import variance_inflation_factor
from .utils import save_dataframe, save_figure

class FeatureSelector(BaseEstimator, TransformerMixin):
    """
    Feature Selection handling VIF, Correlation filter, Mutual Information, RFE, and feature importance reporting.
    """
    def __init__(self, vif_threshold=10, corr_threshold=0.9, k_best=20, rfe_cv=5,
                 report_dir="reports/feature_selection"):
        self.vif_threshold = vif_threshold
        self.corr_threshold = corr_threshold
        self.k_best = k_best
        self.rfe_cv = rfe_cv
        self.report_dir = report_dir
        self.features_to_drop_ = []
        self.selector_ = None
        self.rfe_ = None
        self.selected_features_ = []
        self.vif_data_ = None
        self.corr_matrix_ = None
        self.mi_scores_ = None
        self.rfe_ranking_ = None
        self.permutation_importance_ = None
        self.shap_importance_ = None
        self.shap_values_ = None

    def _calculate_vif(self, X_df):
        """Calculate VIF and return features to drop."""
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning, message="divide by zero encountered in scalar divide")
            vif_values = []
            for i in range(len(X_df.columns)):
                try:
                    vif = variance_inflation_factor(X_df.values, i)
                except Exception:
                    vif = np.inf
                vif_values.append(vif)

        vif_data = pd.DataFrame({
            "feature": X_df.columns,
            "VIF": vif_values
        })
        self.vif_data_ = vif_data.sort_values("VIF", ascending=False)
        return self.vif_data_[self.vif_data_["VIF"] > self.vif_threshold]["feature"].tolist()

    def _compute_shap_importance(self, model, X_df):
        try:
            if hasattr(model, 'feature_importances_'):
                explainer = shap.TreeExplainer(model)
            else:
                explainer = shap.Explainer(model, X_df)
            shap_values = explainer(X_df)
            self.shap_values_ = shap_values
            
            # Handle multi-class (3D) or binary (2D) SHAP values
            # If 3D (samples, features, classes), average absolute values over classes
            if len(shap_values.values.shape) == 3:
                shap_mean = np.abs(shap_values.values).mean(axis=(0, 2))
            else:
                shap_mean = np.abs(shap_values.values).mean(axis=0)

            shap_df = pd.DataFrame({
                "feature": X_df.columns,
                "shap_mean_abs": shap_mean
            }).sort_values("shap_mean_abs", ascending=False)
            return shap_df
        except Exception as e:
            print(f"SHAP importance computation failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _export_reports(self):
        if self.vif_data_ is not None:
            save_dataframe(self.vif_data_, os.path.join(self.report_dir, "vif_report.csv"))
        if self.corr_matrix_ is not None:
            save_dataframe(self.corr_matrix_, os.path.join(self.report_dir, "correlation_matrix.csv"))
            dropped = pd.DataFrame({"dropped_feature": self.corr_to_drop_})
            save_dataframe(dropped, os.path.join(self.report_dir, "correlation_dropped_features.csv"))
        if self.mi_scores_ is not None:
            save_dataframe(self.mi_scores_, os.path.join(self.report_dir, "mutual_information_scores.csv"))
        if self.rfe_ranking_ is not None:
            save_dataframe(self.rfe_ranking_, os.path.join(self.report_dir, "rfe_ranking.csv"))
        if self.permutation_importance_ is not None:
            save_dataframe(self.permutation_importance_, os.path.join(self.report_dir, "permutation_importance.csv"))
        if self.shap_importance_ is not None:
            save_dataframe(self.shap_importance_, os.path.join(self.report_dir, "shap_importance.csv"))
            try:
                fig = plt.figure(figsize=(10, 8))
                if isinstance(self.shap_values_, shap.Explanation):
                    if len(self.shap_values_.shape) == 3:
                        # Multi-class: slice to positive class if binary (2 classes)
                        if self.shap_values_.shape[2] == 2:
                            shap.summary_plot(self.shap_values_[:, :, 1], show=False)
                        else:
                            shap.summary_plot(self.shap_values_, show=False)
                    else:
                        shap.summary_plot(self.shap_values_, show=False)
                else:
                    # Fallback to the data attribute if available
                    data = getattr(self.shap_values_, 'data', None)
                    shap.summary_plot(self.shap_values_, data, show=False)
                save_figure(fig, os.path.join(self.report_dir, "shap_summary_plot.png"))
            except Exception as e:
                print(f"Failed to export SHAP summary plot: {e}")

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X)
        
        # 1. VIF Filter
        vif_to_drop = self._calculate_vif(X_df)
        X_df = X_df.drop(columns=vif_to_drop)
        self.features_to_drop_.extend(vif_to_drop)

        # 2. Correlation Filter
        self.corr_matrix_ = X_df.corr().abs()
        upper = self.corr_matrix_.where(np.triu(np.ones(self.corr_matrix_.shape), k=1).astype(bool))
        self.corr_to_drop_ = [column for column in upper.columns if any(upper[column] > self.corr_threshold)]
        X_df = X_df.drop(columns=self.corr_to_drop_)
        self.features_to_drop_.extend(self.corr_to_drop_)

        # 3. Mutual Information
        if y is not None:
            X_df = X_df.fillna(0)
            k = min(self.k_best, X_df.shape[1])
            self.selector_ = SelectKBest(score_func=mutual_info_classif, k=k)
            self.selector_.fit(X_df, y)

            mask = self.selector_.get_support()
            selected_by_mi = X_df.columns[mask].tolist()
            self.mi_scores_ = pd.DataFrame({
                "feature": X_df.columns,
                "mutual_info": self.selector_.scores_
            }).sort_values("mutual_info", ascending=False)
            X_mi = X_df[selected_by_mi]

            # 4. RFE on MI selected features
            self.rfe_ = RFECV(
                estimator=RandomForestClassifier(random_state=42),
                step=1,
                cv=self.rfe_cv,
                scoring='f1'
            )
            self.rfe_.fit(X_mi, y)
            rfe_mask = self.rfe_.get_support()
            self.selected_features_ = [selected_by_mi[i] for i in range(len(selected_by_mi)) if rfe_mask[i]]
            self.rfe_ranking_ = pd.DataFrame({
                "feature": selected_by_mi,
                "rank": self.rfe_.ranking_
            }).sort_values("rank")

            # 5. Feature importance reports using the selected feature set
            if self.selected_features_:
                importance_model = RandomForestClassifier(random_state=42)
                importance_model.fit(X_mi[self.selected_features_], y)
                perm = permutation_importance(
                    importance_model,
                    X_mi[self.selected_features_],
                    y,
                    n_repeats=10,
                    random_state=42,
                    scoring='f1',
                    n_jobs=-1
                )
                self.permutation_importance_ = pd.DataFrame({
                    "feature": X_mi[self.selected_features_].columns,
                    "importance_mean": perm.importances_mean,
                    "importance_std": perm.importances_std
                }).sort_values("importance_mean", ascending=False)

                self.shap_importance_ = self._compute_shap_importance(
                    importance_model,
                    X_mi[self.selected_features_]
                )
        else:
            self.selected_features_ = X_df.columns.tolist()

        self._export_reports()
        return self

    def transform(self, X):
        X_df = pd.DataFrame(X).copy()
        cols_to_keep = [c for c in self.selected_features_ if c in X_df.columns]
        return X_df[cols_to_keep]

    def get_feature_names_out(self, input_features=None):
        return np.array(self.selected_features_)

    def save_reports(self, output_dir=None):
        if output_dir:
            self.report_dir = output_dir
        self._export_reports()
        return self.report_dir
