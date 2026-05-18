# IQR Trimming - Group C
## 1. Kỹ thuật Tukey IQR Fences Trimming là gì?

**Tukey IQR Fences** (hay còn gọi là phương pháp Hàng rào Tukey) là một kỹ thuật thống kê mạnh mẽ (robust) được dùng để phát hiện các giá trị ngoại lai (outliers) dựa trên **Khoảng biến phân tứ phân vị (Interquartile Range - IQR)**.

Kỹ thuật này thiết lập hai "hàng rào" (fences) để xác định ranh giới của dữ liệu bình thường:

* **Khoảng tứ phân vị ($IQR$):** Được tính bằng hiệu số giữa Tứ phân vị thứ 3 ($Q_3$ - 75th percentile) và Tứ phân vị thứ 1 ($Q_1$ - 25th percentile).

$$IQR = Q_3 - Q_1$$


* **Hàng rào dưới (Lower Fence):**

$$\text{Lower Fence} = Q_1 - 1.5 \times IQR$$


* **Hàng rào trên (Upper Fence):**

$$\text{Upper Fence} = Q_3 + 1.5 \times IQR$$



> *Lưu ý:* Hệ số `1.5` là tiêu chuẩn của Tukey cho các ngoại lai thông thường (mild outliers). Trong một số trường hợp cực đoan hơn, hệ số `3.0` sẽ được sử dụng (extreme outliers).

**Trimming (Xóa bỏ/Cắt tỉa):** Khi một hàng dữ liệu chứa giá trị nằm ngoài hai hàng rào này ($x < \text{Lower Fence}$ hoặc $x > \text{Upper Fence}$), kỹ thuật Trimming sẽ **xóa bỏ hoàn toàn hàng đó** ra khỏi tập dữ liệu, thay vì giữ lại và sửa đổi nó.

---

## 2. Lý giải tính chất qua đoạn trích: "Why delete rows instead of capping?"

Đoạn trích bạn đưa ra giải thích rất chính xác lý do tại sao trong bối cảnh này, việc **Trimming (Xóa bỏ)** lại tối ưu và đúng đắn hơn hoàn toàn so với **Capping (Cắt cụp/Winsorization)**. Nó thể hiện rõ các tính chất bản chất của dữ liệu và bản chất của nhiễu:

### Tính chất 1: Sự phù hợp lý tưởng với phân phối đối xứng và gần chuẩn (Symmetric & Near-Gaussian)

* **Bối cảnh:** Dữ liệu của `Group C` có dạng hình chuông cân đối. Trong một phân phối chuẩn hoàn hảo, khoảng Tukey ($Q_1 - 1.5 \times IQR$ đến $Q_3 + 1.5 \times IQR$) sẽ bao phủ khoảng **99.3%** lượng dữ liệu.
* **Ý nghĩa:** Điều này đồng nghĩa với việc xác suất một dữ liệu "sạch" rơi ra ngoài hàng rào là cực kỳ thấp (chỉ khoảng 0.7%). Do đó, các điểm nằm ngoài hàng rào Tukey trong trường hợp này có độ tin cậy rất cao là các dị thường thực sự, chứ không phải do biến động tự nhiên của một phân phối lệch (skewed).

### Tính chất 2: Bản chất của Outlier là "Nhiễu hệ thống" chứ không phải "Biến dị tự nhiên"

* **Bối cảnh:** Đoạn trích nhấn mạnh các giá trị cực đoan là *lỗi đo lường (measurement errors)* hoặc *nhiễu thiết bị (device noise)* — tức là những quan sát bị hỏng hoàn toàn (corrupted), không phải là ngoại lai mang tính sinh học (biological outliers).
* **Ý nghĩa:**
* Nếu đó là ngoại lai sinh học (ví dụ: một người cao 2m3 trong một nghiên cứu về chiều cao), giá trị đó **có thật** và mang thông tin.
* Nhưng vì đây là nhiễu thiết bị (ví dụ: cảm biến bị chập mạch trả về giá trị sai lệch hoàn toàn), các con số này **không chứa bất kỳ giá trị thông tin nào** về bản chất của đối tượng nghiên cứu. Chúng là "rác" (garbage).



### Tính chất 3: Tác hại của Capping đối với dữ liệu lỗi

