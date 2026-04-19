## 1. Feature Engineering: Tạo đặc trưng dựa trên kiến thức miền (Domain Knowledge)
Mặc dù bạn đã có khá nhiều đặc trưng, nhưng việc tạo ra các biến tương tác có thể giúp mô hình phi tuyến tính bắt trọn các dấu hiệu bệnh lý:

* **Chuẩn hóa kích thước theo Độ phóng đại:** Các biến `cell_area_px` và `perimeter_px` phụ thuộc vào `magnification_x`. Bạn nên tạo ra các đặc trưng thực tế bằng cách quy đổi:
    $$\text{Actual Area} = \frac{\text{cell\_area\_px}}{(\text{magnification\_x})^2}$$
    Việc này giúp mô hình đồng nhất dữ liệu dù ảnh được chụp ở độ phóng đại 40x hay 100x.
* **Tỷ lệ tương phản màu sắc:** Thay vì chỉ dùng `mean_r, g, b` riêng lẻ, hãy tạo ra các tỷ lệ như $R/G$ hoặc $G/B$. Trong huyết học, sự thay đổi sắc thái (ví dụ: tế bào bắt màu kiềm hoặc ưa acid) là một chỉ số phân loại cực mạnh.

[Chi tiết](detail_1.md)

## 2. Xử lý phân phối đa đỉnh (Multi-modality) bằng Clustering
Như bạn thấy ở Nhóm B, các biến có nhiều đỉnh (do chứa nhiều loại tế bào khác nhau). 
* **Chiến lược:** Sử dụng thuật toán **K-Means** hoặc **Gaussian Mixture Models (GMM)** để gom cụm các tế bào dựa trên hình thái (`cell_area`, `nucleus_area`).
* **Ứng dụng:** Thêm nhãn cụm (Cluster ID) này như một đặc trưng đầu vào. Việc này "mách" cho mô hình biết tế bào này thuộc nhóm kích thước nào trước khi thực hiện phân loại nhị nguyên.

[Chi tiết](detail_2.md)

## 3. Lựa chọn đặc trưng (Feature Selection) chuyên sâu
Đừng chỉ giữ lại tất cả các biến. Như phân tích KDE ở Nhóm C, nhiều biến huyết học (`wbc_count`, `rbc_count`) có khả năng phân tách bằng 0.
* **Recursive Feature Elimination (RFE):** Sử dụng Random Forest hoặc XGBoost để loại bỏ dần các đặc trưng ít quan trọng nhất.
* **Mutual Information:** Tính toán độ phụ thuộc thông tin giữa các biến đầu vào và `anomaly_label`. Những biến có điểm Mutual Information thấp nên được loại bỏ để giảm nhiễu và tránh hiện tượng **Curse of Dimensionality** (Lời nguyền đa chiều).

[Chi tiết](detail_3.md)

## 4. Xử lý mất cân bằng nhãn (Advanced Imbalance Handling)
Với `anomaly_label` có Skewness 0.77, dữ liệu của bạn đang lệch. Ngoài việc dùng SMOTE thông thường, hãy thử:
* **SMOTE-Tomek Links:** Kết hợp tạo mẫu ảo (Oversampling) và xóa các mẫu gây nhiễu ở biên giới giữa hai lớp (Undersampling). Điều này giúp đường biên phân loại của các mô hình như SVM hoặc KNN trở nên "sạch" hơn.
* **Cost-sensitive Learning:** Thay vì thay đổi dữ liệu, hãy gán "hình phạt" nặng hơn cho mô hình khi dự đoán sai lớp Bất thường (Nhãn 1).

## 5. Tăng cường dữ liệu bằng "Dịch chuyển phân phối" (Distribution Shifting)
Nếu tập dữ liệu nhỏ, bạn có thể áp dụng các kỹ thuật mô phỏng nhiễu:
* **Thêm nhiễu Gaussian nhẹ** vào các đặc trưng Nhóm B để mô hình trở nên bền bỉ hơn (robust) với các sai số đo đạc nhỏ của thiết bị.
* **Chuẩn hóa theo Staining Protocol:** Nếu bạn phát hiện `staining_protocol` ảnh hưởng đến `mean_r, g, b`, hãy thực hiện **Group-wise Scaling** (chuẩn hóa riêng biệt cho từng nhóm quy trình nhuộm) để đưa tất cả về cùng một không gian màu sắc tham chiếu.

[Chi tiết](detail_4.md)

---