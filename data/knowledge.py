"""
Cơ sở tri thức về tứ giác trong hình học phẳng (chương trình Toán 8).

Đây là NGUỒN DUY NHẤT của tri thức. Script `src/seed.py` đọc file này và
nạp vào Neo4j thành đồ thị gồm 3 loại nút:

    (:Hinh)      - một loại tứ giác (hình thang, hình bình hành, ...)
    (:TinhChat)  - một tính chất nguyên tử (hai đường chéo bằng nhau, ...)
    (:DauHieu)   - một dấu hiệu nhận biết = một luật suy luận
                   "Hình X + các tính chất P1, P2... => Hình Y"

và các quan hệ:

    (Hinh)-[:LA_MOT]->(Hinh)             quan hệ bao hàm (hình vuông LÀ MỘT hình thoi)
    (Hinh)-[:CO_TINH_CHAT]->(TinhChat)   tính chất luôn đúng của hình
    (DauHieu)-[:AP_DUNG_CHO]->(Hinh)     điều kiện về hình ban đầu của luật
    (DauHieu)-[:CAN]->(TinhChat)         các tính chất cần có
    (DauHieu)-[:KET_LUAN]->(Hinh)        hình được kết luận
    (TinhChat)-[:MAU_THUAN]->(TinhChat)  hai tính chất không thể cùng xảy ra
"""

# ---------------------------------------------------------------------------
# 1. CÁC LOẠI HÌNH
#    cap: tầng trong sơ đồ phân cấp (0 = tổng quát nhất)
#    cot: vị trí ngang khi vẽ sơ đồ
# ---------------------------------------------------------------------------
HINH = [
    {"ma": "TU_GIAC", "ten": "Tứ giác", "cap": 0, "cot": 2,
     "dinh_nghia": "Tứ giác ABCD là hình gồm bốn đoạn thẳng AB, BC, CD, DA, "
                   "trong đó không có hai đoạn thẳng nào cùng nằm trên một đường thẳng. "
                   "Ở đây ta xét tứ giác lồi."},
    {"ma": "HINH_THANG", "ten": "Hình thang", "cap": 1, "cot": 1.5,
     "dinh_nghia": "Hình thang là tứ giác có hai cạnh đối song song."},
    {"ma": "HINH_DIEU", "ten": "Hình diều", "cap": 1, "cot": 3.5,
     "dinh_nghia": "Hình diều (hình cánh diều) là tứ giác có hai cặp cạnh kề bằng nhau "
                   "(AB = AD và CB = CD)."},
    {"ma": "HINH_THANG_VUONG", "ten": "Hình thang vuông", "cap": 2, "cot": 0.5,
     "dinh_nghia": "Hình thang vuông là hình thang có một góc vuông."},
    {"ma": "HINH_THANG_CAN", "ten": "Hình thang cân", "cap": 2, "cot": 1.5,
     "dinh_nghia": "Hình thang cân là hình thang có hai góc kề một đáy bằng nhau."},
    {"ma": "HINH_BINH_HANH", "ten": "Hình bình hành", "cap": 2, "cot": 2.75,
     "dinh_nghia": "Hình bình hành là tứ giác có các cạnh đối song song."},
    {"ma": "HINH_CHU_NHAT", "ten": "Hình chữ nhật", "cap": 3, "cot": 1.75,
     "dinh_nghia": "Hình chữ nhật là tứ giác có bốn góc vuông."},
    {"ma": "HINH_THOI", "ten": "Hình thoi", "cap": 3, "cot": 3.25,
     "dinh_nghia": "Hình thoi là tứ giác có bốn cạnh bằng nhau."},
    {"ma": "HINH_VUONG", "ten": "Hình vuông", "cap": 4, "cot": 2.5,
     "dinh_nghia": "Hình vuông là tứ giác có bốn góc vuông và bốn cạnh bằng nhau."},
]