* **Capping (Cập biên)** là phương pháp kéo các giá trị ngoại lai về bằng giá trị của Hàng rào trên hoặc Hàng rào dưới.
* Nếu áp dụng Capping vào đây, bạn đang giữ lại các dòng dữ liệu bị lỗi và ép chúng "đóng giả" làm các giá trị biên hợp lệ. Điều này vô tình tạo ra một cụm dữ liệu nhân tạo (artificial spike) ngay tại các đường biên, làm biến dạng dạng hình chuông (Gaussian) nguyên bản, gây sai lệch nghiêm trọng cho các phép toán thống kê phía sau như tính Trung bình (Mean) và Phương sai (Variance).

---

## Tóm lại

Việc chọn **Tukey IQR Fences Trimming** trong trường hợp này thể hiện một tư duy xử lý dữ liệu chuẩn xác: **"Rác thì phải vứt vào thùng rác (Trimming), chứ không thể tái chế rác thành một điểm dữ liệu cận biên (Capping)."** Khi phân phối đã gần chuẩn và ngoại lai được xác định là nhiễu kỹ thuật, xóa bỏ chúng là cách duy nhất để trả lại sự thuần khiết nguyên bản cho tập dữ liệu.

# Physical Unit Mormalization

Dựa trên hình ảnh bạn cung cấp, đây là kỹ thuật **Chuẩn hóa số đo theo độ phóng đại (Magnification-aware conversion)** nhằm chuyển đổi các đơn vị đo từ pixel ($px$) sang đơn vị vật lý thực tế (micromet - $\mu m$).

Dưới đây là ý nghĩa chi tiết và lập luận toán học đứng sau hai công thức này:

---

## 1. Ý nghĩa của việc biến đổi

Trong xử lý ảnh y sinh (như ảnh chụp tế bào qua kính hiển vi), các bức ảnh có thể được chụp ở các độ phóng đại khác nhau (ví dụ: $40\times, 100\times$). Điều này dẫn đến một vấn đề: **Pixel là một đơn vị phụ thuộc vào thiết bị và cấu hình chụp.**

* **Loại bỏ sự phụ thuộc vào thiết bị:** Một tế bào có kích thước thực tế không đổi, nhưng nếu chụp ở độ phóng đại $100\times$ nó sẽ chiếm nhiều pixel hơn rất nhiều so với khi chụp ở độ phóng đại $40\times$.
* **Tạo tính đồng nhất cho dữ liệu (Comparability):** Việc biến đổi này giúp đưa tất cả các đặc trưng (diện tích, chu vi) của toàn bộ tế bào trong tập dữ liệu về cùng một hệ quy chiếu vật lý thực ($\mu m$ hoặc $\mu m^2$). Sau khi chuyển đổi, bạn có thể so sánh trực tiếp tế bào ở ảnh này với tế bào ở ảnh khác mà không sợ bị sai lệch do độ phóng đại của kính hiển vi.

---

## 2. Lập luận toán học đằng sau công thức

Lập luận toán học của phương pháp này dựa trên **Hình học đồng dạng (Geometric Scaling)** và **Thứ nguyên (Dimensionality)** của các đại lượng đo lường khi một vật thể được phóng đại lên $k$ lần (với $k = \text{magnification\_x}$).

### Đối với Chu vi (True Perimeter) - Không gian 1 chiều ($1D$)

Chu vi là một đại lượng đo chiều dài (tuyến tính - tuyến 1 chiều).

* **Lập luận:** Khi bạn phóng đại một hình ảnh lên $k$ lần, mọi kích thước chiều dài (bề rộng, chiều cao, đường biên) của vật thể trên ảnh pixel cũng sẽ tăng lên tuyến tính đúng $k$ lần.

$$\text{perimeter\_px} = \text{true\_perimeter} \times \text{magnification\_x}$$


* **Công thức đảo:** Để tìm lại chiều dài thực tế ban đầu, ta chỉ cần chia số pixel đo được cho hệ số phóng đại:

$$\text{true\_perimeter} = \frac{\text{perimeter\_px}}{\text{magnification\_x}}$$



### Đối với Diện tích (True Area) - Không gian 2 chiều ($2D$)

Diện tích là đại lượng hình học hai chiều (chiều dài $\times$ chiều rộng).

