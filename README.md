# Mô hình hoá tứ giác trong hình học phẳng với Neo4j

Hệ thống tri thức nhận dạng tứ giác (Toán 8): các loại tứ giác, tính chất và **dấu hiệu nhận biết**
được lưu thành **đồ thị trong Neo4j**. Bộ suy luận tiến (forward chaining) viết bằng Cypher + Python
trả lời các câu hỏi dạng:

- *Hình bình hành có hai đường chéo vuông góc và bằng nhau là hình gì?* → **Hình vuông**
- *Hình thang có một cặp cạnh song song, cặp cạnh còn lại bằng nhau là hình gì?* → **chưa đủ dữ kiện**:
  là hình thang cân **hoặc** hình bình hành.

…kèm lời giải từng bước, sơ đồ phân cấp và phát hiện giả thiết mâu thuẫn.

Ngoài ra, mỗi hình có **công thức diện tích, chu vi và các công thức liên quan** (đường chéo, chiều cao,
đường trung bình, góc, bán kính đường tròn nội/ngoại tiếp) lưu trong Neo4j. Trang **Tính diện tích, chu vi**
cho nhập số liệu và tính ra kết quả kèm lời giải, đồng thời cảnh báo nếu số liệu không nhất quán.

Trang **Thử thách** là một trò chơi: người chơi kéo đỉnh, kéo cạnh hoặc kéo cả hình trên lưới ô vuông
(hoặc nhích từng ô bằng phím mũi tên) để tạo ra hình được yêu cầu. Có hai chế độ:

- **Theo vòng**: từ tứ giác thường lần lượt tạo hình thang → hình thang vuông → … → hình vuông.
- **Tự chọn đề**: chọn hình cho sẵn và hình cần tạo, ví dụ cho sẵn hình bình hành, kéo thành hình vuông.

Mỗi lần thả chuột, toạ độ được đổi thành các tính chất (song song, bằng nhau, góc vuông, đường chéo…) rồi
gửi cho bộ suy luận Neo4j. Neo4j kết luận đúng hình yêu cầu thì được cộng điểm; điểm được lưu vào Neo4j
(nút `:LuotChoi`) để hiện bảng xếp hạng. Khi chọn một đỉnh, bảng vẽ hiện đường gợi ý: đặt đỉnh lên đó sẽ có
cặp cạnh song song hoặc góc vuông.

Trang **Đồ thị tri thức** vẽ toàn bộ tri thức bằng hình ảnh: mỗi hình là một ô có hình vẽ, mỗi mũi tên đi từ
hình tổng quát xuống hình đặc biệt hơn và ghi điều kiện cần thêm (lấy từ các nút `:DauHieu`). Bấm vào điều
kiện để mở đề tương ứng trong trang Thử thách.

## Công nghệ

| Thành phần | Dùng |
|---|---|
| Cơ sở dữ liệu đồ thị | Neo4j 5 (Docker) |
| Ngôn ngữ truy vấn | Cypher |
| Backend + giao diện web | Python 3.10+, Flask |
| Kết nối | Neo4j Python Driver (giao thức Bolt) |

## Cài đặt nhanh

```bash
# 1. Chạy Neo4j (nếu chưa có)
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/matkhau123 -v neo4j_data:/data neo4j:latest
#    hoặc: docker compose up -d

# 2. Cài thư viện
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt

# 3. Cấu hình (sửa mật khẩu nếu khác)
copy .env.example .env          # macOS/Linux: cp .env.example .env

# 4. Nạp tri thức vào Neo4j
python -m src.seed

# 5. Chạy web
python app.py                   # mở http://localhost:5000
```

Trên Windows có thể chạy gộp bước 2–5 bằng `.\run.ps1`.

