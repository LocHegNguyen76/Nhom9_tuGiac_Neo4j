// Các truy vấn mẫu — dán từng câu vào Neo4j Browser để chạy

// 1. Xem toàn bộ sơ đồ phân cấp tứ giác
MATCH p = (:Hinh)-[:LA_MOT]->(:Hinh)
RETURN p;

// 2. Hình vuông là “con cháu” của những hình nào?
MATCH (:Hinh {ma: 'HINH_VUONG'})-[:LA_MOT*]->(a:Hinh)
RETURN DISTINCT a.ten AS hinh_to_tien;

// 3. Mọi tính chất của hình chữ nhật (kể cả kế thừa)
MATCH (:Hinh {ma: 'HINH_CHU_NHAT'})-[:LA_MOT*0..]->(a)-[:CO_TINH_CHAT]->(t)
RETURN t.ten AS tinh_chat, collect(DISTINCT a.ten) AS ke_thua_tu;

// 4. Các dấu hiệu nhận biết hình thoi
MATCH (x:Hinh)<-[:AP_DUNG_CHO]-(d:DauHieu)-[:KET_LUAN]->(:Hinh {ma: 'HINH_THOI'})
MATCH (d)-[:CAN]->(t:TinhChat)
RETURN x.ten AS tu_hinh, collect(t.ten) AS can_them, d.ten AS dau_hieu;

// 5. Đồ thị các dấu hiệu dẫn tới hình vuông
MATCH p = (:Hinh)<-[:AP_DUNG_CHO]-(d:DauHieu)-[:KET_LUAN]->(:Hinh {ma: 'HINH_VUONG'})
OPTIONAL MATCH q = (d)-[:CAN]->(:TinhChat)
RETURN p, q;

// 6. Tính chất “hai đường chéo bằng nhau” giúp nhận biết những hình nào?
MATCH (:TinhChat {ma: 'CHEO_BANG'})<-[:CAN]-(d:DauHieu)-[:KET_LUAN]->(k:Hinh)
MATCH (d)-[:AP_DUNG_CHO]->(x:Hinh)
RETURN x.ten AS tu_hinh, k.ten AS thanh_hinh;

// 7. Các cặp tính chất mâu thuẫn
MATCH (a:TinhChat)-[m:MAU_THUAN]->(b:TinhChat)
RETURN a.ten, b.ten, m.ly_do;

// 8. Một vòng suy luận thuần Cypher:
//    Hình bình hành + hai đường chéo vuông góc + hai đường chéo bằng nhau
//    -> những dấu hiệu nào áp dụng được ngay?
WITH ['HINH_BINH_HANH'] AS hinh, ['CHEO_VUONG_GOC', 'CHEO_BANG'] AS gia_thiet
MATCH (h0:Hinh)-[:LA_MOT*0..]->(a:Hinh) WHERE h0.ma IN hinh
WITH gia_thiet, collect(DISTINCT a.ma) AS hinh_biet
OPTIONAL MATCH (x:Hinh)-[:CO_TINH_CHAT]->(t:TinhChat) WHERE x.ma IN hinh_biet
WITH hinh_biet, gia_thiet + collect(DISTINCT t.ma) AS tc_biet
MATCH (d:DauHieu)-[:AP_DUNG_CHO]->(h:Hinh) WHERE h.ma IN hinh_biet
WITH d, h, tc_biet, [(d)-[:CAN]->(c:TinhChat) | c.ma] AS can
WHERE all(c IN can WHERE c IN tc_biet)
MATCH (d)-[:KET_LUAN]->(k:Hinh)
RETURN d.ma AS dau_hieu, h.ten AS tu_hinh, can, k.ten AS ket_luan
ORDER BY dau_hieu;