# (con, cha): con LÀ MỘT cha
LA_MOT = [
    ("HINH_THANG", "TU_GIAC"),
    ("HINH_DIEU", "TU_GIAC"),
    ("HINH_THANG_VUONG", "HINH_THANG"),
    ("HINH_THANG_CAN", "HINH_THANG"),
    ("HINH_BINH_HANH", "HINH_THANG"),
    ("HINH_CHU_NHAT", "HINH_BINH_HANH"),
    ("HINH_CHU_NHAT", "HINH_THANG_CAN"),
    ("HINH_CHU_NHAT", "HINH_THANG_VUONG"),
    ("HINH_THOI", "HINH_BINH_HANH"),
    ("HINH_THOI", "HINH_DIEU"),
    ("HINH_VUONG", "HINH_CHU_NHAT"),
    ("HINH_VUONG", "HINH_THOI"),
]

# ---------------------------------------------------------------------------
# 2. CÁC TÍNH CHẤT NGUYÊN TỬ (giả thiết người dùng có thể chọn)
#    nhom: canh | goc | duong_cheo
# ---------------------------------------------------------------------------
TINH_CHAT = [
    # --- Cạnh ---
    {"ma": "SS_1_CAP", "nhom": "canh", "ten": "Có một cặp cạnh đối song song"},
    {"ma": "SS_2_CAP", "nhom": "canh", "ten": "Hai cặp cạnh đối song song"},
    {"ma": "BANG_2_CAP", "nhom": "canh", "ten": "Hai cặp cạnh đối bằng nhau"},
    {"ma": "SS_VA_BANG", "nhom": "canh", "ten": "Có một cặp cạnh đối vừa song song vừa bằng nhau"},
    {"ma": "CANH_BEN_BANG", "nhom": "canh", "ten": "Cặp cạnh còn lại (hai cạnh bên) bằng nhau"},
    {"ma": "CANH_BEN_KHONG_SS", "nhom": "canh", "ten": "Hai cạnh bên không song song"},
    {"ma": "HAI_CANH_KE_BANG", "nhom": "canh", "ten": "Có hai cạnh kề bằng nhau"},
    {"ma": "HAI_CAP_KE_BANG", "nhom": "canh", "ten": "Hai cặp cạnh kề bằng nhau (AB = AD, CB = CD)"},
    {"ma": "BON_CANH_BANG", "nhom": "canh", "ten": "Bốn cạnh bằng nhau"},
    # --- Góc ---
    {"ma": "MOT_GOC_VUONG", "nhom": "goc", "ten": "Có một góc vuông"},
    {"ma": "BA_GOC_VUONG", "nhom": "goc", "ten": "Có ba góc vuông"},
    {"ma": "GOC_DOI_BANG", "nhom": "goc", "ten": "Các góc đối bằng nhau"},
    {"ma": "GOC_KE_DAY_BANG", "nhom": "goc", "ten": "Hai góc kề một đáy bằng nhau"},
    # --- Đường chéo ---
    {"ma": "CHEO_TRUNG_DIEM", "nhom": "duong_cheo", "ten": "Hai đường chéo cắt nhau tại trung điểm mỗi đường"},
    {"ma": "CHEO_BANG", "nhom": "duong_cheo", "ten": "Hai đường chéo bằng nhau"},
    {"ma": "CHEO_VUONG_GOC", "nhom": "duong_cheo", "ten": "Hai đường chéo vuông góc với nhau"},
    {"ma": "CHEO_PHAN_GIAC", "nhom": "duong_cheo", "ten": "Có một đường chéo là đường phân giác của một góc"},
]

NHOM_TEN = {"canh": "Về cạnh", "goc": "Về góc", "duong_cheo": "Về đường chéo"}