Không muốn dùng Python? Dán `cypher/seed.cypher` vào Neo4j Browser (http://localhost:7474) để tạo đồ thị,
rồi thử các câu trong `cypher/queries.cypher`.

## Đưa lên web (chạy 24/7, miễn phí)

```
Trình duyệt  ──►  Render (Flask + gunicorn)  ──Bolt──►  Neo4j AuraDB Free
```

**Bước 1 – Tạo Neo4j trên cloud (AuraDB Free)**

1. Vào <https://console.neo4j.io>, đăng nhập (dùng tài khoản Google được).
2. Bấm **New instance** → chọn gói **AuraDB Free** → **Create**.
3. Bấm **Download** để tải file `Neo4j-xxxxxxxx-Created-....txt`. File này chứa `NEO4J_URI`,
   `NEO4J_USERNAME`, `NEO4J_PASSWORD`. Mật khẩu chỉ hiện **một lần**, nên phải lưu lại.
4. Chờ instance chuyển sang trạng thái **Running** (vài phút).

**Bước 2 – Đưa mã nguồn lên GitHub** (`git add .`, `git commit`, `git push`). Không đưa file `.env` lên.

**Bước 3 – Tạo Web Service trên Render**

1. Vào <https://render.com>, đăng ký bằng tài khoản GitHub.
2. **New → Web Service** → chọn repository của dự án.
3. Điền các ô:

   | Ô | Giá trị |
   |---|---|
   | Language | Python 3 |
   | Branch | main |
   | Region | Singapore (gần Việt Nam nhất) |
   | Build Command | `pip install -r requirements.txt && python -m src.seed --neu-can` |
   | Start Command | `gunicorn app:app` |
   | Instance Type | **Free** |

4. Mục **Environment Variables**: thêm 3 biến, chép giá trị từ file `.txt` ở bước 1:
   `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`.
5. Bấm **Deploy Web Service**. Trong log build sẽ thấy “Đã nạp tri thức vào Neo4j…”. Khi báo **Live**,
   web chạy ở địa chỉ dạng `https://ten-dich-vu.onrender.com`.

Ở bước build, lệnh `python -m src.seed --neu-can` tự nạp tri thức vào Aura. Lệnh chỉ nạp lại khi chưa có
dữ liệu hoặc khi `data/knowledge.py`, `data/cong_thuc.py` thay đổi. Điểm của trò chơi Thử thách được giữ nguyên.

**Bước 4 – Giữ web luôn chạy (nên làm)**

Gói miễn phí có hai giới hạn:

- Render cho web “ngủ” sau 15 phút không có ai truy cập. Lần mở sau phải chờ khoảng 1 phút.
- AuraDB Free tự tạm dừng (Paused) sau 3 ngày không có truy vấn. Khi đó vào console.neo4j.io bấm Resume.

Cách xử lý: tạo một monitor miễn phí ở <https://uptimerobot.com> (gói Free dành cho mục đích cá nhân,
phi thương mại), loại **HTTP(s)**, URL `https://ten-dich-vu.onrender.com/suc-khoe`, kiểm tra **5 phút/lần**.
Trang `/suc-khoe` truy vấn Neo4j nên giữ được cả web lẫn Neo4j luôn hoạt động. Nếu một trong hai bị lỗi,
UptimeRobot sẽ gửi email báo. Mỗi tháng Render cho 750 giờ miễn phí, đủ để **một** web chạy suốt tháng.

**Cập nhật về sau:** sửa code → `git push`, Render tự build và chạy lại bản mới.

## Cấu trúc thư mục

```
data/knowledge.py      Cơ sở tri thức: hình, tính chất, dấu hiệu nhận biết, ví dụ
data/cong_thuc.py      Đại lượng và công thức diện tích, chu vi, liên quan
src/seed.py            Nạp tri thức vào Neo4j / xuất file seed.cypher
src/engine.py          Bộ suy luận tiến (các câu Cypher suy luận)
src/tinh_toan.py       Bộ tính diện tích, chu vi từ công thức trong Neo4j
src/hinh_hoc.py        Tính chất tứ giác từ toạ độ, sinh hình mẫu (trang Thử thách)
src/so_do_tri_thuc.py  Vẽ đồ thị tri thức bằng hình ảnh, mũi tên ghi điều kiện
src/hinh_ve.py         Hình vẽ minh hoạ từng loại hình
src/repo.py            Các câu Cypher tra cứu cho giao diện
src/svg.py             Vẽ sơ đồ phân cấp
app.py                 Ứng dụng web Flask
gunicorn.conf.py       Cấu hình chạy trên máy chủ web (Render)
templates/, static/    Giao diện
cypher/                seed.cypher, queries.cypher
tests/                 Kiểm thử tự động (python -m unittest discover tests)
```

## Mô hình đồ thị

```
(:Hinh)-[:LA_MOT]->(:Hinh)                 hình vuông LÀ MỘT hình thoi
(:Hinh)-[:CO_TINH_CHAT]->(:TinhChat)       tính chất luôn đúng của hình
(:DauHieu)-[:AP_DUNG_CHO]->(:Hinh)         luật: nếu là hình X ...
(:DauHieu)-[:CAN]->(:TinhChat)             ... và có các tính chất P ...
(:DauHieu)-[:KET_LUAN]->(:Hinh)            ... thì là hình Y
(:TinhChat)-[:MAU_THUAN]->(:TinhChat)      hai tính chất không thể cùng đúng
(:Hinh)-[:CO_DAI_LUONG]->(:DaiLuong)       đại lượng của hình (a, d₁, h, S, P…)
(:Hinh)-[:CO_CONG_THUC]->(:CongThuc)       công thức của hình
(:CongThuc)-[:CAN_BIEN]->(:DaiLuong)       biến đầu vào
(:CongThuc)-[:TINH_RA]->(:DaiLuong)        biến kết quả
(:LuotChoi)-[:HOAN_THANH]->(:Hinh)         lượt chơi Thử thách đã tạo đúng hình nào
```

Dữ liệu: 9 hình, 17 tính chất, 26 dấu hiệu (25 luật kết luận + 1 luật gợi ý), 5 cặp mâu thuẫn,
71 đại lượng, 68 công thức.
Nút `:LuotChoi` được tạo khi người chơi lưu điểm ở trang Thử thách (không cần nạp lại dữ liệu). Hệ thống chỉ giữ
2000 lượt chơi điểm cao nhất. Nút `:PhienBan` ghi dấu vân tay của bộ tri thức đã nạp.

## Thêm tri thức mới

Sửa `data/knowledge.py` (ví dụ thêm một dấu hiệu vào `DAU_HIEU`) hoặc `data/cong_thuc.py` (thêm công thức), rồi chạy lại `python -m src.seed`.
Trang Đồ thị tri thức tự vẽ lại mũi tên và điều kiện theo dữ liệu mới.
