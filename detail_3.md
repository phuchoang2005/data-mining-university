## 1. Lọc theo độ tương quan và Đa cộng tuyến (Multicollinearity)
Trong dữ liệu hình thái, nhiều biến thực chất là "anh em họ" của nhau (ví dụ: `cell_area_px` và `perimeter_px`). Nếu giữ cả hai, các mô hình như **Logistic Regression** hay **SVM** sẽ bị nhiễu.

* **Kỹ thuật: Variance Inflation Factor (VIF).**
    * Nếu một biến có $VIF > 10$, nghĩa là nó có thể được dự đoán từ các biến khác.
    * **Hành động:** Loại bỏ biến có VIF cao nhất. Ví dụ: Nếu `area`, `perimeter` và `diameter` có tương quan cực cao, hãy chỉ giữ lại `diameter` (vì nó có Skewness thấp hơn).
* **Kỹ thuật: Correlation Matrix (Heatmap).**
    * Loại bỏ một trong hai biến nếu hệ số tương quan $|r| > 0.9$.



## 2. Lọc theo Thông tin tương hỗ (Mutual Information - MI)
Khác với tương quan tuyến tính (Correlation), MI đo lường mức độ phụ thuộc giữa biến đầu vào và nhãn mục tiêu `anomaly_label`, kể cả các mối quan hệ phi tuyến tính.

* **Tại sao dùng?** Rất hiệu quả cho các biến có phân phối đa đỉnh hoặc lệch nặng ở Nhóm A và B.
* **Hành động:** Tính điểm MI cho tất cả 36 biến. Những biến có điểm MI gần bằng 0 (thường là Nhóm C như `rbc_count`, `wbc_count`) nên bị loại bỏ vì chúng không chứa thông tin giúp phân biệt Bình thường/Bất thường.

## 3. Loại bỏ đặc trưng đệ quy (Recursive Feature Elimination - RFE)
Đây là phương pháp "thử sai" thông minh. Bạn chọn một mô hình lõi (ví dụ: **Random Forest** hoặc **XGBoost**) và thuật toán sẽ:
1. Huấn luyện mô hình trên toàn bộ biến.
2. Xếp hạng độ quan trọng.
3. Loại bỏ biến yếu nhất.
4. Lặp lại cho đến khi đạt được số lượng biến tối ưu.

* **Ưu điểm:** RFE tìm ra được sự kết hợp giữa các biến (ví dụ: một biến đơn lẻ có vẻ yếu nhưng khi kết hợp với biến khác lại rất mạnh).

## 4. Kiểm tra độ quan trọng bằng Hoán vị (Permutation Importance)
Độ quan trọng có sẵn trong Random Forest đôi khi bị thiên vị (bias) cho các biến có nhiều giá trị số liên tục (như các biến pixel).

* **Cách làm:** Xáo trộn ngẫu nhiên giá trị của một biến. Nếu sai số của mô hình tăng vọt, biến đó cực kỳ quan trọng. Nếu sai số không đổi, biến đó là "vô dụng".
* **Ứng dụng SHAP (SHapley Additive exPlanations):** Đây là công cụ mạnh nhất hiện nay để giải thích tại sao mô hình lại chọn tế bào đó là bất thường. SHAP sẽ chỉ rõ: "Nhân to đóng góp 40% vào quyết định, độ lệch tâm đóng góp 30%".

---

## Bảng tiêu chí quyết định (Final Decision Matrix)

Dựa trên kết quả EDA của bạn, tôi đề xuất bộ lọc cuối cùng như sau:

| Loại biến | Hành động | Lý do chuyên sâu |
| :--- | :--- | :--- |
| **Nhóm A (Hình thái)** | **Giữ lại 100%** | Điểm Mutual Information cao, KDE phân tách rõ. |
| **Nhóm B (Đa đỉnh)** | **Lọc qua VIF** | Loại bỏ bớt các biến kích thước trùng lặp (ví dụ: bỏ `perimeter` nếu đã có `area`). |
| **Nhóm C (Huyết học)** | **Loại bỏ 70%** | KDE chồng khít, MI thấp. Chỉ giữ lại 1-2 biến đại diện (như `mcv_fl`). |
| **Nhóm D (Điểm số)** | **Loại bỏ `anomaly_score`** | Tránh Data Leakage. Chỉ dùng `confidence` để lọc hàng (samples). |

---

### Quy trình code gợi ý (Workflow)
1.  **Bước 1:** Loại bỏ `anomaly_score` và các biến định danh (`cell_id`).
2.  **Bước 2:** Chạy `SelectKBest` với `mutual_info_classif` để lấy top 15-20 biến.
3.  **Bước 3:** Chạy `RFECV` (RFE với Cross-Validation) để tìm số lượng biến tối ưu cuối cùng (thường là khoảng 10-12 biến).
4.  **Bước 4:** Huấn luyện mô hình trên bộ biến tinh gọn này.