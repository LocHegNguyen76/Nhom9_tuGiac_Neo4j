"""Các truy vấn tra cứu tri thức trên Neo4j (dùng cho giao diện web)."""

Q_DS_HINH = "MATCH (h:Hinh) RETURN h.ma AS ma, h.ten AS ten, h.cap AS cap, h.cot AS cot, h.dinh_nghia AS dinh_nghia ORDER BY h.cap, h.cot"
Q_DS_LA_MOT = "MATCH (c:Hinh)-[:LA_MOT]->(p:Hinh) RETURN c.ma AS con, p.ma AS cha"
Q_DS_TINH_CHAT = """MATCH (t:TinhChat)
RETURN t.ma AS ma, t.ten AS ten, t.nhom AS nhom, t.nhom_ten AS nhom_ten
ORDER BY t.thu_tu"""

Q_CHI_TIET_HINH = """
MATCH (h:Hinh {ma: $ma})
OPTIONAL MATCH (h)-[:LA_MOT]->(cha:Hinh)
OPTIONAL MATCH (con:Hinh)-[:LA_MOT]->(h)
RETURN h {.*} AS hinh,
       collect(DISTINCT cha {.ma, .ten}) AS cha,
       collect(DISTINCT con {.ma, .ten}) AS con"""

Q_TINH_CHAT_CUA_HINH = """
MATCH (h:Hinh {ma: $ma})-[:LA_MOT*0..]->(a:Hinh)-[:CO_TINH_CHAT]->(t:TinhChat)
WITH t, collect(DISTINCT a.ten) AS tu_hinh, min(a.cap) AS cap
RETURN t.ten AS ten, t.nhom_ten AS nhom, tu_hinh, $ten IN tu_hinh AS rieng
ORDER BY rieng DESC, t.thu_tu"""

Q_DAU_HIEU_NHAN_BIET = """
MATCH (d:DauHieu)-[:KET_LUAN]->(:Hinh {ma: $ma})
MATCH (d)-[:AP_DUNG_CHO]->(x:Hinh)
RETURN d.ma AS ma, d.ten AS ten, x.ten AS tu_hinh,
       [(d)-[:CAN]->(t:TinhChat) | t.ten] AS can
ORDER BY d.ma"""

Q_DAU_HIEU_DI_TIEP = """
MATCH (d:DauHieu)-[:AP_DUNG_CHO]->(:Hinh {ma: $ma})
OPTIONAL MATCH (d)-[:KET_LUAN]->(k:Hinh)
RETURN d.ma AS ma, d.ten AS ten, k.ten AS ket_luan, k.ma AS ket_luan_ma,
       [(d)-[:CAN]->(t:TinhChat) | t.ten] AS can
ORDER BY d.ma"""

Q_THONG_KE_NUT = """
MATCH (n) WHERE n:Hinh OR n:TinhChat OR n:DauHieu OR n:DaiLuong OR n:CongThuc
RETURN labels(n)[0] AS nhan, count(*) AS so ORDER BY nhan"""

Q_THONG_KE_CANH = """
MATCH (a)-[r]->(b) WHERE (a:Hinh OR a:TinhChat OR a:DauHieu OR a:CongThuc)
RETURN type(r) AS loai, count(*) AS so ORDER BY loai"""

Q_DS_DAU_HIEU = """
MATCH (d:DauHieu)-[:AP_DUNG_CHO]->(x:Hinh)
OPTIONAL MATCH (d)-[:KET_LUAN]->(k:Hinh)
RETURN d.ma AS ma, d.ten AS ten, d.loai AS loai, x.ten AS tu_hinh, k.ten AS ket_luan,
       [(d)-[:CAN]->(t:TinhChat) | t.ten] AS can
ORDER BY d.ma"""

