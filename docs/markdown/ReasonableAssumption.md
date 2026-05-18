Gọi:

* $s$ là biến ngẫu nhiên đại diện cho thuộc tính sinh học thực (ví dụ: kích thước, màu sắc gốc) của một tế bào.
* $p$ là biến ngẫu nhiên đại diện cho mẻ nhuộm/giao thức nhuộm mà tế bào đó được đưa vào.

Khẳng định *"mẫu được phân phối ngẫu nhiên vào các mẻ"* đồng nghĩa với việc: **Biến ngẫu nhiên $s$ và biến ngẫu nhiên $p$ độc lập với nhau ($s \perp p$)**.

---

## 2. Chứng minh toán học: $\mathbb{E}[s \mid p] = \mu_s$

Theo lý thuyết xác suất, nếu hai biến ngẫu nhiên $s$ và $p$ độc lập với nhau, thì **Hàm mật độ xác suất đồng thời (Joint PDF)** của chúng bằng tích các **Hàm mật độ xác suất biên duyên (Marginal PDF)**:


$$f(s, p) = f_S(s) \cdot f_P(p)$$

Từ đây, ta xét **Hàm mật độ xác suất có điều kiện (Conditional PDF)** của $s$ khi đã biết $p$:


$$f(s \mid p) = \frac{f(s, p)}{f_P(p)}$$

Thay công thức độc lập vào tử số:


$$f(s \mid p) = \frac{f_S(s) \cdot f_P(p)}{f_P(p)} = f_S(s)$$

> **Ý nghĩa trung gian:** Phương trình $f(s \mid p) = f_S(s)$ nói rằng: Dù bạn có biết tế bào nằm ở mẻ $p$ nào đi chăng nữa, thì quy luật phân phối kích thước/màu sắc của nó không có gì thay đổi so với toàn bộ quần thể.

Bây giờ, ta tính **Kỳ vọng có điều kiện (Conditional Expectation)** $\mathbb{E}[s \mid p]$ bằng công thức tích phân (đối với biến liên tục):


$$\mathbb{E}[s \mid p] = \int_{-\infty}^{+\infty} s \cdot f(s \mid p) \, ds$$

Thay $f(s \mid p) = f_S(s)$ vào phương trình:


$$\mathbb{E}[s \mid p] = \int_{-\infty}^{+\infty} s \cdot f_S(s) \, ds$$

Mà theo định nghĩa, vế phải chính là công thức tính kỳ vọng toán học không điều kiện (trung bình toàn cục) của biến $s$:


$$\int_{-\infty}^{+\infty} s \cdot f_S(s) \, ds = \mathbb{E}[s] = \mu_s$$

Vậy, ta có điều phải chứng minh:


$$\mathbb{E}[s \mid p] = \mu_s$$