## Vế 1: Tính chất tuyến tính của kỳ vọng (Linearity of Expectation)

Toán tử kỳ vọng ($\mathbb{E}$) bản chất là một phép tính tổng có trọng số (hoặc tích phân), do đó nó có tính chất tuyến tính.

Với hai biến ngẫu nhiên $X$ và $Y$ bất kỳ, kỳ vọng của tổng luôn bằng tổng các kỳ vọng:


$$\mathbb{E}[X + Y] = \mathbb{E}[X] + \mathbb{E}[Y]$$

Tính chất này **vẫn giữ nguyên giá trị** khi chúng ta áp dụng điều kiện (Conditional Expectation). Nghĩa là, nếu có thêm điều kiện $Z$ xảy ra, thì:


$$\mathbb{E}[X + Y \mid Z] = \mathbb{E}[X \mid Z] + \mathbb{E}[Y \mid Z]$$

Áp dụng trực tiếp vào công thức của bạn, với $X = s$ (tín hiệu gốc), $Y = b^{(p)}$ (nhiễu), và điều kiện $Z = p$ (nhóm giao thức $p$), ta có bước trung gian đầu tiên:


$$\mathbb{E}[s + b^{(p)} \mid p] = \mathbb{E}[s \mid p] + \mathbb{E}[b^{(p)} \mid p]$$

---

## Vế 2: Vì sao $\mathbb{E}[b^{(p)} \mid p] = b^{(p)}$? (Hằng số đối với nhóm $p$)

Kỳ vọng có điều kiện $\mathbb{E}[Y \mid Z]$ có thể hiểu nôm na là: *"Nếu tôi đã biết thông tin $Z$ rồi, thì giá trị trung bình của $Y$ sẽ là bao nhiêu?"*

Trong bối cảnh này:

* $b^{(p)}$ là độ lệch màu (bias) **đặc trưng và cố định** của riêng giao thức nhuộm $p$.
* Ví dụ: Giao thức nhuộm Giemsa (nhóm $p$) luôn làm cho ảnh bị ám xanh thêm đúng $20$ đơn vị màu. Con số $+20$ này là áp dụng chung cho *mọi* bức ảnh trong nhóm $p$.

Vì vậy, khi ta xét điều kiện *"đang ở trong nhóm $p$"*, thì đại lượng $b^{(p)}$ không còn là một biến số ngẫu nhiên mơ hồ nữa. Nó đã biến thành một **hằng số xác định** (deterministic value).

Theo định lý cơ bản của thống kê, kỳ vọng của một hằng số $c$ thì bằng chính nó: $\mathbb{E}[c] = c$. Tương tự với kỳ vọng có điều kiện:


$$\mathbb{E}[b^{(p)} \mid \text{giao thức là } p] = b^{(p)}$$

> *(Giống như việc bạn hỏi: "Nếu chỉ tính riêng các bức ảnh thuộc nhóm Giemsa, thì độ lệch màu trung bình do Giemsa gây ra là bao nhiêu?". Câu trả lời hiển nhiên là: Bằng chính độ lệch của Giemsa).*

---

## Tổng hợp lại phân tích

Nhờ sự kết hợp của cả hai lập luận trên:

1. **Bước 1 (Tính tuyến tính):** Tách kỳ vọng của tổng thành tổng hai kỳ vọng.

$$\mathbb{E}[s + b^{(p)} \mid p] = \mathbb{E}[s \mid p] + \mathbb{E}[b^{(p)} \mid p]$$


2. **Bước 2 (Tính chất hằng số):** Triệt tiêu toán tử $\mathbb{E}$ ở vế sau vì $b^{(p)}$ đã là hằng số trong nhóm $p$.

$$\mathbb{E}[b^{(p)} \mid p] = b^{(p)}$$



Kết hợp lại, ta có phương trình chứng minh hoàn chỉnh:


$$\mu_c^{(p)} = \mathbb{E}[s \mid p] + b^{(p)}$$