* **Lập luận:** Theo nguyên lý hình học đồng dạng, nếu các cạnh của một hình tăng lên $k$ lần thì diện tích của hình đó sẽ tăng lên $k^2$ lần (bình phương hệ số phóng đại). Vì ảnh được phóng đại đều theo cả trục $X$ và trục $Y$, nên số lượng pixel bao phủ tế bào sẽ tăng theo hàm mũ 2.

$$\text{cell\_area\_px} = \text{true\_area} \times (\text{magnification\_x})^2$$


* **Công thức đảo:** Để đưa diện tích pixel về diện tích thực tế, ta phải chia cho bình phương của độ phóng đại:

$$\text{true\_cell\_area} = \frac{\text{cell\_area\_px}}{(\text{magnification\_x})^2}$$



---

## Ví dụ minh họa từ ảnh:

Giả sử có một tế bào thực tế cố định.

* Nếu chụp ở độ phóng đại **$40\times$**, diện tích của nó trên ảnh là $1,600 \text{ px}^2$. Diện tích thực quy đổi: $\frac{1600}{40^2} = 1$ đơn vị thực.
* Nếu chụp ở độ phóng đại **$100\times$**, do phóng to hơn nên nó chiếm tới $10,000 \text{ px}^2$ trên ảnh. Diện tích thực quy đổi: $\frac{10000}{100^2} = 1$ đơn vị thực.

Nhờ phép biến đổi này, mô hình học máy hoặc thuật toán thống kê của bạn sẽ hiểu rằng cả hai bức ảnh trên đang mô tả các tế bào có **cùng một kích thước thực tế**, tránh việc mô hình bị đánh lừa bởi độ phóng đại của kính hiển vi.

# Staining Protocol Shifting

Hình ảnh bạn cung cấp mô tả kỹ thuật **Group-wise mean shift** (Dịch chuyển giá trị trung bình theo từng nhóm giao thức nhuộm). Đây là một phương pháp chuẩn hóa dữ liệu hình ảnh cực kỳ phổ biến trong y sinh để xử lý **Hiệu ứng mẻ/giao thức (Batch effects / Protocol bias)**.

Dưới đây là ý nghĩa và lập luận toán học chi tiết đứng sau phép biến đổi này:

---

## 1. Ý nghĩa của việc biến đổi

Trong giải phẫu bệnh hoặc nghiên cứu tế bào, các mẫu mô/tế bào thường được nhuộm bằng các hóa chất khác nhau (ví dụ: nhuộm Giemsa hoặc nhuộm Wright). Do đặc tính hóa học, mỗi giao thức nhuộm sẽ tạo ra một tông màu nền và độ đậm nhạt khác nhau cho bức ảnh, dù bản chất sinh học của các tế bào là như nhau.

Việc biến đổi này mang 3 ý nghĩa cốt lõi:

* **Loại bỏ nhiễu hệ thống (Staining Protocol Bias):** Phép toán này loại bỏ sự khác biệt về màu sắc do "kỹ thuật nhuộm" gây ra, giúp mô hình tập trung vào "bản chất sinh học" thực sự của tế bào (true hue).
* **Tránh làm sai lệch các đặc trưng phái sinh (Feature Engineering):** Như slide có giải thích, nếu bạn tính các tỷ lệ màu sắc như $R / (R + G + B)$ ngay trên ảnh gốc, sai lệch màu của giao thức nhuộm sẽ bị lồng ghép vào đặc trưng đó và làm sai lệch kết quả. Biến đổi này làm sạch màu sắc trước khi trích xuất đặc trưng.
* **Đảm bảo tính nhất quán nhưng bảo tồn đa dạng sinh học:** Nó chỉ loại bỏ khoảng cách khác biệt giữa các giao thức nhuộm (between-protocol offset), nhưng **giữ nguyên vẹn** sự khác biệt giữa các tế bào trong cùng một giao thức (within-protocol variance). Tế bào có bệnh vẫn sẽ hiển thị khác tế bào khỏe mạnh.

---

## 2. Lập luận toán học đằng sau công thức

Phép biến đổi được thực hiện độc lập cho từng kênh màu $c \in \{R, G, B, \text{intensity}\}$ dựa trên công thức:

$$x_{\text{shifted}} = x - \mu_c^{(p)} + \mu_c^{\text{global}}$$

