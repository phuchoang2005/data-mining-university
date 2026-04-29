## 1. Thêm nhiễu trắng (Gaussian Noise Injection)
Đây là cách cơ bản nhất để "làm khó" mô hình, giúp nó không bị Overfitting vào các con số quá chính xác của thiết bị hiện tại.

* **Cách làm:** Cộng một lượng nhỏ nhiễu $\epsilon$ vào các đặc trưng số, trong đó $\epsilon \sim \mathcal{N}(0, \sigma^2)$.
* **Áp dụng cho Nhóm B & C:** Thêm nhiễu vào `cell_diameter_um` hoặc `mean_r, g, b`.
* **Mục tiêu:** Mô phỏng sự sai số ngẫu nhiên giữa các lần đo hoặc sự khác biệt nhỏ về độ nhạy của cảm biến camera trên kính hiển vi.
* **Lưu ý:** Chỉ nên chọn $\sigma$ bằng khoảng 1-2% giá trị Standard Deviation của biến đó để tránh làm biến dạng đặc trưng bệnh lý.


---

## 2. Chuẩn hóa và Dịch chuyển theo Giao thức (Staining Protocol Shifting)
Dữ liệu của bạn có cột `staining_protocol`. Màu sắc tế bào (`mean_r, g, b`) phụ thuộc rất nhiều vào việc mẫu máu được nhuộm đậm hay nhạt.

* **Kỹ thuật:** **Group-wise Normalization & Shifting.**
    * Tính trung bình màu sắc $\mu_{protocol}$ cho từng loại giao thức nhuộm.
    * Dịch chuyển phân phối màu sắc của mẫu từ Giao thức A sang Giao thức B bằng cách cộng thêm độ lệch giữa hai giá trị trung bình: $x_{new} = x + (\mu_{B} - \mu_{A})$.
* **Mục tiêu:** Giúp mô hình nhận diện được tế bào bất thường bất kể nó được nhuộm bằng phương pháp Giemsa, Wright hay bất kỳ quy trình nào khác.

---

## 3. Tổng hợp mẫu mới bằng SMOTE-Tomek (Synthetic Distribution Shifting)
Vì nhãn `anomaly_label` của bạn bị lệch (Skew = 0.77), lớp "Bất thường" đang bị thiếu hụt.

* **Cách làm:** Thay vì chỉ lặp lại các mẫu cũ, SMOTE tạo ra các mẫu mới nằm **trên đường thẳng nối** giữa các mẫu bất thường có sẵn. 
* **Dịch chuyển phân phối:** Việc này thực chất là làm "dày" thêm vùng không gian của lớp thiểu số, dịch chuyển trọng tâm phân phối của lớp Bất thường về phía các vùng dữ liệu chưa được khám phá nhưng vẫn hợp lệ về mặt sinh học.
* **Kết hợp Tomek Links:** Xóa bỏ các mẫu nằm quá sát biên giới giữa hai lớp (nơi phân phối bị chồng lấn mạnh) để tạo ra một khoảng cách (Margin) rõ ràng hơn cho mô hình.



---

## 4. Mô phỏng dịch chuyển hiệp biến (Covariate Shift Simulation)
Trong thực tế, điều kiện lấy mẫu có thể thay đổi (ví dụ: máy đo ở bệnh viện A luôn cho kết quả `hemoglobin` cao hơn bệnh viện B một chút).

* **Kỹ thuật:** **Feature Scaling Shifting.**
    * Thực hiện nhân toàn bộ một cột đặc trưng với một hệ số biến thiên nhỏ (ví dụ: $0.98$ hoặc $1.02$).
    * Áp dụng cho các chỉ số huyết học ở **Nhóm C**.
* **Mục tiêu:** Tạo ra một tập dữ liệu "stress-test" để kiểm tra xem mô hình có bị sụp đổ khi các chỉ số tổng quát của bệnh nhân bị dịch chuyển nhẹ hay không.

---

## Bảng hướng dẫn áp dụng theo nhóm biến

| Nhóm biến | Loại dịch chuyển | Công thức gợi ý |
| :--- | :--- | :--- |
| **Nhóm A (Bệnh lý)** | **Hạn chế dịch chuyển** | Chỉ dùng SMOTE để tạo mẫu mới, tránh thêm nhiễu quá mạnh làm mất đặc trưng nhân. |
| **Nhóm B (Hình thái)** | **Gaussian Noise** | $x' = x + \text{rnorm}(0, 0.01 \times \text{std}(x))$ |
| **Nhóm C (Huyết học)** | **Covariate Shift** | $x' = x \times \text{uniform}(0.98, 1.02)$ |
| **Nhóm D (Màu sắc)** | **Protocol Shifting** | Dịch chuyển Mean màu sắc theo từng loại `staining_protocol`. |
---