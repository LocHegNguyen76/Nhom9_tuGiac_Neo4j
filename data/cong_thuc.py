"""
Công thức diện tích, chu vi và các công thức liên quan của từng loại tứ giác.

Mỗi hình có:
  DAI_LUONG[hình] : danh sách đại lượng (biến, ký hiệu hiển thị, tên, kiểu)
                    kiểu: "dai" (độ dài) | "dt" (diện tích) | "goc" (góc, đơn vị độ)
  CONG_THUC[hình] : danh sách công thức (loại, hiển thị, kết quả, biểu thức Python, ghi chú)

Biểu thức Python chỉ được dùng các hàm trong HAM (sqrt, sind, cosd, ...);
góc luôn tính bằng độ. Các biến đầu vào của công thức được tự động lấy ra
từ biểu thức (hàm cac_bien_vao).

Script src/seed.py nạp phần này vào Neo4j thành:
  (:Hinh)-[:CO_DAI_LUONG]->(:DaiLuong)
  (:Hinh)-[:CO_CONG_THUC]->(:CongThuc)
  (:CongThuc)-[:CAN_BIEN]->(:DaiLuong)
  (:CongThuc)-[:TINH_RA]->(:DaiLuong)
"""
import ast
import math

LOAI_CONG_THUC = {
    "dien_tich": "Diện tích",
    "chu_vi": "Chu vi",
    "duong_cheo": "Đường chéo",
    "chieu_cao": "Chiều cao",
    "canh": "Cạnh / đường trung bình",
    "goc": "Góc",
    "duong_tron": "Đường tròn nội / ngoại tiếp",
}


def _sind(x): return math.sin(math.radians(x))
def _cosd(x): return math.cos(math.radians(x))
def _tand(x): return math.tan(math.radians(x))
def _atand(x): return math.degrees(math.atan(x))
def _asind(x): return math.degrees(math.asin(x))
def _acosd(x): return math.degrees(math.acos(x))


HAM = {"sqrt": math.sqrt, "sind": _sind, "cosd": _cosd, "tand": _tand,
       "atand": _atand, "asind": _asind, "acosd": _acosd, "pi": math.pi}

DAI_LUONG = {
    "TU_GIAC": [
        ("a", "a", "Cạnh AB", "dai"), ("b", "b", "Cạnh BC", "dai"),
        ("c", "c", "Cạnh CD", "dai"), ("d", "d", "Cạnh DA", "dai"),
        ("d1", "d₁", "Đường chéo AC", "dai"), ("d2", "d₂", "Đường chéo BD", "dai"),
        ("phi", "φ", "Góc giữa hai đường chéo", "goc"),
        ("A", "Â", "Góc A", "goc"), ("B", "B̂", "Góc B", "goc"), ("C", "Ĉ", "Góc C", "goc"),
        ("D", "D̂", "Góc D", "goc"),
        ("S", "S", "Diện tích", "dt"), ("P", "P", "Chu vi", "dai"),
    ],
    "HINH_THANG": [
        ("a", "a", "Đáy lớn AB", "dai"), ("b", "b", "Đáy nhỏ CD", "dai"),
        ("c", "c", "Cạnh bên BC", "dai"), ("d", "d", "Cạnh bên AD", "dai"),
        ("h", "h", "Chiều cao", "dai"), ("m", "m", "Đường trung bình", "dai"),
        ("S", "S", "Diện tích", "dt"), ("P", "P", "Chu vi", "dai"),
    ],
    "HINH_THANG_CAN": [
        ("a", "a", "Đáy lớn AB", "dai"), ("b", "b", "Đáy nhỏ CD", "dai"),
        ("c", "c", "Cạnh bên (AD = BC)", "dai"), ("h", "h", "Chiều cao", "dai"),
        ("d", "d", "Đường chéo (AC = BD)", "dai"), ("alpha", "α", "Góc ở đáy lớn (Â = B̂)", "goc"),
        ("m", "m", "Đường trung bình", "dai"),
        ("S", "S", "Diện tích", "dt"), ("P", "P", "Chu vi", "dai"),
    ],
    "HINH_THANG_VUONG": [
        ("a", "a", "Đáy lớn AB", "dai"), ("b", "b", "Đáy nhỏ CD", "dai"),
        ("h", "h", "Cạnh bên AD (vuông góc hai đáy, = chiều cao)", "dai"),
        ("c", "c", "Cạnh bên BC", "dai"), ("m", "m", "Đường trung bình", "dai"),
        ("S", "S", "Diện tích", "dt"), ("P", "P", "Chu vi", "dai"),
    ],
    "HINH_BINH_HANH": [
        ("a", "a", "Cạnh AB", "dai"), ("b", "b", "Cạnh AD", "dai"),
        ("alpha", "α", "Góc A (giữa hai cạnh a, b)", "goc"),
        ("ha", "hₐ", "Chiều cao ứng với cạnh a", "dai"),
        ("d1", "d₁", "Đường chéo AC", "dai"), ("d2", "d₂", "Đường chéo BD", "dai"),
        ("S", "S", "Diện tích", "dt"), ("P", "P", "Chu vi", "dai"),
    ],
    "HINH_CHU_NHAT": [
        ("a", "a", "Chiều dài", "dai"), ("b", "b", "Chiều rộng", "dai"),
        ("d", "d", "Đường chéo", "dai"), ("R", "R", "Bán kính đường tròn ngoại tiếp", "dai"),
        ("S", "S", "Diện tích", "dt"), ("P", "P", "Chu vi", "dai"),
    ],
    "HINH_THOI": [
        ("a", "a", "Cạnh", "dai"),
        ("d1", "d₁", "Đường chéo BD", "dai"), ("d2", "d₂", "Đường chéo AC", "dai"),
        ("alpha", "α", "Góc A", "goc"), ("h", "h", "Chiều cao", "dai"),
        ("r", "r", "Bán kính đường tròn nội tiếp", "dai"),
        ("S", "S", "Diện tích", "dt"), ("P", "P", "Chu vi", "dai"),
    ],
    "HINH_VUONG": [
        ("a", "a", "Cạnh", "dai"), ("d", "d", "Đường chéo", "dai"),
        ("R", "R", "Bán kính đường tròn ngoại tiếp", "dai"),
        ("r", "r", "Bán kính đường tròn nội tiếp", "dai"),
        ("S", "S", "Diện tích", "dt"), ("P", "P", "Chu vi", "dai"),
    ],
    "HINH_DIEU": [
        ("a", "a", "Cạnh AB = AD", "dai"), ("b", "b", "Cạnh CB = CD", "dai"),
        ("d1", "d₁", "Đường chéo AC (trục đối xứng)", "dai"), ("d2", "d₂", "Đường chéo BD", "dai"),
        ("S", "S", "Diện tích", "dt"), ("P", "P", "Chu vi", "dai"),
    ],
}