Lập luận toán học ở đây dựa trên **Mô hình cộng tính (Additive Model)** của sai số và **Tính chất tuyến tính của phép tịnh tiến**.

Để làm rõ sự mơ hồ này, chúng ta sẽ cùng nhau đặt phương pháp này vào một **mô hình toán học thống kê** cụ thể. Khi viết tường minh các thành phần dưới dạng phương trình, bạn sẽ thấy bản chất của phép toán này thực chất là một trò chơi "bóc tách và tịnh tiến" vector rất đẹp mắt.

---

## 1. Thiết lập Mô hình Toán học (Additive Bias Model)

Giả sử giá trị màu sắc quan sát được tại một pixel là $x$. Trong thực tế thống kê, giá trị $x$ này được cấu thành từ 2 thành phần độc lập:

1. **$s$ (Signal):** Tín hiệu sinh học thực sự của tế bào (đây là cái ta muốn giữ lại). Giả sử dữ liệu sạch $s$ này có giá trị trung bình lý thuyết là $\mu_s$.
2. **$b^{(p)}$ (Bias):** Sai số hệ thống do giao thức nhuộm $p$ gây ra (đây là "nhiễu" ta muốn xóa bỏ). Sai số này là **cố định** cho mọi bức ảnh dùng chung giao thức $p$.

Mối quan hệ này được biểu diễn bằng mô hình cộng tính (Additive Model):


$$x = s + b^{(p)}$$

Bây giờ, ta hãy xem kỳ vọng (giá trị trung bình) của các đại lượng này hoạt động ra sao.

---

## 2. Chứng minh bước 1: Group-wise Mean Centering (Trừ đi trung bình nhóm)

Mục tiêu của bước này là **cô lập và triệt tiêu** hoàn toàn hằng số nhiễu $b^{(p)}$ của riêng nhóm $p$.

Đầu tiên, ta tính giá trị trung bình của nhóm $p$ (Ký hiệu là $\mu_c^{(p)}$ hoặc toán tử kỳ vọng $\mathbb{E}[x \mid p]$):


$$\mu_c^{(p)} = \mathbb{E}[x \mid p] = \mathbb{E}[s + b^{(p)} \mid p]$$

Do tính chất tuyến tính của kỳ vọng [_LyGiai_](LinearityOfExpectation.md), và vì $b^{(p)}$ là hằng số đối với nhóm $p$, ta có:


$$\mu_c^{(p)} = \mathbb{E}[s \mid p] + b^{(p)}$$

*Giả định hợp lý:* [GiaDinh](ReasonableAssumption.md) Giả sử các mẫu tế bào được phân phối ngẫu nhiên vào các mẻ nhuộm (không có chuyện mẻ $p$ chỉ toàn tế bào kích thước to, mẻ $q$ toàn tế bào nhỏ). Do đó, trung bình sinh học của nhóm $p$ cũng chính là trung bình sinh học toàn cục: $\mathbb{E}[s \mid p] = \mu_s$.

Suy ra:


$$\mu_c^{(p)} = \mu_s + b^{(p)}$$

Bây giờ, thực hiện phép toán **Group-wise Mean Centering** bằng cách lấy giá trị quan sát trừ đi trung bình nhóm:


$$\text{Centering} = x - \mu_c^{(p)}$$

$$\text{Centering} = (s + b^{(p)}) - (\mu_s + b^{(p)})$$

$$\text{Centering} = s - \mu_s$$

> **Ý nghĩa toán học 1:** Hãy nhìn vào kết quả $(s - \mu_s)$. Nhiễu hệ thống $b^{(p)}$ đã **bị triệt tiêu hoàn toàn**! Lúc này, phân phối của tất cả các nhóm (dù là Giemsa hay Wright) đều bị kéo về một trục tọa độ mới có **giá trị trung bình bằng 0**.

---

## 3. Chứng minh bước 2: Global Re-centering (Cộng lại trung bình toàn cục)

Sau bước 1, dữ liệu đã sạch nhiễu nhưng trung bình lại bằng 0 (xuất hiện nhiều giá trị âm, không đúng với thực tế kênh màu $R, G, B$ vốn mang giá trị dương). Ta cần đưa chúng về lại hệ quy chiếu ban đầu của ảnh.