# Tính chất luôn đúng của từng hình (chỉ ghi phần RIÊNG; phần của hình cha
# được kế thừa qua quan hệ LA_MOT khi truy vấn).
CO_TINH_CHAT = {
    "TU_GIAC": [],
    "HINH_THANG": ["SS_1_CAP"],
    "HINH_DIEU": ["HAI_CAP_KE_BANG", "HAI_CANH_KE_BANG", "CHEO_VUONG_GOC", "CHEO_PHAN_GIAC"],
    "HINH_THANG_VUONG": ["MOT_GOC_VUONG"],
    "HINH_THANG_CAN": ["GOC_KE_DAY_BANG", "CHEO_BANG", "CANH_BEN_BANG"],
    "HINH_BINH_HANH": ["SS_2_CAP", "BANG_2_CAP", "SS_VA_BANG", "GOC_DOI_BANG",
                       "CHEO_TRUNG_DIEM", "CANH_BEN_BANG"],
    "HINH_CHU_NHAT": ["BA_GOC_VUONG"],
    "HINH_THOI": ["BON_CANH_BANG"],
    "HINH_VUONG": [],
}

# Hai tính chất không thể cùng đúng
MAU_THUAN = [
    ("SS_2_CAP", "CANH_BEN_KHONG_SS",
     "Tứ giác có hai cặp cạnh đối song song thì hai cạnh bên cũng song song."),
    ("CHEO_TRUNG_DIEM", "CANH_BEN_KHONG_SS",
     "Hai đường chéo cắt nhau tại trung điểm mỗi đường ⇒ hình bình hành ⇒ hai cạnh bên song song."),
    ("SS_VA_BANG", "CANH_BEN_KHONG_SS",
     "Một cặp cạnh đối vừa song song vừa bằng nhau ⇒ hình bình hành ⇒ hai cạnh bên song song."),
    ("BANG_2_CAP", "CANH_BEN_KHONG_SS",
     "Hai cặp cạnh đối bằng nhau ⇒ hình bình hành ⇒ hai cạnh bên song song."),
    ("GOC_DOI_BANG", "CANH_BEN_KHONG_SS",
     "Các góc đối bằng nhau ⇒ hình bình hành ⇒ hai cạnh bên song song."),
]

