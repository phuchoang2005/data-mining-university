## 1. Tại sao phải dùng Clustering cho phân phối đa đỉnh?
Nếu bạn chỉ dùng một giá trị trung bình (mean) cho một biến có 3 đỉnh, giá trị đó thường rơi vào "vùng trũng" – nơi không có dữ liệu thực tế.
* **Mục tiêu:** Biến các "đỉnh" này thành một đặc trưng phân loại mới (Cluster ID).
* **Lợi ích:** Giúp mô hình (như XGBoost) hiểu rằng: "Tế bào này thuộc nhóm Kích thước Lớn, nên tiêu chuẩn về độ tròn của nó phải khác với nhóm Kích thước Nhỏ".

---

## 2. Lựa chọn thuật toán: K-Means vs. GMM

| Thuật toán | Đặc điểm | Khi nào dùng? |
| :--- | :--- | :--- |
| **K-Means** | Phân cụm cứng (Hard clustering), dựa trên khoảng cách Euclide. | Khi các đỉnh tách biệt rõ ràng và có dạng hình cầu. |
| **GMM (Gaussian Mixture Models)** | Phân cụm mềm (Soft clustering), dựa trên xác suất và phân phối Gauss. | **Khuyên dùng cho dữ liệu này.** GMM cực mạnh trong việc tách các phân phối đa đỉnh bị chồng lấp một phần. |

---

## 3. Quy trình thực hiện (Step-by-Step)

### Bước 1: Chọn biến để phân cụm (Feature Selection)
Đừng dùng tất cả 36 biến. Chỉ chọn những biến thể hiện đa đỉnh rõ rệt nhất trong EDA:
* `cell_diameter_um`
* `nucleus_area_pct`
* `chromatin_density`
* `cell_area_px`
* `cytoplasm_ratio`
* `granularity_score`

### Bước 2: Tìm số lượng cụm tối ưu ($K$)
Bạn cần xác định xem có bao nhiêu "đỉnh" thực sự.
* Sử dụng **Elbow Method** (Phương pháp khuỷu tay) hoặc **Silhouette Score**.
* Thông thường với tế bào máu, $K$ thường rơi vào khoảng **3 đến 5** (tương ứng với các dòng tế bào chính). Hiện tại pipeline sử dụng **$K = 4$**.

### Bước 3: Huấn luyện và Gán nhãn cụm
Sử dụng GMM để tính toán xác suất tế bào thuộc về một cụm.

```python
from sklearn.mixture import GaussianMixture
import pandas as pd

# 1. Chọn các biến đa đỉnh đã được scaling
features_for_clustering = [
    'cell_diameter_um', 'nucleus_area_pct', 'chromatin_density',
    'cell_area_px', 'cytoplasm_ratio', 'granularity_score'
]
X_clust = df[features_for_clustering]

# 2. Khởi tạo GMM (4 cụm dựa trên kết quả Elbow Method)
gmm = GaussianMixture(n_components=4, random_state=42)
df['cell_subpopulation'] = gmm.fit_predict(X_clust)

# 3. Xem kết quả phân cụm có khớp với nhãn anomaly không
print(pd.crosstab(df['cell_subpopulation'], df['anomaly_label']))
```

---

## 4. Cách sử dụng kết quả Clustering để nâng cao Model

Sau khi có cột `cell_subpopulation`, bạn có hai cách để nâng cấp tiền xử lý:

### Cách A: Feature Augmentation (Thêm đặc trưng)
Coi nhãn cụm là một biến hạng mục (Categorical feature).
* Thực hiện **One-Hot Encoding** cho cột `cell_subpopulation`.
* Mô hình bây giờ sẽ có thêm thông tin ngữ cảnh về loại tế bào.

### Cách B: Cluster-specific Scaling (Chuẩn hóa theo cụm)
Đây là kỹ thuật rất mạnh: Thay vì chuẩn hóa toàn bộ tập dữ liệu, bạn chuẩn hóa các biến Nhóm B **theo từng cụm**.
* **Lý do:** Một tế bào nhân to trong nhóm "Tế bào nhỏ" là bất thường, nhưng nhân to trong nhóm "Tế bào lớn" có thể là bình thường.
* **Cách làm:** Trừ đi giá trị trung bình của cụm đó thay vì trung bình của toàn bộ dữ liệu.

---

## 5. Lưu ý quan trọng
* **Tránh rò rỉ dữ liệu (Data Leakage):** Khi huấn luyện Clustering, tuyệt đối **không đưa biến `anomaly_label` vào**. Clustering phải hoàn toàn khách quan dựa trên đặc điểm hình thái.
* **Xử lý Outliers trước:** Bạn nên xử lý các giá trị quá cực đoan (Nhóm C) trước khi chạy Clustering, vì K-Means và GMM rất nhạy cảm với outliers, chúng có thể tạo ra một cụm riêng chỉ chứa 1-2 điểm nhiễu.

**Kết luận:** Bằng cách thêm bước Clustering này, bạn đang chuyển đổi bài toán từ "Phân loại mù" sang "Phân loại có ngữ cảnh dòng tế bào". Điều này đặc biệt hiệu quả nếu bạn định sử dụng **Random Forest**.

Bạn có muốn tôi giúp viết một đoạn code hoàn chỉnh tích hợp cả **Feature Engineering (N/C Ratio)** và **Clustering (GMM)** vào một Pipeline duy nhất không?