Ta tính toán giá trị trung bình toàn cục (Global Mean) trên toàn bộ tập dữ liệu (gồm nhiều giao thức khác nhau):


$$\mu_c^{\text{global}} = \mathbb{E}[x] = \mathbb{E}[s + b^{(p)}] = \mathbb{E}[s] + \mathbb{E}[b^{(p)}]$$

$$\mu_c^{\text{global}} = \mu_s + \bar{b}$$


*(Trong đó $\bar{b}$ là sai số trung bình của tất cả các giao thức nhuộm gộp lại).*

Bây giờ, ta thực hiện toàn bộ công thức dịch chuyển:


$$x_{\text{shifted}} = \underbrace{(x - \mu_c^{(p)})}_{\text{Bước 1: Centering}} + \underbrace{\mu_c^{\text{global}}}_{\text{Bước 2: Re-centering}}$$

Thay các kết quả đã chứng minh ở trên vào:


$$x_{\text{shifted}} = (s - \mu_s) + (\mu_s + \bar{b})$$

$$x_{\text{shifted}} = s + \bar{b}$$

> **Ý nghĩa toán học 2:** Công thức cuối cùng chỉ còn lại $s$ (tín hiệu gốc) và $\bar{b}$ (một hằng số chung cho toàn bộ tập dữ liệu). Lúc này, tất cả các điểm dữ liệu thuộc mọi nhóm giao thức đều có chung một mức nền sai số như nhau ($\bar{b}$). Sự khác biệt giữa các nhóm (between-protocol offset) đã hoàn toàn biến mất.

---

## 4. Chứng minh toán học: Tại sao phương sai không đổi?

Một phương pháp chuẩn hóa tồi là phương pháp làm bóp méo hình dạng phân phối (phương sai) của dữ liệu gốc. Hãy chứng minh phương pháp Mean Shift này **bảo toàn nguyên vẹn cấu trúc dữ liệu** nội bộ của từng nhóm.

Ta tính phương sai (Variance) của dữ liệu sau khi dịch chuyển trong nhóm $p$:


$$\text{Var}(x_{\text{shifted}} \mid p) = \text{Var}(x - \mu_c^{(p)} + \mu_c^{\text{global}} \mid p)$$

Trong một nhóm $p$ cụ thể, cả $\mu_c^{(p)}$ và $\mu_c^{\text{global}}$ đều là những **hằng số** đã được tính toán cố định từ trước. Theo tính chất cơ bản của toán tử phương sai: $\text{Var}(X + \text{hằng số}) = \text{Var}(X)$.

Do đó:


$$\text{Var}(x_{\text{shifted}} \mid p) = \text{Var}(x \mid p)$$

## Tóm tắt bản chất bằng hình học

Nếu bạn coi tập dữ liệu của mỗi giao thức nhuộm là một "đám mây điểm" trên không gian:

1. **Group-wise Mean Centering:** Nhấc trọng tâm của tất cả các đám mây điểm đó, đặt trùng khít vào gốc tọa độ $O(0,0)$. Hành động này xóa bỏ khoảng cách lệch giữa các đám mây.
2. **Global Re-centering:** Bê nguyên cả cụm các đám mây đang trùng nhau ở gốc tọa độ đó, tịnh tiến đến vị trí trọng tâm toàn cục $\mu^{\text{global}}$.

Kết quả là các đám mây hòa vào làm một, phân phối đồng nhất với nhau, không còn phân biệt ảnh này được nhuộm bằng phương pháp nào nữa, nhưng hình dáng từng đám mây (phương sai - thông tin sinh học) thì không hề bị bóp méo.

# Form Factor

## 1. Ý nghĩa Hình thái và Sinh học của Form Factor

Chỉ số này đóng vai trò như một thước đo để phân loại cấu trúc hình học của tế bào:

* **Giá trị bằng $1.0$ (Tối đa):** Đại diện cho một **hình tròn hoàn hảo**. Trong y sinh, đây thường là dấu hiệu của các tế bào có hình thái bình thường, khỏe mạnh (normal morphology).
* **Giá trị càng nhỏ (< 1.0):** Thể hiện hình dạng tế bào càng méo mó, xù xì hoặc kéo dài.
* **Elongated:** Tế bào bị kéo dẹt thành hình bầu dục hoặc hình thoi.
* **Lobulated:** Tế bào bị phân thành nhiều thùy (giống như nhân của tế bào bạch cầu).
* **Membrane-deformed:** Màng tế bào bị biến dạng, gồ ghề, không đều.
* Trong phân tích y sinh, các giá trị thấp này thường là tín hiệu cảnh báo tế bào bị biến đổi cấu trúc hoặc nhiễm bệnh (**abnormal**).


