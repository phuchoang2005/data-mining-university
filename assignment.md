Với một nhóm 4 người, bạn có thể chia dự án theo mô hình **Pipeline song song**. Cách tiếp cận tốt nhất là chia theo các "mảng chuyên môn" để tận dụng tối đa các phân tích chúng ta đã làm từ đầu đến giờ.

Dưới đây là sơ đồ phân chia nhiệm vụ (Task Allocation) tối ưu:

---

## 1. Người 1: Data Cleaning & Baseline Preprocessing (Nền tảng)
Người này chịu trách nhiệm "dọn dẹp" dữ liệu thô để các thành viên khác có dữ liệu sạch để làm việc.
* **Xử lý Nhóm C & D:** Thực hiện **Trimming** (xóa bỏ) outliers cho các biến huyết học và nhiễu kỹ thuật.
* **Lọc dữ liệu:** Sử dụng `labeller_confidence_score` để loại bỏ các mẫu nhiễu và xóa cột `anomaly_score` (tránh rò rỉ dữ liệu).
* **Xây dựng Baseline:** Huấn luyện một mô hình đơn giản (ví dụ: Logistic Regression) trên dữ liệu thô để làm mốc so sánh (benchmark).

## 2. Người 2: Feature Engineer & Domain Expert (Nâng cao giá trị)
Người này tập trung vào việc biến đổi các đặc trưng hình thái học (Nhóm A & B).
* **Tạo biến mới:** Tính toán các chỉ số chuyên môn như **N/C Ratio**, **Form Factor**, và quy đổi pixel sang **Micrometer ($\mu m$)**.
* **Dịch chuyển phân phối:** Thực hiện kỹ thuật thêm nhiễu Gaussian và chuẩn hóa màu sắc theo `staining_protocol`.
* **Xử lý Skewness:** Áp dụng **Yeo-Johnson** hoặc **Power Transformation** cho Nhóm A và B.

## 3. Người 3: Statistical Analyst & Optimizer (Tối ưu hóa)
Người này chịu trách nhiệm "tinh lọc" dữ liệu từ Người 1 và Người 2.
* **Clustering (GMM):** Phân cụm các biến đa đỉnh ở Nhóm B để tạo ra biến `cell_subpopulation`.
* **Lựa chọn đặc trưng (Feature Selection):** Chạy VIF để khử đa cộng tuyến, tính Mutual Information và thực hiện **RFE** để chọn ra 12-15 biến tốt nhất.
* **Phân tích tương quan:** Đảm bảo các đặc trưng mới tạo ra không bị trùng lặp thông tin quá mức.

## 4. Người 4: ML Architect & Evaluation (Huấn luyện & Đánh giá)
Người này là người "về đích", kết hợp mọi thứ vào mô hình cuối cùng.
* **Xử lý mất cân bằng:** Áp dụng **SMOTE-Tomek** để cân bằng lớp nhãn.
* **Xây dựng Pipeline:** Kết hợp các bước Scaling (RobustScaler cho Nhóm A, StandardScaler cho Nhóm B) vào `sklearn.pipeline`.
* **Huấn luyện & Tuning:** Chạy song song các mô hình (XGBoost, Random Forest, SVM, MLP) và thực hiện **Hyperparameter Tuning** (GridSearch/Optuna).
* **Đánh giá chuyên sâu:** Vẽ Confusion Matrix, ROC-AUC và phân tích **SHAP** để giải thích mô hình.

---

### Bảng phối hợp công việc (Workflow Timeline)

| Giai đoạn | Người 1 (Cleaner) | Người 2 (Enhancer) | Người 3 (Optimizer) | Người 4 (Architect) |
| :--- | :--- | :--- | :--- | :--- |
| **Tuần 1** | Làm sạch, lọc nhiễu | Tạo NC_Ratio, quy đổi $\mu m$ | Phân cụm GMM | Thiết lập khung Pipeline |
| **Tuần 2** | Scaling cơ bản | Dịch chuyển phân phối | Lọc đặc trưng (RFE) | Huấn luyện Baseline |
| **Tuần 3** | Hỗ trợ chuẩn bị tập Test | Kiểm tra tính ổn định | Giải thích Feature Importance | Tuning & Chốt mô hình |

---

### Các công cụ để team làm việc song song:
1.  **GitHub/GitLab:** Bắt buộc phải có để quản lý code. Mỗi người làm trên một `branch` riêng (ví dụ: `feature-engineering`, `clustering`, `modeling`).
2.  **DVC (Data Version Control):** Nếu dữ liệu lớn, hãy dùng DVC để quản lý các phiên bản dữ liệu sau khi tiền xử lý.
3.  **Weights & Biases (W&B) hoặc MLflow:** Để cả team cùng theo dõi kết quả huấn luyện của các mô hình khác nhau trên một bảng điều khiển chung.

**Lời khuyên:** Người 1 và Người 2 nên bắt đầu sớm nhất. Người 3 và 4 có thể viết sẵn code khung (Skeletal code) bằng dữ liệu mẫu, sau đó cập nhật dữ liệu thật khi Người 1 và 2 hoàn thành.
