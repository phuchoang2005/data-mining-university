Để nâng cao hiệu quả mô hình, việc chỉ sử dụng các đặc trưng "thô" (raw features) thường không đủ. Trong huyết học (Hematology), các chuyên gia không nhìn vào từng con số đơn lẻ mà nhìn vào **mối tương quan** giữa chúng.

Dưới đây là 5 hướng tạo đặc trưng mới (Feature Engineering) dựa trên kiến thức chuyên môn để giúp mô hình của bạn "thông minh" như một bác sĩ xét nghiệm:

---

## 1. Chỉ số N/C Ratio (Nucleus-to-Cytoplasm Ratio)
Đây là "tiêu chuẩn vàng" trong việc phân biệt tế bào lành tính và ác tính. Tế bào bất thường (như tế bào ung thư hoặc tế bào non) thường có nhân rất lớn chiếm gần hết diện tích tế bào.

* **Công thức:**
$$NC\_Ratio = \frac{nucleus\_area\_pct}{100 - nucleus\_area\_pct}$$
* **Ý nghĩa:** Nếu tỷ lệ này đột ngột tăng cao, đó là dấu hiệu mạnh mẽ của nhãn `1` (Bất thường). Bạn cũng có thể dùng `cytoplasm_ratio` để tính toán chính xác hơn phần diện tích còn lại.

## 2. Chuẩn hóa Đơn vị Vật lý (Physical Units Normalization)
Dữ liệu của bạn có các mức độ phóng đại khác nhau (40x, 60x, 100x). Một tế bào "to" ở 40x sẽ có số pixel khác hẳn một tế bào "to" ở 100x. Để mô hình không bị nhầm lẫn, bạn cần quy đổi về đơn vị thực tế ($\mu m$).

* **Cách làm:** Tạo ra các đặc trưng "thực" thay vì dựa trên pixel.
    * `true_cell_area = cell_area_px / (magnification_x^2)`
    * `true_perimeter = perimeter_px / magnification_x`
* **Ý nghĩa:** Giúp mô hình đồng nhất được kích thước tế bào trên mọi loại kính hiển vi và độ phóng đại.



## 3. Chỉ số Độ phức tạp Hình dạng (Shape Complexity/Form Factor)
Tế bào bình thường thường có màng trơn tru và hình dáng ổn định. Tế bào bất thường thường có hình dạng kỳ dị, màng tế bào lồi lõm.

* **Công thức (Form Factor):**
$$Form\_Factor = \frac{4\pi \times cell\_area\_px}{perimeter\_px^2}$$
* **Ý nghĩa:** Giá trị này càng gần **1.0**, tế bào càng tròn trịa hoàn hảo. Giá trị càng nhỏ, tế bào càng có hình dạng phức tạp hoặc màng tế bào bị biến dạng nặng (`membrane_smoothness` thấp).

## 4. Đặc trưng Màu sắc chuẩn hóa (Chromaticity Features)
Cường độ sáng (`stain_intensity`) có thể thay đổi tùy vào ánh sáng lúc chụp, nhưng **tỷ lệ màu** thì ít thay đổi hơn.

* **Cách làm:** Thay vì dùng `mean_r`, `mean_g`, `mean_b`, hãy tạo ra các biến tỷ lệ:
    * $R\_Ratio = R / (R + G + B)$
    * $G\_Ratio = G / (R + G + B)$
    * $B\_Ratio = B / (R + G + B)$
* **Ý nghĩa:** Tế bào bắt màu kiềm (xanh đậm) hay ưa acid (hồng/đỏ) sẽ được thể hiện rõ ràng qua tỷ lệ này, loại bỏ được nhiễu do ánh sáng quá chói hoặc quá tối.

## 5. Tương quan Cá thể - Quần thể (Global-Local Interaction)
Một tế bào có đường kính 12$\mu m$ có thể là bình thường với người này nhưng là bất thường với người khác nếu các tế bào còn lại của họ đều rất nhỏ.

* **Cách làm:** Tạo biến so sánh kích thước tế bào hiện tại với chỉ số trung bình của bệnh nhân đó (nếu có `patient_id`) hoặc với chỉ số `mcv_fl` (thể tích trung bình hồng cầu).
    * `relative_size = cell_diameter_um / mcv_fl`
* **Ý nghĩa:** Giúp mô hình hiểu được ngữ cảnh. Nếu một tế bào "khổng lồ" xuất hiện trong một mẫu máu có chỉ số MCV thấp, khả năng cao đó là một tế bào non (Blast) hoặc đại thực bào bất thường.

---

### Bảng tóm tắt các đặc trưng mới cần tạo:

| Đặc trưng mới | Công thức/Nguồn | Nhắm tới nhóm biến | Mục tiêu phân loại |
| :--- | :--- | :--- | :--- |
| **NC_Index** | Nucleus Area / Cytoplasm Area | Nhóm A | Phát hiện tế bào ác tính |
| **Real_Size** | Area / (Mag^2) | Nhóm B | Đồng nhất dữ liệu thiết bị |
| **Compactness** | Area / (Perimeter^2) | Nhóm A + B | Phát hiện biến dạng màng |
| **Color_Shift** | R / (R+G+B) | Nhóm C | Phân loại loại tế bào (Dòng bạch cầu) |
| **Size_Anomaly** | Diameter / MCV | Nhóm B + C | Phát hiện sự bất thường kích thước |

Việc tạo thêm khoảng 5-7 đặc trưng "thông minh" này thường giúp tăng độ chính xác (Accuracy) và F1-score của mô hình thêm **3% - 8%** so với việc chỉ dùng dữ liệu thô.