---

## 2. Lập luận Toán học đằng sau công thức

Công thức toán học của Form Factor được định nghĩa là:

$$\text{Form\_Factor} = \frac{4\pi \times \text{true\_cell\_area}}{\text{true\_perimeter}^2}$$

Công thức này bắt nguồn trực tiếp từ **Bất đẳng thức đẳng chu (Isoperimetric Inequality)** trong hình học phẳng. Bất đẳng thức này phát biểu rằng: *Trong tất cả các hình hình học đóng có cùng một chu vi, hình tròn là hình có diện tích lớn nhất. Ngược lại, với một diện tích cố định, hình tròn có chu vi ngắn nhất.*

### Chứng minh tại sao hình tròn có Form Factor = 1:

Gọi một hình tròn có bán kính là $R$.

* Diện tích hình tròn: $A = \pi R^2$
* Chu vi hình tròn: $P = 2\pi R \implies P^2 = 4\pi^2 R^2$

Thay $A$ và $P^2$ của hình tròn vào công thức Form Factor:


$$\text{Form\_Factor} = \frac{4\pi \times (\pi R^2)}{4\pi^2 R^2} = \frac{4\pi^2 R^2}{4\pi^2 R^2} = 1$$

### Đối với các hình khác hình tròn:

Khi một tế bào bị kéo dài hoặc màng tế bào trở nên xù xì (phức tạp), **chu vi ($P$) của nó sẽ tăng lên rất nhanh** trong khi diện tích ($A$) tăng không đáng kể hoặc giữ nguyên.

Do chu vi $P$ nằm ở mẫu số và lại bị bình phương ($P^2$), nên khi chu vi tăng lên, giá trị của phân số sẽ giảm mạnh xuống dưới $1.0$. Hình dạng càng xa rời hình tròn (càng phức tạp, càng nhiều góc cạnh/nếp nhăn), mẫu số càng lớn, khiến chỉ số Form Factor càng tiến dần về $0$.

---

## 3. Đặc tính Bất biến với Độ phóng đại (Magnification-invariant)

Slide của bạn có nhấn mạnh một ý quan trọng: Chỉ số này được tính từ `true_cell_area` và `true_perimeter` (các giá trị đã được quy đổi sang đơn vị vật lý thực tế $\mu m$ ở bước trước), chứ không tính từ số lượng pixel thô.

Tuy nhiên, về mặt bản chất toán học, **Form Factor là một đại lượng không thứ nguyên (dimensionless)**:

* Đơn vị của Diện tích là diện tích thực ($\mu m^2$).
* Đơn vị của Chu vi bình phương cũng là diện tích thực ($(\mu m)^2 = \mu m^2$).

Do tử số và mẫu số triệt tiêu đơn vị cho nhau, biến Form Factor hoàn toàn độc lập với việc ảnh phóng to hay thu nhỏ. Nó là một đặc trưng hình học thuần túy của bản thân tế bào, giúp mô hình AI có thể so sánh hình dạng tế bào một cách công bằng trên mọi kính hiển vi có độ phóng đại khác nhau.

# Size Anomaly

Biến **Size Anomaly** (Bất thường về kích thước) trong công thức này thể hiện một kỹ thuật toán học được gọi là **Chuẩn hóa theo ngữ cảnh cá thể (Patient-specific Normalization / Contextual Scaling)**.

Thay vì đánh giá kích thước tế bào một cách độc lập trên toàn bộ tập dữ liệu, công thức này dịch chuyển hệ quy chiếu toán học từ không gian tuyệt đối sang không gian tương đối của riêng bệnh nhân đó.

---

## 1. Ý nghĩa Toán học: Khử biến nhiễu nền (Confounding Variable Elimination)

Trong thống kê, đặc điểm sinh học của từng bệnh nhân (như tuổi tác, giới tính, tình trạng sức khỏe nền) là một **biến nhiễu (confounding variable)** lớn.

