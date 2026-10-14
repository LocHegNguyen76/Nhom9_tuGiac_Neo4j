"""
Nhận diện tính chất của tứ giác ABCD từ toạ độ 4 đỉnh (dùng cho trang Thử thách).

Toạ độ là số nguyên (các đỉnh được bắt dính vào lưới ô vuông), nên các phép
kiểm tra song song, vuông góc, bằng nhau được tính CHÍNH XÁC bằng số nguyên:
    song song      <=> tích có hướng = 0
    vuông góc      <=> tích vô hướng = 0
    bằng nhau      <=> bình phương độ dài bằng nhau
Chỉ phép so sánh góc (góc đối, góc kề đáy, phân giác) dùng số thực với sai số nhỏ.

Kết quả là danh sách mã tính chất (trùng với các nút :TinhChat trong Neo4j),
sau đó được đưa vào bộ suy luận để Neo4j kết luận đây là hình gì.
"""
import math

EPS = 1e-9


def _v(p, q):
    return (q[0] - p[0], q[1] - p[1])


def _cross(u, v):
    return u[0] * v[1] - u[1] * v[0]


def _dot(u, v):
    return u[0] * v[0] + u[1] * v[1]


def _l2(u):
    return u[0] * u[0] + u[1] * u[1]


def _goc(u, v):
    """Góc (độ) giữa hai vectơ."""
    c = _dot(u, v) / math.sqrt(_l2(u) * _l2(v))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def kiem_tra_hop_le(pts):
    """Trả về (True, "") nếu ABCD là tứ giác lồi hợp lệ, ngược lại (False, lý do)."""
    if len(pts) != 4:
        return False, "Cần đúng 4 đỉnh."
    if len({tuple(p) for p in pts}) < 4:
        return False, "Có hai đỉnh trùng nhau."
    canh = [_v(pts[i], pts[(i + 1) % 4]) for i in range(4)]
    tich = [_cross(canh[i], canh[(i + 1) % 4]) for i in range(4)]
    if any(t == 0 for t in tich):
        return False, "Có ba đỉnh liên tiếp thẳng hàng."
    if not (all(t > 0 for t in tich) or all(t < 0 for t in tich)):
        return False, "Tứ giác bị lõm hoặc tự cắt — hãy kéo để được tứ giác lồi."
    return True, ""


def so_do(pts):
    """Độ dài các cạnh, đường chéo và số đo các góc (để hiển thị)."""
    A, B, C, D = pts
    canh = {"AB": _v(A, B), "BC": _v(B, C), "CD": _v(C, D), "DA": _v(D, A)}
    goc = {
        "A": _goc(_v(A, B), _v(A, D)), "B": _goc(_v(B, A), _v(B, C)),
        "C": _goc(_v(C, B), _v(C, D)), "D": _goc(_v(D, C), _v(D, A)),
    }
    return {
        "canh": {k: math.sqrt(_l2(v)) for k, v in canh.items()},
        "cheo": {"AC": math.sqrt(_l2(_v(A, C))), "BD": math.sqrt(_l2(_v(B, D)))},
        "goc": goc,
    }