# (loại, hiển thị, kết quả, biểu thức Python, ghi chú)
CONG_THUC = {
    "TU_GIAC": [
        ("chu_vi", "P = a + b + c + d", "P", "a + b + c + d", "Chu vi bằng tổng bốn cạnh."),
        ("dien_tich", "S = ½ · d₁ · d₂ · sin φ", "S", "0.5 * d1 * d2 * sind(phi)",
         "φ là góc giữa hai đường chéo. Nếu hai đường chéo vuông góc thì S = ½ · d₁ · d₂."),
        ("goc", "D̂ = 360° − (Â + B̂ + Ĉ)", "D", "360 - (A + B + C)", "Tổng bốn góc của tứ giác bằng 360°."),
    ],
    "HINH_THANG": [
        ("dien_tich", "S = ½ · (a + b) · h", "S", "0.5 * (a + b) * h", "Nửa tổng hai đáy nhân chiều cao."),
        ("dien_tich", "S = m · h", "S", "m * h", "Đường trung bình nhân chiều cao."),
        ("chu_vi", "P = a + b + c + d", "P", "a + b + c + d", "Tổng hai đáy và hai cạnh bên."),
        ("canh", "m = (a + b) / 2", "m", "(a + b) / 2", "Đường trung bình bằng nửa tổng hai đáy."),
        ("canh", "b = 2m − a", "b", "2 * m - a", "Suy từ công thức đường trung bình."),
        ("chieu_cao", "h = 2S / (a + b)", "h", "2 * S / (a + b)", "Suy từ công thức diện tích."),
        ("chieu_cao", "h = S / m", "h", "S / m", ""),
    ],
    "HINH_THANG_CAN": [
        ("dien_tich", "S = ½ · (a + b) · h", "S", "0.5 * (a + b) * h", ""),
        ("chu_vi", "P = a + b + 2c", "P", "a + b + 2 * c", "Hai cạnh bên bằng nhau."),
        ("canh", "m = (a + b) / 2", "m", "(a + b) / 2", ""),
        ("chieu_cao", "h = √(c² − ((a − b)/2)²)", "h", "sqrt(c**2 - ((a - b) / 2)**2)",
         "Định lý Pytago trong tam giác vuông tạo bởi cạnh bên, chiều cao và đoạn (a − b)/2."),
        ("canh", "c = √(h² + ((a − b)/2)²)", "c", "sqrt(h**2 + ((a - b) / 2)**2)", "Định lý Pytago."),
        ("duong_cheo", "d = √(h² + ((a + b)/2)²)", "d", "sqrt(h**2 + ((a + b) / 2)**2)",
         "Hai đường chéo của hình thang cân bằng nhau."),
        ("goc", "α = arctan(2h / (a − b))", "alpha", "atand(2 * h / (a - b))", "Góc ở đáy lớn (a > b)."),
        ("chieu_cao", "h = (a − b)/2 · tan α", "h", "(a - b) / 2 * tand(alpha)", ""),
        ("canh", "c = (a − b) / (2 · cos α)", "c", "(a - b) / (2 * cosd(alpha))", ""),
        ("chieu_cao", "h = 2S / (a + b)", "h", "2 * S / (a + b)", ""),
    ],
    "HINH_THANG_VUONG": [
        ("dien_tich", "S = ½ · (a + b) · h", "S", "0.5 * (a + b) * h",
         "Cạnh bên vuông góc với hai đáy chính là chiều cao."),
        ("chu_vi", "P = a + b + h + c", "P", "a + b + h + c", ""),
        ("canh", "m = (a + b) / 2", "m", "(a + b) / 2", ""),
        ("canh", "c = √(h² + (a − b)²)", "c", "sqrt(h**2 + (a - b)**2)", "Định lý Pytago."),
        ("chieu_cao", "h = √(c² − (a − b)²)", "h", "sqrt(c**2 - (a - b)**2)", "Định lý Pytago."),
        ("chieu_cao", "h = 2S / (a + b)", "h", "2 * S / (a + b)", ""),
    ],
    "HINH_BINH_HANH": [
        ("dien_tich", "S = a · hₐ", "S", "a * ha", "Cạnh đáy nhân chiều cao tương ứng."),
        ("dien_tich", "S = a · b · sin α", "S", "a * b * sind(alpha)", ""),
        ("chu_vi", "P = 2 · (a + b)", "P", "2 * (a + b)", ""),
        ("chieu_cao", "hₐ = b · sin α", "ha", "b * sind(alpha)", ""),
        ("chieu_cao", "hₐ = S / a", "ha", "S / a", ""),
        ("duong_cheo", "d₁ = √(a² + b² + 2ab · cos α)", "d1", "sqrt(a**2 + b**2 + 2 * a * b * cosd(alpha))",
         "Định lý côsin. Luôn có d₁² + d₂² = 2(a² + b²)."),
        ("duong_cheo", "d₂ = √(a² + b² − 2ab · cos α)", "d2", "sqrt(a**2 + b**2 - 2 * a * b * cosd(alpha))",
         "Định lý côsin."),
        ("canh", "b = P/2 − a", "b", "P / 2 - a", ""),
        ("goc", "α = arcsin(hₐ / b)", "alpha", "asind(ha / b)", "Cho góc nhọn α."),
    ],
    "HINH_CHU_NHAT": [
        ("dien_tich", "S = a · b", "S", "a * b", "Chiều dài nhân chiều rộng."),
        ("chu_vi", "P = 2 · (a + b)", "P", "2 * (a + b)", ""),
        ("duong_cheo", "d = √(a² + b²)", "d", "sqrt(a**2 + b**2)", "Định lý Pytago; hai đường chéo bằng nhau."),
        ("duong_tron", "R = d / 2", "R", "d / 2", "Tâm đường tròn ngoại tiếp là giao điểm hai đường chéo."),
        ("duong_cheo", "d = 2R", "d", "2 * R", ""),
        ("canh", "b = S / a", "b", "S / a", ""),
        ("canh", "b = P/2 − a", "b", "P / 2 - a", ""),
        ("canh", "b = √(d² − a²)", "b", "sqrt(d**2 - a**2)", ""),
        ("canh", "a = P/4 + √((P/4)² − S)", "a", "P / 4 + sqrt((P / 4)**2 - S)",
         "Giải hệ a + b = P/2 và a · b = S (lấy a ≥ b)."),
    ],
    "HINH_THOI": [
        ("dien_tich", "S = ½ · d₁ · d₂", "S", "0.5 * d1 * d2", "Nửa tích hai đường chéo."),
        ("dien_tich", "S = a · h", "S", "a * h", ""),
        ("dien_tich", "S = a² · sin α", "S", "a**2 * sind(alpha)", ""),
        ("chu_vi", "P = 4a", "P", "4 * a", ""),
        ("canh", "a = P / 4", "a", "P / 4", ""),
        ("canh", "a = √((d₁/2)² + (d₂/2)²)", "a", "sqrt((d1 / 2)**2 + (d2 / 2)**2)",
         "Hai đường chéo vuông góc tại trung điểm mỗi đường (Pytago)."),
        ("duong_cheo", "d₂ = 2 · √(a² − (d₁/2)²)", "d2", "2 * sqrt(a**2 - (d1 / 2)**2)", ""),
        ("duong_cheo", "d₁ = 2a · sin(α/2)", "d1", "2 * a * sind(alpha / 2)", ""),
        ("duong_cheo", "d₂ = 2a · cos(α/2)", "d2", "2 * a * cosd(alpha / 2)", ""),
        ("goc", "α = 2 · arctan(d₁ / d₂)", "alpha", "2 * atand(d1 / d2)", ""),
        ("chieu_cao", "h = S / a", "h", "S / a", ""),
        ("duong_tron", "r = h / 2", "r", "h / 2", "Tâm đường tròn nội tiếp là giao điểm hai đường chéo."),
    ],
    "HINH_VUONG": [
        ("dien_tich", "S = a²", "S", "a**2", ""),
        ("dien_tich", "S = d² / 2", "S", "d**2 / 2", ""),
        ("chu_vi", "P = 4a", "P", "4 * a", ""),
        ("duong_cheo", "d = a√2", "d", "a * sqrt(2)", ""),
        ("canh", "a = d / √2", "a", "d / sqrt(2)", ""),
        ("canh", "a = √S", "a", "sqrt(S)", ""),
        ("canh", "a = P / 4", "a", "P / 4", ""),
        ("duong_tron", "R = d / 2", "R", "d / 2", ""),
        ("duong_tron", "r = a / 2", "r", "a / 2", ""),
    ],
    "HINH_DIEU": [
        ("dien_tich", "S = ½ · d₁ · d₂", "S", "0.5 * d1 * d2", "Hai đường chéo của hình diều vuông góc."),
        ("chu_vi", "P = 2 · (a + b)", "P", "2 * (a + b)", ""),
        ("duong_cheo", "d₁ = √(a² − (d₂/2)²) + √(b² − (d₂/2)²)", "d1",
         "sqrt(a**2 - (d2 / 2)**2) + sqrt(b**2 - (d2 / 2)**2)",
         "AC chia BD thành hai nửa bằng nhau và vuông góc với BD (Pytago)."),
    ],
}