# ---------------------------------------------------------------------------
# 3. DẤU HIỆU NHẬN BIẾT (LUẬT SUY LUẬN)
#    ap_dung: hình ban đầu phải có
#    can:     các tính chất cần có
#    ket_luan: hình kết luận (None = luật gợi ý, chỉ đưa ra nhận xét)
#    tru_khi: (chỉ cho luật gợi ý) không hiển thị nếu đã suy ra một trong các hình này
# ---------------------------------------------------------------------------
DAU_HIEU = [
    # ----- Hình thang -----
    {"ma": "DH01", "ap_dung": "TU_GIAC", "can": ["SS_1_CAP"], "ket_luan": "HINH_THANG",
     "ten": "Tứ giác có hai cạnh đối song song là hình thang."},
    {"ma": "DH02", "ap_dung": "HINH_THANG", "can": ["MOT_GOC_VUONG"], "ket_luan": "HINH_THANG_VUONG",
     "ten": "Hình thang có một góc vuông là hình thang vuông."},
    {"ma": "DH03", "ap_dung": "HINH_THANG", "can": ["GOC_KE_DAY_BANG"], "ket_luan": "HINH_THANG_CAN",
     "ten": "Hình thang có hai góc kề một đáy bằng nhau là hình thang cân."},
    {"ma": "DH04", "ap_dung": "HINH_THANG", "can": ["CHEO_BANG"], "ket_luan": "HINH_THANG_CAN",
     "ten": "Hình thang có hai đường chéo bằng nhau là hình thang cân."},
    {"ma": "DH05", "ap_dung": "HINH_THANG", "can": ["CANH_BEN_BANG", "CANH_BEN_KHONG_SS"],
     "ket_luan": "HINH_THANG_CAN",
     "ten": "Hình thang có hai cạnh bên bằng nhau và không song song là hình thang cân."},
    {"ma": "GY01", "ap_dung": "HINH_THANG", "can": ["CANH_BEN_BANG"], "ket_luan": None,
     "tru_khi": ["HINH_THANG_CAN", "HINH_BINH_HANH"],
     "ten": "Hình thang có hai cạnh bên bằng nhau CHƯA chắc là hình thang cân.",
     "ghi_chu": "Hình thang có một cặp cạnh song song và cặp cạnh còn lại bằng nhau thì là "
                "HÌNH THANG CÂN hoặc HÌNH BÌNH HÀNH. Cần thêm một giả thiết, ví dụ: "
                "“hai cạnh bên không song song” (→ hình thang cân) hoặc "
                "“hai cặp cạnh đối song song” (→ hình bình hành)."},
    # ----- Hình bình hành -----
    {"ma": "DH06", "ap_dung": "TU_GIAC", "can": ["SS_2_CAP"], "ket_luan": "HINH_BINH_HANH",
     "ten": "Tứ giác có các cạnh đối song song là hình bình hành."},
    {"ma": "DH07", "ap_dung": "TU_GIAC", "can": ["BANG_2_CAP"], "ket_luan": "HINH_BINH_HANH",
     "ten": "Tứ giác có các cạnh đối bằng nhau là hình bình hành."},
    {"ma": "DH08", "ap_dung": "TU_GIAC", "can": ["SS_VA_BANG"], "ket_luan": "HINH_BINH_HANH",
     "ten": "Tứ giác có hai cạnh đối song song và bằng nhau là hình bình hành."},
    {"ma": "DH09", "ap_dung": "TU_GIAC", "can": ["GOC_DOI_BANG"], "ket_luan": "HINH_BINH_HANH",
     "ten": "Tứ giác có các góc đối bằng nhau là hình bình hành."},
    {"ma": "DH10", "ap_dung": "TU_GIAC", "can": ["CHEO_TRUNG_DIEM"], "ket_luan": "HINH_BINH_HANH",
     "ten": "Tứ giác có hai đường chéo cắt nhau tại trung điểm của mỗi đường là hình bình hành."},
    # ----- Hình chữ nhật -----
    {"ma": "DH11", "ap_dung": "TU_GIAC", "can": ["BA_GOC_VUONG"], "ket_luan": "HINH_CHU_NHAT",
     "ten": "Tứ giác có ba góc vuông là hình chữ nhật."},
    {"ma": "DH12", "ap_dung": "HINH_THANG_CAN", "can": ["MOT_GOC_VUONG"], "ket_luan": "HINH_CHU_NHAT",
     "ten": "Hình thang cân có một góc vuông là hình chữ nhật."},
    {"ma": "DH13", "ap_dung": "HINH_BINH_HANH", "can": ["MOT_GOC_VUONG"], "ket_luan": "HINH_CHU_NHAT",
     "ten": "Hình bình hành có một góc vuông là hình chữ nhật."},
    {"ma": "DH14", "ap_dung": "HINH_BINH_HANH", "can": ["CHEO_BANG"], "ket_luan": "HINH_CHU_NHAT",
     "ten": "Hình bình hành có hai đường chéo bằng nhau là hình chữ nhật."},
    # ----- Hình thoi -----
    {"ma": "DH15", "ap_dung": "TU_GIAC", "can": ["BON_CANH_BANG"], "ket_luan": "HINH_THOI",
     "ten": "Tứ giác có bốn cạnh bằng nhau là hình thoi."},
    {"ma": "DH16", "ap_dung": "HINH_BINH_HANH", "can": ["HAI_CANH_KE_BANG"], "ket_luan": "HINH_THOI",
     "ten": "Hình bình hành có hai cạnh kề bằng nhau là hình thoi."},
    {"ma": "DH17", "ap_dung": "HINH_BINH_HANH", "can": ["CHEO_VUONG_GOC"], "ket_luan": "HINH_THOI",
     "ten": "Hình bình hành có hai đường chéo vuông góc là hình thoi."},
    {"ma": "DH18", "ap_dung": "HINH_BINH_HANH", "can": ["CHEO_PHAN_GIAC"], "ket_luan": "HINH_THOI",
     "ten": "Hình bình hành có một đường chéo là đường phân giác của một góc là hình thoi."},
    # ----- Hình vuông -----
    {"ma": "DH19", "ap_dung": "HINH_CHU_NHAT", "can": ["HAI_CANH_KE_BANG"], "ket_luan": "HINH_VUONG",
     "ten": "Hình chữ nhật có hai cạnh kề bằng nhau là hình vuông."},
    {"ma": "DH20", "ap_dung": "HINH_CHU_NHAT", "can": ["CHEO_VUONG_GOC"], "ket_luan": "HINH_VUONG",
     "ten": "Hình chữ nhật có hai đường chéo vuông góc là hình vuông."},
    {"ma": "DH21", "ap_dung": "HINH_CHU_NHAT", "can": ["CHEO_PHAN_GIAC"], "ket_luan": "HINH_VUONG",
     "ten": "Hình chữ nhật có một đường chéo là đường phân giác của một góc là hình vuông."},
    {"ma": "DH22", "ap_dung": "HINH_THOI", "can": ["MOT_GOC_VUONG"], "ket_luan": "HINH_VUONG",
     "ten": "Hình thoi có một góc vuông là hình vuông."},
    {"ma": "DH23", "ap_dung": "HINH_THOI", "can": ["CHEO_BANG"], "ket_luan": "HINH_VUONG",
     "ten": "Hình thoi có hai đường chéo bằng nhau là hình vuông."},
    # ----- Hình diều -----
    {"ma": "DH24", "ap_dung": "TU_GIAC", "can": ["HAI_CAP_KE_BANG"], "ket_luan": "HINH_DIEU",
     "ten": "Tứ giác có hai cặp cạnh kề bằng nhau là hình diều."},
    {"ma": "DH25", "ap_dung": "HINH_DIEU", "can": ["SS_1_CAP"], "ket_luan": "HINH_THOI",
     "ten": "Hình diều có một cặp cạnh đối song song là hình thoi."},
]

