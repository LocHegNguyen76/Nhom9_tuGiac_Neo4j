"""
Bộ tính toán diện tích, chu vi và các đại lượng liên quan.

Công thức được lưu trong Neo4j:
    (:Hinh)-[:CO_CONG_THUC]->(:CongThuc)-[:CAN_BIEN]->(:DaiLuong)
                                        -[:TINH_RA]->(:DaiLuong)

Thuật toán (cũng là suy luận tiến, giống bộ nhận dạng hình):
    Tập đại lượng đã biết = các số người dùng nhập.
    Lặp: với mỗi công thức mà mọi biến CAN_BIEN đều đã biết,
         tính giá trị biến TINH_RA; nếu biến đó chưa biết thì ghi nhận
         (một bước giải), nếu đã biết thì so sánh để phát hiện dữ liệu
         không nhất quán.
    Dừng khi không tính thêm được đại lượng nào.
"""
from dataclasses import dataclass, field

from data.cong_thuc import HAM

Q_DAI_LUONG = """
MATCH (:Hinh {ma: $ma})-[:CO_DAI_LUONG]->(d:DaiLuong)
RETURN d.bien AS bien, d.ky_hieu AS ky_hieu, d.ten AS ten, d.kieu AS kieu
ORDER BY d.thu_tu"""

Q_CONG_THUC = """
MATCH (:Hinh {ma: $ma})-[:CO_CONG_THUC]->(c:CongThuc)-[:TINH_RA]->(k:DaiLuong)
RETURN c.ma AS ma, c.loai AS loai, c.loai_ten AS loai_ten, c.hien_thi AS hien_thi,
       c.bieu_thuc AS bieu_thuc, c.ghi_chu AS ghi_chu, k.bien AS ket_qua,
       [(c)-[:CAN_BIEN]->(v:DaiLuong) | v.bien] AS vao
ORDER BY c.thu_tu"""

SAI_SO = 1e-6


class Neo4jCongThuc:
    def __init__(self, run):
        self.run = run

    def dai_luong(self, ma):
        return self.run(Q_DAI_LUONG, ma=ma)

    def cong_thuc(self, ma):
        rows = self.run(Q_CONG_THUC, ma=ma)
        for r in rows:
            r["vao"] = sorted(r["vao"])
        return rows


class MemoryCongThuc:
    """Bản Python thuần (dùng cho kiểm thử)."""

    def __init__(self, CT):
        self.CT = CT

    def dai_luong(self, ma):
        return [{k: d[k] for k in ("bien", "ky_hieu", "ten", "kieu")}
                for d in self.CT.ds_dai_luong() if d["hinh"] == ma]

    def cong_thuc(self, ma):
        return [{k: c[k] for k in ("ma", "loai", "loai_ten", "hien_thi", "bieu_thuc", "ghi_chu", "ket_qua", "vao")}
                for c in self.CT.ds_cong_thuc() if c["hinh"] == ma]


@dataclass
class KetQuaTinh:
    gia_tri: dict = field(default_factory=dict)      # bien -> số
    nguon: dict = field(default_factory=dict)        # bien -> "nhập" | mã công thức
    buoc: list = field(default_factory=list)         # các bước giải
    loi_nhap: list = field(default_factory=list)     # lỗi dữ liệu nhập
    khong_nhat_quan: list = field(default_factory=list)
    khong_ap_dung: list = field(default_factory=list)


def hop_le(kieu, x):
    if kieu == "goc":
        return 0 < x < 180
    return x > 0


def dinh_dang(x):
    if x is None:
        return ""
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    s = f"{x:.4f}".rstrip("0").rstrip(".")
    return s


def tinh(dai_luong, cong_thuc, nhap, max_vong=20):
    """
    dai_luong: list {bien, ky_hieu, ten, kieu}
    cong_thuc: list {ma, hien_thi, bieu_thuc, ket_qua, vao, ...}
    nhap:      dict bien -> số (người dùng nhập)
    """
    kq = KetQuaTinh()
    kieu = {d["bien"]: d["kieu"] for d in dai_luong}
    ky_hieu = {d["bien"]: d["ky_hieu"] for d in dai_luong}

    for bien, x in nhap.items():
        if bien not in kieu:
            continue
        if not hop_le(kieu[bien], x):
            kq.loi_nhap.append(f"{ky_hieu[bien]} = {dinh_dang(x)} không hợp lệ "
                               + ("(góc phải nằm trong khoảng 0° đến 180°)." if kieu[bien] == "goc"
                                  else "(độ dài, diện tích phải lớn hơn 0)."))
            continue
        kq.gia_tri[bien] = float(x)
        kq.nguon[bien] = "nhập"
    if kq.loi_nhap:
        return kq

    da_kiem = set()
    for vong in range(1, max_vong + 1):
        moi = False
        for ct in cong_thuc:
            if not all(v in kq.gia_tri for v in ct["vao"]):
                continue
            kq_bien = ct["ket_qua"]
            if kq_bien in kq.gia_tri and ct["ma"] in da_kiem:
                continue
            try:
                x = float(eval(ct["bieu_thuc"], {"__builtins__": {}},  # noqa: S307 (biểu thức từ CSDL tri thức)
                               {**HAM, **{v: kq.gia_tri[v] for v in ct["vao"]}}))
            except (ValueError, ZeroDivisionError, OverflowError):
                x = None
            if x is None or not hop_le(kieu[kq_bien], x):
                if ct["ma"] not in da_kiem:
                    kq.khong_ap_dung.append({"ct": ct, "ly_do": "dữ liệu không thoả điều kiện của công thức"})
                da_kiem.add(ct["ma"])
                continue
            da_kiem.add(ct["ma"])
            if kq_bien in kq.gia_tri:
                cu = kq.gia_tri[kq_bien]
                if abs(cu - x) > SAI_SO * max(1.0, abs(cu)):
                    kq.khong_nhat_quan.append({"ct": ct, "tinh_duoc": x, "da_co": cu,
                                               "nguon": kq.nguon[kq_bien]})
                continue
            kq.gia_tri[kq_bien] = x
            kq.nguon[kq_bien] = ct["ma"]
            kq.buoc.append({"vong": vong, "ct": ct, "gia_tri": x,
                            "thay_so": {v: kq.gia_tri[v] for v in ct["vao"]}})
            moi = True
        if not moi:
            break
    return kq