# Số liệu mẫu cho nút "Điền ví dụ"
VI_DU_TINH = {
    "TU_GIAC": {"a": 4, "b": 5, "c": 6, "d": 3, "d1": 7, "d2": 6, "phi": 60, "A": 80, "B": 100, "C": 70},
    "HINH_THANG": {"a": 10, "b": 6, "c": 5, "d": 4.5, "h": 4},
    "HINH_THANG_CAN": {"a": 10, "b": 4, "h": 4},
    "HINH_THANG_VUONG": {"a": 9, "b": 5, "h": 3},
    "HINH_BINH_HANH": {"a": 6, "b": 4, "alpha": 30},
    "HINH_CHU_NHAT": {"a": 4, "b": 3},
    "HINH_THOI": {"d1": 6, "d2": 8},
    "HINH_VUONG": {"a": 5},
    "HINH_DIEU": {"a": 7.5, "b": 10, "d2": 12},
}


def cac_bien_vao(bieu_thuc):
    """Lấy danh sách biến đầu vào từ biểu thức (bỏ tên hàm)."""
    ten = {n.id for n in ast.walk(ast.parse(bieu_thuc, mode="eval")) if isinstance(n, ast.Name)}
    return sorted(ten - set(HAM))


def ds_cong_thuc():
    """Danh sách phẳng mọi công thức kèm mã, biến vào, thứ tự."""
    out = []
    for hinh, ds in CONG_THUC.items():
        for i, (loai, hien_thi, ket_qua, bieu_thuc, ghi_chu) in enumerate(ds, 1):
            out.append({"ma": f"CT_{hinh}_{i:02d}", "hinh": hinh, "loai": loai,
                        "loai_ten": LOAI_CONG_THUC[loai], "hien_thi": hien_thi,
                        "ket_qua": ket_qua, "bieu_thuc": bieu_thuc, "ghi_chu": ghi_chu,
                        "vao": cac_bien_vao(bieu_thuc), "thu_tu": i})
    return out


def ds_dai_luong():
    out = []
    for hinh, ds in DAI_LUONG.items():
        for i, (bien, ky_hieu, ten, kieu) in enumerate(ds):
            out.append({"ma": f"{hinh}.{bien}", "hinh": hinh, "bien": bien, "ky_hieu": ky_hieu,
                        "ten": ten, "kieu": kieu, "thu_tu": i})
    return out
