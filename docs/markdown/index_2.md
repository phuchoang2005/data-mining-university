# Winsorization
## 1. Bản chất toán học của công thức

Hàm số phân nhánh (piecewise function) này hoạt động như một bộ giới hạn biên (clamping/capping) dựa trên phân vị (percentile):

* **Nhánh 1 ($x < P_1 \rightarrow x' = P_1$):** Tất cả các giá trị cực nhỏ (nằm dưới phân vị thứ 1) sẽ bị kéo lên và gán bằng đúng giá trị tại biên $P_1$.
* **Nhánh 2 ($P_1 \le x \le P_{99} \rightarrow x' = x$):** Vùng "an toàn". Khoảng 98% dữ liệu nằm ở giữa sẽ được giữ nguyên vẹn, không có bất kỳ sự biến đổi nào.
* **Nhánh 3 ($x > P_{99} \rightarrow x' = P_{99}$):** Tất cả các giá trị cực lớn (vượt quá phân vị thứ 99) sẽ bị ép hạ xuống và gán bằng đúng giá trị tại biên $P_{99}$.

---

## 2. Ý nghĩa toán học và thống kê trong xử lý Outliers

### Bảo toàn kích thước mẫu (Sample Size Preservation)

Khi xử lý outlier, bản năng đầu tiên thường là loại bỏ hoàn toàn dòng dữ liệu đó (Trimming/Truncation). Tuy nhiên, nếu xóa dòng, bạn sẽ làm mất luôn thông tin hợp lệ của các biến (features) khác trên cùng dòng đó. Winsorization giải quyết triệt để bài toán này: **Số lượng mẫu ($N$) được giữ nguyên 100%**, giúp các phép toán thống kê phía sau không bị mất mát bậc tự do (degrees of freedom) hoặc giảm sức mạnh thống kê (statistical power).

### Tăng tính bền vững (Robustness) cho các đại lượng đo lường

Outliers là "kẻ thù" của các đại lượng nhạy cảm như Trung bình cộng ($\mu$) và Phương sai ($\sigma^2$). Chỉ cần một vài giá trị cực đại xuất hiện, đường trung bình sẽ bị kéo lệch hẳn về phía đó.

* Khi ép các điểm dị biệt về $P_1$ và $P_{99}$, Winsorization làm cho số trung bình mới tiến gần hơn về số trung vị (Median) — một đại lượng vốn rất bền vững trước biến động.
* Nó làm giảm đáng kể phương sai ảo do nhiễu gây ra, giúp các mô hình toán học (như Hồi quy tuyến tính - Linear Regression) không bị "dắt mũi" bởi một vài điểm cá biệt.

### Giữ lại thông tin về mặt thứ tự (Ordinal Relationship)

Nếu một điểm dữ liệu vốn là lớn nhất hệ thống, sau khi Winsorize, nó *vẫn* nằm trong nhóm những điểm lớn nhất (bằng $P_{99}$). Nó không bị biến thành một giá trị trung bình vô nghĩa, giúp giữ lại cấu trúc phân hạng tương đối của dữ liệu.

### Ổn định hóa phân phối phục vụ Machine Learning

Trong các mô hình học máy sử dụng thuật toán tối ưu dựa trên Gradient, các giá trị outlier quá lớn có thể khiến gradient bị bùng nổ (gradient explosion), làm mô hình mất ổn định. Việc "chặn trần, chặn sàn" toán học hóa một vùng phân phối có biên độ kiểm soát được, giúp thuật toán hội tụ nhanh và mượt mà hơn khi tính toán ma trận.

**Tóm lại:** Winsorization không triệt tiêu outlier theo kiểu "khai tử", mà là đặt ra một giới hạn nghiêm ngặt để đưa các phần tử "nổi loạn" về chuẩn mực chung của tập dữ liệu.

# Yeo-Johnson Transform

Nếu như **Winsorization** chọn cách xử lý trực diện bằng cơ chế **"gọt giũa và cắt ngọn"** (clamping), tạo ra các nút thắt dữ liệu tại biên, thì **Yeo-Johnson Transform** lại tiếp cận bài toán theo một triết lý toán học hoàn toàn khác: **"Uốn cong không gian"** (Power Transformation).

Nó không cắt bỏ hay thay đổi giá trị của bất kỳ ai, mà dùng một hàm số phi tuyến để co giãn toàn bộ tập dữ liệu, biến một phân phối lệch chuẩn, méo mó trở nên cân đối và giống với **Phân phối chuẩn (Gaussian/Normal Distribution)** nhất có thể.

---

## 1. Công thức Toán học của Yeo-Johnson

Yeo-Johnson (xuất hiện năm 2000) là bản nâng cấp tối quan trọng của thuật toán Box-Cox nổi tiếng. Trong khi Box-Cox bất lực trước dữ liệu bằng 0 hoặc âm, Yeo-Johnson giải quyết triệt để bằng một hàm phân nhánh bốn trường hợp theo giá trị của biến số $y$ và tham số tối ưu $\lambda$:

$$y^{(\lambda)} = \begin{cases} \frac{(y + 1)^\lambda - 1}{\lambda} & \text{nếu } y \ge 0, \lambda \neq 0 \\ \log(y + 1) & \text{nếu } y \ge 0, \lambda = 0 \\ -\frac{(-y + 1)^{2 - \lambda} - 1}{2 - \lambda} & \text{nếu } y < 0, \lambda \neq 2 \\ -\log(-y + 1) & \text{nếu } y < 0, \lambda = 2 \end{cases}$$

*Trong đó, $\lambda$ không phải do con người tự chọn bừa, mà được tìm ra thông qua phương pháp tối ưu Maximum Likelihood Estimation (Ước lượng hợp lý cực đại) để đưa phân phối về dạng chuẩn nhất.*

---

## 2. Ý nghĩa toán học trong việc xử lý Outliers và Phân phối

### Thuần hóa Outliers bằng cách "Nén khoảng cách"

Yeo-Johnson không biến một siêu Outlier thành một giá trị bình thường, nó chỉ **thu nhỏ khoảng cách tương đối** giữa Outlier và phần còn lại của thế giới.

* Ví dụ với dữ liệu dương và $\lambda \to 0$, hàm số biến đổi tương đương với hàm logarit $\log(y+1)$. Trong thang đo logarit, khoảng cách giữa $10$ và $100$ cũng chỉ bằng khoảng cách giữa $100$ và $1000$.
* Nhờ vậy, các đuôi dài (long-tail) của phân phối lệch phải (positive skew) bị ép co lại, kéo các điểm ngoại lai cực đại về gần trung tâm hơn mà không làm mất đi tính chất "lớn nhất" của chúng.

### Ổn định phương sai (Homoscedasticity)

Trong nhiều mô hình thống kê và học máy (như hồi quy tuyến tính, ANOVA), giả định quan trọng là phương sai của sai số phải không đổi (homoscedasticity). Outliers xuất hiện thường làm phá vỡ giả định này (gây ra hiện tượng heteroscedasticity). Việc uốn cong không gian bằng Yeo-Johnson giúp dàn đều mật độ dữ liệu, ổn định lại phương sai trên toàn dải phân phối.

### Bảo toàn tính trơn và tính khả vi (Smoothness & Differentiability)

Khác với Winsorization tạo ra các đường gãy khúc và "gói" một đống dữ liệu vào một điểm duy nhất (tạo ra các đỉnh nhọn bất thường tại $P_1$ và $P_{99}$ trên biểu đồ mật độ), Yeo-Johnson là một hàm **đơn điệu nghiêm ngặt** và **khả vi liên tục**. Điều này đồng nghĩa với việc nó giữ nguyên thứ tự trước-sau của dữ liệu và cực kỳ thân thiện với các thuật toán tối ưu hóa dựa trên đạo hàm (Gradient Descent).

---

## 3. So sánh tư duy xử lý Outliers: Winsorization vs. Yeo-Johnson

| Tiêu chí | Winsorization | Yeo-Johnson Transform |
| --- | --- | --- |
| **Triết lý** | Sửa giá trị của phần tử cá biệt (Cắt ngọn). | Thay đổi thang đo của toàn bộ hệ thống (Uốn cong). |
| **Hình dáng phân phối** | Giữ nguyên hình dáng cũ nhưng xuất hiện 2 cột biến tần suất cao ở 2 đầu biên. | Biến đổi hình dáng phân phối gốc tiến gần về phân phối hình chuông (Gaussian). |
| **Bảo toàn thông tin** | Mất đi thông tin về độ lớn chính xác của Outlier (chỉ biết nó vượt biên). | Giữ lại toàn bộ thông tin gốc, có thể đảo ngược quy trình (Inverse Transform) về dữ liệu ban đầu. |
| **Trường hợp áp dụng** | Khi bạn chắc chắn Outlier là nhiễu/lỗi nhập liệu và muốn triệt tiêu tầm ảnh hưởng của chúng. | Khi bản chất dữ liệu có phân phối lệch (ví dụ: thu nhập, lượng traffic) và mô hình ML yêu cầu đầu vào dạng chuẩn. |

# RobustScaler

Nếu **Winsorization** chọn cách "gọt giũa trực diện", **Yeo-Johnson** chọn cách "uốn cong không gian phân phối", thì **RobustScaler** lại tiếp cận bài toán theo triết lý: **"Sống chung với lũ nhưng không để lũ làm ảnh hưởng đến thước đo"**.

Đây là một kỹ thuật chuẩn hóa dữ liệu (Scaling) cực kỳ phổ biến trong Machine Learning, được sinh ra để thay thế cho `StandardScaler` hay `MinMaxScaler` khi tập dữ liệu của bạn chứa quá nhiều dị biệt.

---

## 1. Công thức Toán học của RobustScaler

Công thức biến đổi của RobustScaler cho từng điểm dữ liệu $x$ như sau:

$$x' = \frac{x - \text{median}(x)}{\text{IQR}(x)}$$

Trong đó:

* $\text{median}(x)$ (Trung vị): Giá trị nằm chính giữa tập dữ liệu khi đã sắp xếp theo thứ tự.
* $\text{IQR}$ (Interquartile Range - Khoảng tứ phân vị): Được tính bằng $Q_3 - Q_1$ (Giá trị ở phân vị 75% trừ đi giá trị ở phân vị 25%). Đây chính là khoảng không gian bao trọn 50% lượng dữ liệu tập trung ở vùng trung tâm.

---

## 2. Ý nghĩa toán học trong việc xử lý Outliers

Để hiểu tại sao nó "Robust" (mạnh mẽ/bền vững), hãy so sánh nó với người anh em chuẩn hóa quen thuộc là `StandardScaler` ($\frac{x - \text{mean}}{\text{std}}$):

### Miễn dịch với sự kéo lệch của tâm (Center Immunity)

`StandardScaler` dùng số Trung bình (Mean). Nếu bạn có 9 người thu nhập 10 triệu và 1 tỷ phú thu nhập 10 tỷ, Mean sẽ bị kéo vọt lên gần 1 tỷ. Phép trừ $(x - \text{mean})$ lúc này sẽ khiến dữ liệu của 9 người bình thường trở thành số âm rất lớn.
`RobustScaler` dùng Trung vị (Median). Trong ví dụ trên, Median vẫn loanh quanh mức 10 triệu. Cái bóng của outlier tỷ phú hoàn toàn không hề làm dịch chuyển cái "tâm" của thước đo.

### Thước đo khoảng cách không bị giãn nở ảo (Scale Immunity)

`StandardScaler` dùng Độ lệch chuẩn (Standard Deviation - $\sigma$). Vì $\sigma$ tính toán dựa trên bình phương khoảng cách từ các điểm đến Mean, một vài siêu Outlier sẽ đẩy $\sigma$ lên cực kỳ lớn. Khi chia cho một $\sigma$ khổng lồ, toàn bộ dữ liệu bình thường sẽ bị bóp nghẹt (squeezed) lại thành một cụm siêu nhỏ sát nhau, làm mất đi tính phân tách của feature.
`RobustScaler` chia cho $\text{IQR}$. Vì $\text{IQR}$ chỉ nhìn vào phân vị 25% và 75%, dù Outlier có tiến đến vô cùng thì $\text{IQR}$ vẫn giữ nguyên giá trị ổn định. Nhờ đó, khoảng cách giữa các dữ liệu bình thường được bảo toàn nguyên vẹn sau khi scale.

### Giữ lại hình dáng phân phối và Outlier gốc

Không giống như Winsorization (bóp chết outlier tại biên) hay Yeo-Johnson (nén khoảng cách outlier bằng hàm phi tuyến), RobustScaler là một **phép biến đổi tuyến tính** (Linear Transformation).

* Nó giữ nguyên hình dáng phân phối gốc (độ lệch, độ nhọn).
* Sau khi biến đổi, các dữ liệu "chuẩn" sẽ tập trung đẹp đẽ xung quanh khoảng $[-1, 1]$ hoặc $[-2, 2]$.
* Các Outlier không biến mất, chúng vẫn nằm xa tít tắp (ví dụ có giá trị sau scale là $15, 45, 100$), nhưng chúng không còn quyền năng làm tổn hại đến thang đo của các điểm dữ liệu khác.

---

## 3. Bức tranh toàn cảnh: Chọn phương pháp nào?

| Tiêu chí | Winsorization | Yeo-Johnson Transform | RobustScaler |
| --- | --- | --- | --- |
| **Bản chất phép toán** | Chặn biên (Clipped/Capped) | Phi tuyến (Power Transform) | Tuyến tính (Linear Translation & Scale) |
| **Outlier có còn là Outlier?** | **Không.** Bị ép thành giá trị biên. | **Còn**, nhưng khoảng cách tới tâm bị thu hẹp đáng kể. | **Còn nguyên.** Giữ nguyên khoảng cách tỉ lệ thuận ban đầu. |
| **Hình dáng phân phối** | Bị biến dạng ở hai đầu biên. | Thay đổi hoàn toàn (biến phân phối lệch thành phân phối chuẩn). | Giữ nguyên vẹn hình dáng (chỉ dịch tâm và đổi gốc tọa độ). |
| **Khi nào nên dùng?** | Khi biết chắc outlier là lỗi hoặc muốn triệt tiêu hoàn toàn nhiễu của chúng. | Khi thuật toán ML bắt buộc dữ liệu phải có phân phối chuẩn (Gaussian). | Khi muốn đưa dữ liệu về cùng một thang đo để chạy ML (KNN, SVM, Neural Network) nhưng không muốn các outlier làm mờ nhạt đi thông tin của dữ liệu bình thường. |