* Một tế bào có đường kính $12\ \mu\text{m}$ có thể là hoàn toàn bình thường ở Bệnh nhân A (người vốn có các tế bào nền to).
* Nhưng cũng là $12\ \mu\text{m}$ đó, nó lại là một sự đột biến khổng lồ ở Bệnh nhân B (người có tế bào nền rất nhỏ, khoảng $7\ \mu\text{m}$).

Nếu đưa trực tiếp biến nguyên bản `cell_diameter_um` vào mô hình máy học, mô hình sẽ bị bối rối và có thể phân loại sai do sự chồng lấn phân phối giữa các bệnh nhân.

Bằng cách lập tỷ số:


$$\text{size\_anomaly} = \frac{\text{cell\_diameter\_um}}{\text{mcv\_fl}}$$

Mô hình toán học đã thực hiện phép **tính tỷ lệ (Scaling)** để triệt tiêu đặc tính nền của bệnh nhân. Giá trị đầu ra không còn đơn thuần là "đường kính bao nhiêu" nữa, mà là **"tế bào này lớn gấp bao nhiêu lần so với mức trung bình của chính cơ thể họ"**.

---

## 2. Phân tích Thứ nguyên (Dimensional Analysis) và Tính phi tuyến tính

Một điểm cực kỳ thú vị và thông minh về mặt toán học trong công thức này nằm ở sự kết hợp giữa hai không gian thứ nguyên khác nhau:

* **Tử số (`cell_diameter_um`):** Là một đại lượng hình học **1 chiều (1D)** – Đo chiều dài ($\mu\text{m}$).
* **Mẫu số (`mcv_fl`):** MCV (Mean Corpuscular Volume) là thể tích trung bình của hồng cầu, đây là đại lượng **3 chiều (3D)** – Đo thể tích ($1\text{ fL} = 1\ \mu\text{m}^3$).

### Hệ quả toán học của việc chia $1D$ cho $3D$:

Nếu mục tiêu chỉ là lập tỷ lệ đồng dạng thuần túy về mặt chiều dài, người ta sẽ dùng căn bậc ba của MCV ($\sqrt[3]{\text{MCV}}$). Tuy nhiên, việc giữ nguyên `mcv_fl` ở mẫu số tạo ra một hiệu ứng toán học có chủ đích: **Sự khuếch đại phi tuyến tính đối với các trường hợp bệnh lý nghiêm trọng.**

Xét hai trường hợp:

1. **Bệnh nhân bị thiếu máu hồng cầu nhỏ (Microcytic anemia):** Chỉ số $\text{mcv\_fl}$ của họ rất thấp (mẫu số nhỏ). Khi cơ thể họ xuất hiện một tế bào bất thường (như nguyên bào - blast), tử số tăng lên, mẫu số lại nhỏ $\rightarrow$ Chỉ số `size_anomaly` sẽ **tăng vọt lên cực kỳ cao (tăng theo hàm mũ so với tuyến tính)**.
2. **Bệnh nhân có thể trạng hồng cầu to (Macrocytic):** Mẫu số lớn sẽ tự động "ghìm" bớt chỉ số này xuống, tránh việc mô hình AI phát báo động giả (False Positive) khi thấy một tế bào hơi to một chút nhưng thực ra là do thể trạng của bệnh nhân đó vốn thế.

---

## 3. Ý nghĩa trong bài toán Phát hiện ngoại lai (Anomaly Detection)

Trong phân tích máu, các tế bào như **Blasts** (nguyên bào ác tính trong bệnh máu trắng) hoặc **Macrophages** (đại thực bào) có kích thước khổng lồ so với hồng cầu bình thường.

Về mặt thống kê, công thức này biến bài toán từ **Phát hiện ngoại lai toàn cục (Global Outlier Detection)** thành **Phát hiện ngoại lai theo ngữ cảnh (Contextual Outlier Detection)**.

Nó cô lập phần phân phối dữ liệu "bình thường" của từng bệnh nhân về quanh một mức sàn chung, và đẩy các tế bào bệnh lý (Blasts, Macrophages) ra hẳn rìa ngoài của phân phối (đuôi phân phối - heavy tails), giúp các thuật toán phân lớp phía sau dễ dàng nhận diện ra chúng một cách chính xác tuyệt đối.