def tinh_chat(pts):
    """Danh sách mã tính chất (TinhChat.ma) mà tứ giác ABCD thoả mãn."""
    A, B, C, D = [tuple(p) for p in pts]
    AB, BC, CD, DA = _v(A, B), _v(B, C), _v(C, D), _v(D, A)
    AC, BD = _v(A, C), _v(B, D)

    ss_ab_cd = _cross(AB, CD) == 0
    ss_bc_da = _cross(BC, DA) == 0
    eq = lambda u, v: _l2(u) == _l2(v)  # noqa: E731
    g = so_do(pts)["goc"]
    goc_bang = lambda x, y: abs(g[x] - g[y]) < 1e-7  # noqa: E731
    vuong = [_dot(_v(A, B), _v(A, D)) == 0, _dot(_v(B, A), _v(B, C)) == 0,
             _dot(_v(C, B), _v(C, D)) == 0, _dot(_v(D, C), _v(D, A)) == 0]

    def phan_giac(dinh, ke1, ke2, cheo):
        return abs(_goc(_v(dinh, ke1), _v(dinh, cheo)) - _goc(_v(dinh, cheo), _v(dinh, ke2))) < 1e-7

    tc = {
        "SS_1_CAP": ss_ab_cd or ss_bc_da,
        "SS_2_CAP": ss_ab_cd and ss_bc_da,
        "BANG_2_CAP": eq(AB, CD) and eq(BC, DA),
        "SS_VA_BANG": (ss_ab_cd and eq(AB, CD)) or (ss_bc_da and eq(BC, DA)),
        "CANH_BEN_BANG": (ss_ab_cd and eq(BC, DA)) or (ss_bc_da and eq(AB, CD)),
        "CANH_BEN_KHONG_SS": (ss_ab_cd or ss_bc_da) and not (ss_ab_cd and ss_bc_da),
        "HAI_CANH_KE_BANG": eq(AB, BC) or eq(BC, CD) or eq(CD, DA) or eq(DA, AB),
        "HAI_CAP_KE_BANG": (eq(AB, DA) and eq(BC, CD)) or (eq(AB, BC) and eq(CD, DA)),
        "BON_CANH_BANG": eq(AB, BC) and eq(BC, CD) and eq(CD, DA),
        "MOT_GOC_VUONG": sum(vuong) >= 1,
        "BA_GOC_VUONG": sum(vuong) >= 3,
        "GOC_DOI_BANG": goc_bang("A", "C") and goc_bang("B", "D"),
        "GOC_KE_DAY_BANG": (ss_ab_cd and (goc_bang("A", "B") or goc_bang("C", "D")))
                           or (ss_bc_da and (goc_bang("B", "C") or goc_bang("D", "A"))),
        "CHEO_TRUNG_DIEM": A[0] + C[0] == B[0] + D[0] and A[1] + C[1] == B[1] + D[1],
        "CHEO_BANG": _l2(AC) == _l2(BD),
        "CHEO_VUONG_GOC": _dot(AC, BD) == 0,
        "CHEO_PHAN_GIAC": phan_giac(A, B, D, C) or phan_giac(C, B, D, A)
                          or phan_giac(B, A, C, D) or phan_giac(D, A, C, B),
    }
    return [k for k, v in tc.items() if v]


# ---------------------------------------------------------------------------
# Sinh ngẫu nhiên một tứ giác thuộc đúng một loại (dùng cho trang Thử thách)
# Toạ độ nguyên trong lưới 1..31 x 1..22 (giống bảng vẽ trên trang web).
# ---------------------------------------------------------------------------
LUOI_X, LUOI_Y = (1, 31), (1, 22)

# Hướng của cạnh đáy: nằm ngang hoặc nghiêng theo các vectơ nguyên nhỏ
HUONG = [(1, 0), (0, 1), (1, 1), (1, -1), (2, 1), (1, 2), (2, -1), (1, -2),
         (3, 1), (1, 3), (3, -1), (1, -3), (3, 2), (2, 3), (3, -2), (2, -3)]

# Các nhóm vectơ có cùng độ dài (để dựng hình thoi có toạ độ nguyên)
CUNG_DO_DAI = [
    [(5, 0), (0, 5), (3, 4), (4, 3), (-3, 4), (-4, 3)],
    [(4, 2), (2, 4), (-2, 4), (-4, 2)],
    [(6, 3), (3, 6), (-3, 6), (-6, 3)],
    [(3, 1), (1, 3), (-1, 3), (-3, 1)],
    [(6, 2), (2, 6), (-2, 6), (-6, 2)],
    [(3, 2), (2, 3), (-2, 3), (-3, 2)],
    [(6, 4), (4, 6), (-4, 6), (-6, 4)],
    [(5, 5), (7, 1), (1, 7), (-1, 7), (-7, 1), (-5, 5)],
    [(8, 1), (7, 4), (4, 7), (1, 8), (-1, 8), (-4, 7), (-7, 4), (-8, 1)],
]


def _cong(*vs):
    return (sum(v[0] for v in vs), sum(v[1] for v in vs))


def _nhan(k, v):
    return (k * v[0], k * v[1])


def _boi(u, lo, hi, R):
    """Hệ số nguyên m sao cho độ dài m·u nằm trong [lo, hi]."""
    d = math.hypot(*u)
    ms = [m for m in range(1, 40) if lo <= m * d <= hi]
    return R.choice(ms) if ms else max(1, round(lo / d))


