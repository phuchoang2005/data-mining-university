## 1. Tương tác Categorical x Numerical (Contextual Features)

Đây là hướng bạn đã quan tâm. Mục tiêu là tạo ra sự "nhạy cảm theo ngữ cảnh" cho mô hình.

- **Z-score theo Loại tế bào (Grouped Z-score):** Đã đề cập ở phần trước, đây là "vũ khí" mạnh nhất.
  - **Thực hiện:** Với mỗi mẫu, tính: $\frac{Value - Mean_{CellType}}{Std_{CellType}}$. Áp dụng cho `cell_diameter_um` và `nucleus_area_pct`.
- **Mã hóa Tương tác (Interaction Encoding):** Kết hợp một biến phân loại quan trọng với một ngưỡng định lượng.
  - **Ví dụ:** Tạo biến `Is_Large_Lymphocyte` = 1 nếu (`cell_type` == 'Lymphocyte' AND `cell_area_px` > 500), ngược lại = 0.
- **Protocol-Adjusted Intensity:** Điều chỉnh cường độ màu sắc dựa trên quy trình nhuộm.
  - **Công thức:** $Adjusted\_Intensity = stain\_intensity \times TargetMean_{StainingProtocol}$

## 2. Tương tác Categorical x Categorical (Feature Crossing)

Khi hai biến phân loại kết hợp với nhau, chúng có thể tạo ra một "ngữ cảnh" hoàn toàn mới.

- **Cell-Protocol Cross:** Kết hợp `cell_type` và `staining_protocol`.
  - **Tại sao?** Một loại tế bào `Blast_Cell` có thể trông rất khác nhau dưới nhuộm `Giemsa` so với `Wright`.
  - **Thực hiện:** Tạo biến mới `Cell_Stain = cell_type + "_" + staining_protocol`. Sau đó dùng **One-Hot Encoding** cho biến mới này.
  - > ⚠️ **Lưu ý:** Không dùng Target Encoding cho biến chứa `cell_type` vì `cell_type` có mối quan hệ xác định (p=0.0) với `anomaly_label` — Target Encoding sẽ gây Overfitting.
- **Age-Type Interaction:** Kết hợp `patient_age_group` và `cell_type`.
  - **Tại sao?** Tỷ lệ xuất hiện của các tế bào non (Blast) ở nhóm `Pediatric` (trẻ em) mang ý nghĩa bệnh lý khác so với nhóm `Elderly` (người già).

## 3 Quy trình Kiểm chứng (Validation Workflow) cho Team

Sau khi Người 2 tạo ra các biến tương tác này, Người 3 và Người 4 cần làm:

1.  **Kiểm tra Tương quan:** Đảm bảo biến tương tác mới không bị tương quan quá mức ($r > 0.95$) với các biến gốc để tránh đa cộng tuyến.
2.  **Đánh giá SHAP:** Sử dụng SHAP để xem mô hình thực sự đánh giá cao biến tương tác nào.
    - _Ví dụ:_ Nếu `NC_Ratio` đứng top 3 quan trọng, hướng đi đó là đúng. Nếu `Cell_Stain` đứng cuối, có thể bỏ qua để tinh gọn mô hình.
