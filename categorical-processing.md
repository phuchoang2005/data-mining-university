## 1. Nhóm Biến Có Ý Nghĩa Thống Kê Cao ($p < 0.05$)

Đây là những biến có mối liên hệ mật thiết với việc tế bào đó là Bình thường hay Bất thường.

### a. `cell_type` và `disease_category` ($p = 0.0$)

- **Phân tích:** Đây là những biến mang thông tin sinh học cốt lõi. Tuy nhiên, nhìn vào biểu đồ, `cell_type` có rất nhiều nhóm nhỏ (cardinality cao) và một số nhóm có tỷ lệ cực thấp (như `Artefact`, `Smudge Cell`).
- **Cảnh báo Data Leakage:** Biến `disease_category` chứa các giá trị như "Normal_WBC", "Leukemia", "Anemia". Nếu bạn dùng biến này để dự đoán `anomaly_label`, mô hình sẽ đạt độ chính xác 100% một cách vô nghĩa (vì "Normal" chắc chắn là nhãn 0, "Leukemia" chắc chắn là nhãn 1).
- **Hướng xử lý:**
  - **`disease_category`:** **Loại bỏ (Drop)** khỏi tập huấn luyện để tránh rò rỉ dữ liệu, hoặc chỉ dùng để phân tích hậu kiểm.
  - **`cell_type`:** Sử dụng **Target Encoding** (mã hóa theo trung bình nhãn) hoặc **One-Hot Encoding**. Với các nhóm có tỷ lệ < 2% (như `Sickle_Cell`, `Spherocyte`), hãy gom chúng vào một nhóm chung gọi là **"Other_Rare_Types"** để tránh Overfitting.

### b. `staining_protocol` ($p = 0.026$)

- **Phân tích:** Giá trị $p < 0.05$ cho thấy quy trình nhuộm (Giemsa, Wright,...) có ảnh hưởng đến kết quả phân loại. Điều này có thể do một số bệnh lý chỉ được phát hiện rõ dưới một loại nhuộm nhất định.
- **Hướng xử lý:** Sử dụng **One-Hot Encoding**. Vì chỉ có 3 giá trị, việc này sẽ tạo thêm 3 cột binary đơn giản cho mô hình.

---

## 2. Nhóm Biến Không Có Ý Nghĩa Thống Kê ($p > 0.05$)

Những biến này dường như độc lập với nhãn mục tiêu trong tập dữ liệu hiện tại.

### a. `patient_age_group` ($p = 0.589$) và `patient_sex` ($p = 0.376$)

- **Phân tích:** Giới tính và độ tuổi không trực tiếp quyết định một tế bào đơn lẻ là bất thường hay không (trong ngữ cảnh bộ dữ liệu này).
- **Hướng xử lý:**
  - **`patient_sex`:** Có thể giữ lại bằng **One-Hot Encoding** (vì chỉ có 2 giá trị M/F) để mô hình có tính bao quát.
  - **`patient_age_group`:** Vì đây là biến có thứ tự (Pediatric < Adult < Elderly), bạn nên sử dụng **Ordinal Encoding** (gán nhãn 1, 2, 3) thay vì One-Hot.

### b. `dataset_source` ($p = 0.520$) và `microscope_model` ($p = 0.408$)

- **Phân tích:** Đây là tin tốt! Việc $p$-value cao cho thấy mô hình của bạn sẽ không bị "thiên kiến" (bias) bởi việc ảnh đó chụp từ kính hiển vi nào hay nguồn dữ liệu nào. Điều này giúp mô hình có khả năng tổng quát hóa tốt hơn.
- **Hướng xử lý:** **Cân nhắc loại bỏ (Drop)** cả hai biến này để giảm chiều dữ liệu (Dimensionality Reduction), giúp mô hình tinh gọn và tập trung hoàn toàn vào các đặc trưng hình thái tế bào.

---

## 3. Tổng kết bảng kế hoạch tiền xử lý Categorical

| Thuộc tính              | Tình trạng ($p$-value) | Phương pháp mã hóa    | Hành động bổ sung             |
| :---------------------- | :--------------------- | :-------------------- | :---------------------------- |
| **`cell_type`**         | 0.0 (Rất mạnh)         | Target Encoding / OHE | Gom nhóm các loại hiếm (< 2%) |
| **`disease_category`**  | 0.0 (Rất mạnh)         | **Drop**              | Tránh Data Leakage            |
| **`staining_protocol`** | 0.026 (Mạnh)           | One-Hot Encoding      | Giữ nguyên                    |
| **`patient_age_group`** | 0.589 (Yếu)            | Ordinal Encoding      | Giữ lại làm biến kiểm soát    |
| **`patient_sex`**       | 0.376 (Yếu)            | One-Hot Encoding      | Giữ lại làm biến kiểm soát    |
| **`dataset_source`**    | 0.520 (Rất yếu)        | **Drop**              | Giảm nhiễu hệ thống           |
| **`microscope_model`**  | 0.408 (Rất yếu)        | **Drop**              | Giảm nhiễu hệ thống           |

---

## 4. Tối ưu hóa chuyên sâu: Sự kết hợp Categorical & Numerical

Để nâng cao hiệu quả, team bạn có thể thực hiện thêm:

1.  **Group-wise Scaling:** Thay vì chuẩn hóa `cell_area_px` cho toàn bộ dữ liệu, hãy chuẩn hóa theo từng `cell_type`. (Ví dụ: Một con Bạch cầu trung tính to là bình thường, nhưng một con Hồng cầu to lại là bất thường).
2.  **Interaction Features:** Tạo biến kết hợp như `cell_type` + `staining_protocol` để xem một loại tế bào dưới một loại nhuộm nhất định có bộc lộ đặc trưng tốt hơn không.

[Chi tiết](/numeric/detail_Categorical&Numberical.md)