def _ung_vien(ma, R):
    u = (1, 0) if R.random() < 0.4 else R.choice(HUONG)
    n = (-u[1], u[0])
    O = (0, 0)
    if ma == "TU_GIAC":
        pts = []
        for a0 in (135, 45, -45, -135):
            a = math.radians(a0 + R.uniform(-20, 20))
            r = R.uniform(5, 10)
            pts.append((round(16 + r * math.cos(a) * 1.3), round(11.5 + r * math.sin(a))))
        return pts
    if ma in ("HINH_THANG", "HINH_THANG_VUONG", "HINH_THANG_CAN"):
        a = _boi(u, 10, 17, R)
        if ma == "HINH_THANG_CAN":
            bs = [b for b in range(1, a) if (a - b) % 2 == 0 and b * math.hypot(*u) >= 4]
        else:
            bs = [b for b in range(1, a) if b * math.hypot(*u) >= 4]
        if not bs:
            return None
        b = R.choice(bs)
        t = _boi(n, 5, 10, R)
        if ma == "HINH_THANG":
            p = R.choice([x for x in range(-2, a - b + 3) if x not in (0, a - b, (a - b) / 2)] or [1])
        elif ma == "HINH_THANG_VUONG":
            p = R.choice([0, a - b])
        else:
            p = (a - b) // 2
        w = _cong(_nhan(p, u), _nhan(t, n))
        return [O, _nhan(a, u), _cong(w, _nhan(b, u)), w]
    if ma in ("HINH_BINH_HANH", "HINH_CHU_NHAT"):
        a = _boi(u, 8, 15, R)
        t = _boi(n, 5, 10, R)
        p = 0 if ma == "HINH_CHU_NHAT" else R.choice([-3, -2, -1, 1, 2, 3])
        w = _cong(_nhan(p, u), _nhan(t, n))
        return [O, _nhan(a, u), _cong(_nhan(a, u), w), w]
    if ma == "HINH_VUONG":
        m = _boi(u, 6, 11, R)
        return [O, _nhan(m, u), _cong(_nhan(m, u), _nhan(m, n)), _nhan(m, n)]
    if ma == "HINH_THOI":
        nhom = R.choice(CUNG_DO_DAI)
        cap = [(v, w) for v in nhom for w in nhom if _cross(v, w) > 0 and _dot(v, w) != 0]
        v, w = R.choice(cap)
        k = max(1, round(R.uniform(6, 9) / math.hypot(*v)))
        v, w = _nhan(k, v), _nhan(k, w)
        return [O, v, _cong(v, w), w]
    if ma == "HINH_DIEU":
        L = _boi(u, 10, 16, R)
        ms = [m for m in range(1, L) if 2 * m != L and 0.15 * L <= m <= 0.85 * L]
        m = R.choice(ms)
        r = _boi(n, 3, 7, R)
        return [O, _cong(_nhan(m, u), _nhan(r, n)), _nhan(L, u), _cong(_nhan(m, u), _nhan(-r, n))]
    return None


def _dat_vao_luoi(pts, R):
    """Dịch hình vào giữa lưới (toạ độ nguyên); None nếu hình quá to."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    lo_x, hi_x = LUOI_X[0] + 1 - min(xs), LUOI_X[1] - 1 - max(xs)
    lo_y, hi_y = LUOI_Y[0] + 1 - min(ys), LUOI_Y[1] - 1 - max(ys)
    if lo_x > hi_x or lo_y > hi_y:
        return None
    gx, gy = (lo_x + hi_x) / 2, (lo_y + hi_y) / 2
    dx = round(min(hi_x, max(lo_x, gx + R.uniform(-2, 2))))
    dy = round(min(hi_y, max(lo_y, gy + R.uniform(-1.5, 1.5))))
    return [(x + dx, y + dy) for x, y in pts]


def sinh_hinh(ma, dung_loai, R=None, so_lan=60):
    """
    Sinh toạ độ một tứ giác thuộc loại `ma`.
    dung_loai(pts) -> bool: hàm kiểm tra cuối cùng (trang web dùng bộ suy luận Neo4j).
    Trả về list 4 điểm hoặc None.
    """
    import random

    R = R or random.Random()
    for _ in range(so_lan):
        pts = _ung_vien(ma, R)
        if not pts:
            continue
        if R.random() < 0.5:                       # lật ngẫu nhiên cho đa dạng
            pts = [(x, -y) for x, y in pts]
        pts = _dat_vao_luoi(pts, R)
        if not pts or not kiem_tra_hop_le(pts)[0]:
            continue
        if dung_loai(pts):
            return [list(p) for p in pts]
    return None
