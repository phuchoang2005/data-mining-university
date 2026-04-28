## 1. Group-wise Statistics (Chuẩn hóa theo nhóm)

Đây là kỹ thuật quan trọng nhất trong bài toán tế bào máu.

- **Vấn đề:** Một tế bào `Neutrophil` (Bạch cầu trung tính) vốn dĩ to hơn `Normal RBC` (Hồng cầu). Nếu bạn dùng `StandardScaler` cho toàn bộ cột `cell_diameter_um`, mô hình sẽ bị "ám ảnh" bởi kích thước tuyệt đối.
- **Giải pháp:** Tính toán **Z-score theo từng loại tế bào**.
  - Công thức: $$Z_{grouped} = \frac{x - \mu_{cell\_type}}{\sigma_{cell\_type}}$$
- **Ý nghĩa:** Đặc trưng này cho mô hình biết: "Tế bào này to bất thường **so với các tế bào cùng loại với nó**", thay vì to so với trung bình chung của mẫu máu.

## 2. ~~Smoothing Target Encoding~~ → One-Hot Encoding cho `cell_type`

> **⚠️ Cảnh báo:** Trong bộ dữ liệu này, `cell_type` có mối quan hệ gần như xác định với `anomaly_label` (p_value = 0.0). Điều này có nghĩa là mỗi loại tế bào đều ánh xạ gần 100% vào nhãn 0 hoặc 1. Target Encoding (kể cả với Smoothing) sẽ chuyển `cell_type` thành giá trị gần bằng 0.0 hoặc 1.0 — tức là **bản sao của nhãn mục tiêu**, gây Overfitting nghiêm trọng.

- **Giải pháp thực tế:** Sử dụng **One-Hot Encoding** cho `cell_type` (gom nhóm hiếm < 2% vào `Other_Rare_Types`). OHE mã hóa **danh tính** của loại tế bào mà không nhúng target information.
- **Khi nào dùng Target Encoding:** Chỉ khi mối quan hệ giữa biến phân loại và nhãn là **xác suất** (ví dụ: 60%/40%), không phải xác định (100%/0%).

---

## 3. Tạo đặc trưng Tương tác (Cross-Feature Interactions)

Sự kết hợp giữa một đặc trưng phân loại và một ngưỡng định lượng thường là chìa khóa để phát hiện bệnh lý.

- **Flag Features (Biến cờ hiệu):** Tạo các biến Boolean dựa trên kiến thức chuyên môn.
  - _Ví dụ:_ `Is_Large_Nucleus_in_Small_Cell` = (Nếu `cell_type` là 'Lymphocyte' VÀ `nucleus_area_pct` > 80%).
- **Categorical-Driven Scaling:** Nhân các đặc trưng hình thái với trọng số của `staining_protocol`.
  - _Lý do:_ Nếu nhuộm Wright làm nhân tế bào trông to hơn 5% so với Giemsa, bạn có thể tạo biến điều chỉnh: `adj_nucleus_area = nucleus_area_pct * staining_adjustment_factor`.

[Chi tiết](detail_CrossFeatureInteration.md)

---

## 4. Kết luận cho Team

Việc tối ưu hóa sự kết hợp này giúp mô hình đạt được 2 mục tiêu:

1.  **Tính ổn định (Robustness):** Không bị đánh lừa bởi các yếu tố gây nhiễu như kính hiển vi hay quy trình nhuộm.
2.  **Độ nhạy (Sensitivity):** Phát hiện được các tế bào bất thường "ẩn mình" vốn có kích thước trông giống tế bào bình thường nhưng lại có cấu trúc nhân sai lệch so với quần thể cùng loại.

**Lời khuyên:** Sau khi tạo các đặc trưng kết hợp này, hãy sử dụng biểu đồ **SHAP Summary Plot**. Nó sẽ cho team bạn thấy rõ: "Liệu sự kết hợp giữa `cell_type` và `nc_ratio` có thực sự là yếu tố quyết định nhãn 1 hay không?".

Team bạn có muốn tôi giải thích thêm về cách dùng **SHAP** để kiểm chứng các đặc trưng kết hợp này sau khi huấn luyện không?
