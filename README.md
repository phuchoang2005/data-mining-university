# 🩸 Blood Cell Classification Project (Binary Classification)

## 📌 Project Overview

This project focuses on building a robust Machine Learning model to classify blood cells into two categories: **Normal** and **Abnormal**. The dataset consists of cellular morphological features, hematological indices, and medical metadata.

- **Objective:** Optimize the F1-Score for detecting abnormal cells.
- **Dataset:** 5,880 samples, 36 attributes (Numerical & Categorical).
- **Methodology:** An advanced preprocessing pipeline integrated with biological domain knowledge.

---

## 👥 Team Structure & Roles

The project is implemented by a 4-member team using a parallel pipeline model:

1.  **Data Sanitizer (Member 1):** Data cleaning, label noise removal, and handling technical outliers (Group C).
2.  **Feature Engineer (Member 2):** Physical unit conversion ($\mu m$), engineering new features (NC Ratio, Form Factor), and skewness correction.
3.  **Advanced Statistician (Member 3):** GMM Clustering, Grouped Z-scores, Feature Selection (RFE), and Class Balancing (SMOTE-Tomek).
4.  **Team Lead / ML Architect:** End-to-end Pipeline construction, multi-model training (XGBoost, Random Forest...), hyperparameter tuning, and SHAP evaluation.

---

## 🛠 Feature Processing Strategy (Feature Groups)

Features are categorized into four strategic groups, each receiving specialized treatment:

- **Group A (Pathology Signals):** Critical pathology indicators (`lobularity`, `eccentricity`...). Processed with **RobustScaler** and **Capping** to preserve vital biological outlier signals.
- **Group B (Morphology):** Size and membrane features. Converted to physical units and normalized within specific cell populations (**Grouped Z-score**).
- **Group C (Hematology/Noise):** General hematological indices. Filtered for noise using the **IQR (Interquartile Range)** method.
- **Group D (Governance):** Metadata and confidence scores. Used for sample quality filtering and preventing **Data Leakage** (e.g., removing `anomaly_score`).

---

## 🚀 Advanced Techniques

- **N/C Ratio:** Calculation of the Nucleus-to-Cytoplasm area ratio—the "gold standard" in hematology.
- **GMM Clustering:** Automated detection of hidden subpopulations within multi-modal distributions.
- **Feature Crossing:** Interaction features between `cell_type` and `staining_protocol`.
- **SMOTE-Tomek:** Simultaneous data balancing and decision boundary cleaning.

---

## 📁 Project Structure

```text
.
├── ./config.yml # Assignment
├── ./data # saved pre-processed dataset
│   ├── ./data/intermidiate
│   ├── ./data/processed
│   └── ./data/raw
├── ./docs # Instruction pre-processing
│   ├── ./docs/categorical-processing.md
│   ├── ./docs/category
│   │   ├── ./docs/category/detail_Categorical&Numberical.md
│   │   └── ./docs/category/detail_CrossFeatureInteration.md
│   ├── ./docs/numeric
│   │   ├── ./docs/numeric/advanced-numeric-processing.md
│   │   ├── ./docs/numeric/detail_1.md
│   │   ├── ./docs/numeric/detail_2.md
│   │   ├── ./docs/numeric/detail_3.md
│   │   ├── ./docs/numeric/detail_5.md
│   │   ├── ./docs/numeric/NhomA.png
│   │   ├── ./docs/numeric/NhomB.png
│   │   ├── ./docs/numeric/NhomC.png
│   │   └── ./docs/numeric/NhomD.png
│   ├── ./docs/numeric-processing.md
│   └── ./docs/visualize # EDA dataset
│       ├── ./docs/visualize/KTDL_DoAn_TienXuLy_01.ipynb
│       └── ./docs/visualize/visualizeByGroup.ipynb
├── ./models
│   └── ./models/saved
├── ./README.md
├── ./reports # Validation, Evaluation, Metric, Confusion Matrix,...
├── ./requirement.txt #dependencies
```

---

## 💻 Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/phuchoang2005/data-mining-university.git
   ```
2. **Set up the virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or .\venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. **Configure parameters** in `config.yml` and execute the pipeline scripts.

---

## 📊 Expected Deliverables

The final model provides high **Explainability** via **SHAP values**, allowing medical experts to understand exactly why a specific cell was flagged as abnormal based on its morphological structure.