# ---------------------------------------------------------------------------
# 4. BÀI TOÁN MẪU (dùng cho trang Ví dụ)
# ---------------------------------------------------------------------------
VI_DU = [
    {"de": "Hình bình hành có hai đường chéo vuông góc và bằng nhau là hình gì?",
     "hinh": "HINH_BINH_HANH", "tc": ["CHEO_VUONG_GOC", "CHEO_BANG"]},
    {"de": "Hình thang có một cặp cạnh song song, cặp cạnh còn lại bằng nhau là hình gì?",
     "hinh": "HINH_THANG", "tc": ["CANH_BEN_BANG"]},
    {"de": "Hình thang có hai cạnh bên bằng nhau và không song song là hình gì?",
     "hinh": "HINH_THANG", "tc": ["CANH_BEN_BANG", "CANH_BEN_KHONG_SS"]},
    {"de": "Tứ giác có hai đường chéo cắt nhau tại trung điểm mỗi đường và bằng nhau là hình gì?",
     "hinh": "TU_GIAC", "tc": ["CHEO_TRUNG_DIEM", "CHEO_BANG"]},
    {"de": "Tứ giác có bốn cạnh bằng nhau và một góc vuông là hình gì?",
     "hinh": "TU_GIAC", "tc": ["BON_CANH_BANG", "MOT_GOC_VUONG"]},
    {"de": "Hình thang có hai đường chéo bằng nhau và một góc vuông là hình gì?",
     "hinh": "HINH_THANG", "tc": ["CHEO_BANG", "MOT_GOC_VUONG"]},
    {"de": "Tứ giác có hai cặp cạnh kề bằng nhau và một cặp cạnh đối song song là hình gì?",
     "hinh": "TU_GIAC", "tc": ["HAI_CAP_KE_BANG", "SS_1_CAP"]},
    {"de": "Hình thoi có hai đường chéo bằng nhau là hình gì?",
     "hinh": "HINH_THOI", "tc": ["CHEO_BANG"]},
    {"de": "Tứ giác có một cặp cạnh đối song song và một góc vuông là hình gì?",
     "hinh": "TU_GIAC", "tc": ["SS_1_CAP", "MOT_GOC_VUONG"]},
    {"de": "(Mâu thuẫn) Tứ giác có hai cặp cạnh đối song song nhưng hai cạnh bên không song song?",
     "hinh": "TU_GIAC", "tc": ["SS_2_CAP", "CANH_BEN_KHONG_SS"]},
]