# Các câu truy vấn mẫu hiển thị trên trang "Đồ thị tri thức" để người học tự chạy
TRUY_VAN_MAU = [
    ("Xem toàn bộ sơ đồ phân cấp tứ giác",
     "MATCH p = (:Hinh)-[:LA_MOT]->(:Hinh)\nRETURN p"),
    ("Hình vuông là “con cháu” của những hình nào?",
     "MATCH (:Hinh {ma: 'HINH_VUONG'})-[:LA_MOT*]->(a:Hinh)\nRETURN DISTINCT a.ten AS hinh_to_tien"),
    ("Mọi tính chất của hình chữ nhật (kể cả kế thừa)",
     "MATCH (:Hinh {ma: 'HINH_CHU_NHAT'})-[:LA_MOT*0..]->(a)-[:CO_TINH_CHAT]->(t)\n"
     "RETURN t.ten AS tinh_chat, collect(DISTINCT a.ten) AS ke_thua_tu"),
    ("Các dấu hiệu nhận biết hình thoi",
     "MATCH (x:Hinh)<-[:AP_DUNG_CHO]-(d:DauHieu)-[:KET_LUAN]->(:Hinh {ma: 'HINH_THOI'})\n"
     "MATCH (d)-[:CAN]->(t:TinhChat)\n"
     "RETURN x.ten AS tu_hinh, collect(t.ten) AS can_them, d.ten AS dau_hieu"),
    ("Đồ thị các dấu hiệu dẫn tới hình vuông",
     "MATCH p = (:Hinh)<-[:AP_DUNG_CHO]-(d:DauHieu)-[:KET_LUAN]->(:Hinh {ma: 'HINH_VUONG'})\n"
     "OPTIONAL MATCH q = (d)-[:CAN]->(:TinhChat)\nRETURN p, q"),
    ("Tính chất “hai đường chéo bằng nhau” giúp nhận biết những hình nào?",
     "MATCH (:TinhChat {ma: 'CHEO_BANG'})<-[:CAN]-(d:DauHieu)-[:KET_LUAN]->(k:Hinh)\n"
     "MATCH (d)-[:AP_DUNG_CHO]->(x:Hinh)\nRETURN x.ten AS tu_hinh, k.ten AS thanh_hinh"),
    ("Các cặp tính chất mâu thuẫn",
     "MATCH (a:TinhChat)-[m:MAU_THUAN]->(b:TinhChat)\nRETURN a.ten, b.ten, m.ly_do"),
    ("Công thức diện tích và chu vi của mọi hình",
     "MATCH (h:Hinh)-[:CO_CONG_THUC]->(c:CongThuc)\nWHERE c.loai IN ['dien_tich', 'chu_vi']\n"
     "RETURN h.ten AS hinh, c.loai_ten AS loai, c.hien_thi AS cong_thuc\nORDER BY h.cap, h.ten, c.thu_tu"),
    ("Muốn tính diện tích hình thoi cần biết những đại lượng nào?",
     "MATCH (:Hinh {ma: 'HINH_THOI'})-[:CO_CONG_THUC]->(c:CongThuc)-[:TINH_RA]->(:DaiLuong {bien: 'S'})\n"
     "RETURN c.hien_thi AS cong_thuc, [(c)-[:CAN_BIEN]->(v) | v.ten] AS can_biet"),
    ("Đồ thị công thức của hình chữ nhật",
     "MATCH p = (:Hinh {ma: 'HINH_CHU_NHAT'})-[:CO_CONG_THUC]->(c:CongThuc)-[:TINH_RA|CAN_BIEN]->(:DaiLuong)\nRETURN p"),
]

# ----- Trang Thử thách -----
Q_LUU_LUOT_CHOI = """
CREATE (l:LuotChoi {ten: $ten, diem: $diem, so_cau: $so_cau, thoi_diem: datetime()})
WITH l
UNWIND $hoan_thanh AS ma
MATCH (h:Hinh {ma: ma})
MERGE (l)-[:HOAN_THANH]->(h)
RETURN count(*) AS so"""

Q_BANG_XEP_HANG = """
MATCH (l:LuotChoi)
RETURN l.ten AS ten, l.diem AS diem, l.so_cau AS so_cau,
       toString(date(l.thoi_diem)) AS ngay
ORDER BY diem DESC, l.thoi_diem ASC
LIMIT 10"""
