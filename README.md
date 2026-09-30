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

## Cấu trúc thư mục

```
data/knowledge.py      Cơ sở tri thức: hình, tính chất, dấu hiệu nhận biết, ví dụ
data/cong_thuc.py      Đại lượng và công thức diện tích, chu vi, liên quan
src/seed.py            Nạp tri thức vào Neo4j / xuất file seed.cypher
src/engine.py          Bộ suy luận tiến (các câu Cypher suy luận)
src/tinh_toan.py       Bộ tính diện tích, chu vi từ công thức trong Neo4j
src/hinh_ve.py         Hình vẽ minh hoạ từng loại hình
src/repo.py            Các câu Cypher tra cứu cho giao diện
src/svg.py             Vẽ sơ đồ phân cấp
app.py                 Ứng dụng web Flask
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
```

Dữ liệu: 9 hình, 17 tính chất, 26 dấu hiệu (25 luật kết luận + 1 luật gợi ý), 5 cặp mâu thuẫn,
71 đại lượng, 68 công thức.

## Thêm tri thức mới

Sửa `data/knowledge.py` (ví dụ thêm một dấu hiệu vào `DAU_HIEU`) hoặc `data/cong_thuc.py` (thêm công thức), rồi chạy lại `python -m src.seed`.
