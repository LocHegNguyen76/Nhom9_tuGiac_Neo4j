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
