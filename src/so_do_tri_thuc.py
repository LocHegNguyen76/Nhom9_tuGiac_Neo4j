"""
Sơ đồ tri thức dạng hình ảnh (trang Đồ thị tri thức).

- Mỗi nút :Hinh được vẽ bằng chính hình tứ giác đó, có ký hiệu cạnh bằng nhau,
  cạnh song song và góc vuông.
- Mỗi mũi tên đi từ hình tổng quát (cha) xuống hình đặc biệt (con) theo quan hệ LA_MOT,
  trên mũi tên ghi điều kiện cần thêm, lấy từ các nút :DauHieu trong Neo4j:
      (d:DauHieu)-[:AP_DUNG_CHO]->(cha), (d)-[:KET_LUAN]->(con), (d)-[:CAN]->(:TinhChat)
  Nếu không có dấu hiệu đi thẳng từ cha sang con thì dùng dấu hiệu từ hình tổ tiên gần nhất
  của cha (ví dụ từ “Tứ giác” sang “Hình bình hành” cho mũi tên Hình thang -> Hình bình hành).
"""
import json
from html import escape
from itertools import permutations

# ---------------------------------------------------------------------------
# Hình vẽ từng loại tứ giác trong khung 120 x 80
#   ss:    (i, j, số vạch)  cặp cạnh song song, mũi tên nhỏ chỉ theo hướng i -> j
#   bang:  (i, j, số vạch)  cạnh bằng nhau
#   vuong: đỉnh có góc vuông
# ---------------------------------------------------------------------------
BIEU_TUONG = {
    "TU_GIAC": {"pts": [(12, 72), (34, 14), (96, 6), (112, 66)]},
    "HINH_THANG": {"pts": [(6, 70), (114, 70), (90, 14), (32, 14)],
                   "ss": [(0, 1, 1), (3, 2, 1)]},
    "HINH_THANG_VUONG": {"pts": [(14, 70), (112, 70), (80, 14), (14, 14)],
                         "ss": [(0, 1, 1), (3, 2, 1)], "vuong": [0, 3]},
    "HINH_THANG_CAN": {"pts": [(6, 70), (114, 70), (86, 14), (34, 14)],
                       "ss": [(0, 1, 1), (3, 2, 1)], "bang": [(1, 2, 1), (3, 0, 1)]},
    "HINH_BINH_HANH": {"pts": [(6, 70), (84, 70), (114, 14), (36, 14)],
                       "ss": [(0, 1, 1), (3, 2, 1), (0, 3, 2), (1, 2, 2)]},
    "HINH_CHU_NHAT": {"pts": [(12, 70), (108, 70), (108, 12), (12, 12)],
                      "bang": [(0, 1, 1), (3, 2, 1), (1, 2, 2), (0, 3, 2)], "vuong": [0, 1, 2, 3]},
    "HINH_THOI": {"pts": [(60, 4), (110, 40), (60, 76), (10, 40)],
                  "bang": [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 0, 1)]},
    "HINH_VUONG": {"pts": [(30, 72), (90, 72), (90, 12), (30, 12)],
                   "bang": [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 0, 1)], "vuong": [0, 1, 2, 3]},
    "HINH_DIEU": {"pts": [(60, 4), (94, 28), (60, 78), (26, 28)],
                  "bang": [(0, 1, 1), (3, 0, 1), (1, 2, 2), (2, 3, 2)]},
}

NUT_W, NUT_H = 172, 128          # kích thước một nút
COT_W = 290                      # khoảng cách giữa hai cột
LE = 24                          # lề
CO_CHU = 13                      # cỡ chữ nhãn trên mũi tên
DONG_H = 17                      # chiều cao một dòng nhãn
TOI_DA_KY_TU = 40                # ngắt dòng nhãn


def _chuan(x, y):
    n = (x * x + y * y) ** 0.5 or 1.0
    return x / n, y / n


def ve_bieu_tuong(ma, ox, oy):
    """SVG của hình `ma` vẽ trong khung 120x80 đặt tại (ox, oy)."""
    bt = BIEU_TUONG.get(ma)
    if not bt:
        return ""
    P = [(ox + x, oy + y) for x, y in bt["pts"]]
    out = ['<polygon class="sd-hinh" points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in P) + '"/>']
    for i, j, n in bt.get("bang", []):          # vạch đánh dấu cạnh bằng nhau
        (x1, y1), (x2, y2) = P[i], P[j]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        tx, ty = _chuan(x2 - x1, y2 - y1)
        nx, ny = -ty, tx
        for k in range(n):
            d = (k - (n - 1) / 2) * 4
            cx, cy = mx + tx * d, my + ty * d
            out.append(f'<line class="sd-dau" x1="{cx - nx * 5:.1f}" y1="{cy - ny * 5:.1f}" '
                       f'x2="{cx + nx * 5:.1f}" y2="{cy + ny * 5:.1f}"/>')
    for i, j, n in bt.get("ss", []):            # mũi tên nhỏ đánh dấu cạnh song song
        (x1, y1), (x2, y2) = P[i], P[j]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        tx, ty = _chuan(x2 - x1, y2 - y1)
        nx, ny = -ty, tx
        for k in range(n):
            d = (k - (n - 1) / 2) * 5 + 2
            cx, cy = mx + tx * d, my + ty * d
            out.append(f'<polyline class="sd-dau" points="{cx - tx * 4 + nx * 4:.1f},{cy - ty * 4 + ny * 4:.1f} '
                       f'{cx:.1f},{cy:.1f} {cx - tx * 4 - nx * 4:.1f},{cy - ty * 4 - ny * 4:.1f}"/>')
    for k in bt.get("vuong", []):               # ký hiệu góc vuông
        p = P[k]
        a = _chuan(P[(k + 1) % 4][0] - p[0], P[(k + 1) % 4][1] - p[1])
        b = _chuan(P[(k - 1) % 4][0] - p[0], P[(k - 1) % 4][1] - p[1])
        s = 8
        out.append(f'<polyline class="sd-vuong" points="{p[0] + a[0] * s:.1f},{p[1] + a[1] * s:.1f} '
                   f'{p[0] + (a[0] + b[0]) * s:.1f},{p[1] + (a[1] + b[1]) * s:.1f} '
                   f'{p[0] + b[0] * s:.1f},{p[1] + b[1] * s:.1f}"/>')
    return "".join(out)


# ---------------------------------------------------------------------------
# Điều kiện trên từng mũi tên
# ---------------------------------------------------------------------------
def canh_suy_ra(hinh, la_mot, dau_hieu):
    """
    hinh:     list dict {ma, ...}
    la_mot:   list (con, cha)
    dau_hieu: list dict {ma, ten, tu, den, can: [{ma, ngan, thu_tu}]}   (chỉ dấu hiệu có kết luận)
    Trả về list dict {tu, den, dau_hieu: [...], gian_tiep: bool}, mũi tên đi từ cha xuống con.
    """
    cha_cua = {}
    for con, cha in la_mot:
        cha_cua.setdefault(con, []).append(cha)

    def to_tien_gan_nhat(ma):
        """Các tầng tổ tiên của `ma`, gần trước xa sau (không gồm chính nó)."""
        tang, da_gap, hien = [], {ma}, [ma]
        while hien:
            ke = []
            for h in hien:
                for c in cha_cua.get(h, []):
                    if c not in da_gap:
                        da_gap.add(c)
                        ke.append(c)
            if ke:
                tang.append(ke)
            hien = ke
        return tang

    theo_cap = {}
    for d in dau_hieu:
        theo_cap.setdefault((d["tu"], d["den"]), []).append(d)

    ds = []
    for con, cha in la_mot:
        truc_tiep = theo_cap.get((cha, con), [])
        if truc_tiep:
            ds.append({"tu": cha, "den": con, "dau_hieu": truc_tiep, "gian_tiep": False})
            continue
        dh = []
        for tang in to_tien_gan_nhat(cha):
            for a in tang:
                dh += theo_cap.get((a, con), [])
            if dh:
                break
        ds.append({"tu": cha, "den": con, "dau_hieu": dh, "gian_tiep": True})
    return ds


def _ngat_dong(chu, dau, thut="    "):
    """Ngắt `chu` thành nhiều dòng; dòng đầu bắt đầu bằng `dau`, các dòng sau thụt vào."""
    dong, hang = [], dau
    for w in chu.split():
        if len(hang) + 1 + len(w) > TOI_DA_KY_TU and hang.strip("+ và"):
            dong.append(hang)
            hang = thut + w
        else:
            hang = f"{hang} {w}"
    dong.append(hang)
    return dong


def _dong_nhan(dau_hieu):
    """Các dòng chữ ghi trên mũi tên: mỗi dấu hiệu bắt đầu bằng dấu +, điều kiện thứ hai trở đi bắt đầu bằng “và”."""
    dong = []
    for d in dau_hieu:
        can = sorted(d["can"], key=lambda c: c.get("thu_tu", 0))
        for i, c in enumerate(can):
            dong += _ngat_dong(c["ngan"], "+" if i == 0 else "   và")
    return dong


# ---------------------------------------------------------------------------
# Vẽ toàn bộ sơ đồ
# ---------------------------------------------------------------------------
def _cat_hop(cx, cy, tx, ty, w, h, gap):
    """Điểm trên cạnh hộp (tâm cx, cy) theo hướng (tx, ty), lùi thêm gap."""
    kx = (w / 2) / abs(tx) if tx else float("inf")
    ky = (h / 2) / abs(ty) if ty else float("inf")
    k = min(kx, ky) + gap
    return cx + tx * k, cy + ty * k


def _giao_hcn(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def _doan_cat_hcn(p, q, r):
    """Đoạn thẳng pq có cắt hình chữ nhật r = (x1, y1, x2, y2) không (lấy mẫu)."""
    for k in range(21):
        t = k / 20
        x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        if r[0] <= x <= r[2] and r[1] <= y <= r[3]:
            return True
    return False


KHOANG_MIN = 110                 # khoảng trống tối thiểu giữa hai tầng hình

# Cột riêng cho sơ đồ hình ảnh (thoáng hơn cho nhãn); hình khác dùng thuộc tính `cot` trong Neo4j
COT_RIENG = {"TU_GIAC": 2.0, "HINH_THANG": 1.35, "HINH_DIEU": 3.7, "HINH_THANG_VUONG": 0.0,
             "HINH_THANG_CAN": 1.35, "HINH_BINH_HANH": 2.65, "HINH_CHU_NHAT": 1.45,
             "HINH_THOI": 3.2, "HINH_VUONG": 2.35}


def _kich_thuoc_nhan(c):
    dong = _dong_nhan(c["dau_hieu"])
    if not dong:
        return None
    return dong, max(len(s) for s in dong) * CO_CHU * 0.6 + 18, len(dong) * DONG_H + 10


def _bo_tri(hinh, canh, khoang, kich_thuoc):
    """Đặt các hình và nhãn với khoảng cách giữa các tầng cho trước.
    Trả về vị trí, đoạn mũi tên, nhãn, kích thước và các tầng còn chỗ nhãn bị đè."""
    cot = {h["ma"]: COT_RIENG.get(h["ma"], h["cot"]) for h in hinh}
    min_cot = min(cot.values())
    y, y_cap = LE + NUT_H / 2, {}
    for c in sorted({h["cap"] for h in hinh}):
        y_cap[c] = y
        y += NUT_H + khoang[c]
    cap = {h["ma"]: h["cap"] for h in hinh}
    pos = {h["ma"]: (LE + NUT_W / 2 + (cot[h["ma"]] - min_cot) * COT_W, y_cap[h["cap"]]) for h in hinh}
    W = max(x for x, _ in pos.values()) + NUT_W / 2 + LE
    H = max(y for _, y in pos.values()) + NUT_H / 2 + LE
    hop_nut = [(x - NUT_W / 2 - 6, y - NUT_H / 2 - 6, x + NUT_W / 2 + 6, y + NUT_H / 2 + 6)
               for x, y in pos.values()]

    doan = []
    for c in canh:
        (x1, y1), (x2, y2) = pos[c["tu"]], pos[c["den"]]
        tx, ty = _chuan(x2 - x1, y2 - y1)
        doan.append((_cat_hop(x1, y1, tx, ty, NUT_W, NUT_H, 4), _cat_hop(x2, y2, -tx, -ty, NUT_W, NUT_H, 7)))

    # Vùng quanh đầu mũi tên: nhãn không được che
    hop_mui = [(q[0] - 14, q[1] - 16, q[0] + 14, q[1] + 4) for _, q in doan]

    # Thử nhiều vị trí dọc mũi tên (và lệch sang hai bên một chút), chọn chỗ không đè lên hình,
    # nhãn khác, đầu mũi tên và ít cắt mũi tên khác nhất. Thử vài thứ tự đặt nhãn, lấy cách tốt nhất.
    lon_truoc = sorted(range(len(canh)), key=lambda k: -(kich_thuoc[k][2] if kich_thuoc[k] else 0))
    tot_nhat = None
    for dau in permutations(lon_truoc[:3]):
        thu_tu = list(dau) + lon_truoc[3:]
        kq = _dat_nhan(canh, doan, kich_thuoc, thu_tu, hop_nut, hop_mui, W, cap)
        if tot_nhat is None or kq[0] < tot_nhat[0]:
            tot_nhat = kq
    _, nhan, va_cham = tot_nhat
    return pos, doan, nhan, W, H, va_cham


def _dat_nhan(canh, doan, kich_thuoc, thu_tu, hop_nut, hop_mui, W, cap):
    nhan, va_cham, tong = [None] * len(canh), set(), 0
    for k in thu_tu:
        if not kich_thuoc[k]:
            continue
        dong, w, h = kich_thuoc[k]
        (px, py), (qx, qy) = doan[k]
        tot = None
        for i in range(15):
            t = 0.15 + i * 0.05
            for lech in (0, -0.3, 0.3):
                cx, cy = px + (qx - px) * t + lech * w, py + (qy - py) * t
                r = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
                diem = abs(t - 0.5) * 4 + abs(lech) * 6
                diem += 1000 * sum(_giao_hcn(r, b) for b in hop_nut)
                diem += 1000 * sum(_giao_hcn(r, n["hop"]) for n in nhan if n)
                diem += 1000 * sum(_giao_hcn(r, b) for b in hop_mui)
                diem += 150 * sum(_doan_cat_hcn(*doan[j], r) for j in range(len(doan)) if j != k)
                if r[0] < 2 or r[2] > W - 2:
                    diem += 1000
                if tot is None or diem < tot[0]:
                    tot = (diem, cx, cy, r)
        diem, cx, cy, r = tot
        tong += diem
        if diem >= 1000:
            va_cham.add(cap[canh[k]["tu"]])
        nhan[k] = {"dong": dong, "x": cx, "y": cy, "w": w, "h": h,
                   "hop": (r[0] - 5, r[1] - 5, r[2] + 5, r[3] + 5)}
    return tong, nhan, va_cham


_BO_NHO = {}


def ve_so_do(hinh, canh, link=True):
    """hinh: list dict {ma, ten, cap, cot}; canh: kết quả của canh_suy_ra().
    Việc dàn trang mất khoảng một giây nên kết quả được nhớ lại theo dữ liệu đầu vào."""
    khoa = json.dumps([hinh, canh, link], sort_keys=True, ensure_ascii=False, default=str)
    if khoa not in _BO_NHO:
        if len(_BO_NHO) > 20:
            _BO_NHO.clear()
        _BO_NHO[khoa] = _ve_so_do(hinh, canh, link)
    return _BO_NHO[khoa]


def _ve_so_do(hinh, canh, link):
    kich_thuoc = [_kich_thuoc_nhan(c) for c in canh]
    khoang = {c: KHOANG_MIN for c in {h["cap"] for h in hinh}}
    for _ in range(25):        # tầng nào nhãn còn bị đè thì nới rộng khoảng cách tầng đó
        pos, doan, nhan, W, H, va_cham = _bo_tri(hinh, canh, khoang, kich_thuoc)
        if not va_cham:
            break
        for c in va_cham:
            khoang[c] += 16

    out = [f'<svg class="so-do-tt" viewBox="0 0 {W:.0f} {H:.0f}" xmlns="http://www.w3.org/2000/svg" '
           f'role="img" aria-label="Sơ đồ tri thức: từ hình này suy ra hình kia">',
           '<defs><marker id="sd-mui" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
           'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="sd-mui"/></marker></defs>']

    # Mũi tên
    for k, c in enumerate(canh):
        (px, py), (qx, qy) = doan[k]
        goi_y = "\n".join(f'{d["ma"]}: {d["ten"]}' for d in c["dau_hieu"])
        if c["gian_tiep"] and c["dau_hieu"]:
            goi_y += "\n(dấu hiệu áp dụng cho mọi tứ giác)"
        out.append(f'<g class="sd-canh"><title>{escape(goi_y)}</title>'
                   f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{qx:.1f}" y2="{qy:.1f}" marker-end="url(#sd-mui)"/></g>')

    # Nhãn điều kiện (vẽ sau mũi tên để nằm trên)
    for k, n in enumerate(nhan):
        if not n:
            continue
        c = canh[k]
        goi_y = "\n".join(f'{d["ma"]}: {d["ten"]}' for d in c["dau_hieu"])
        if link:
            goi_y += "\n— Bấm để thử kéo hình trong trang Thử thách"
        x0, y0 = n["x"] - n["w"] / 2, n["y"] - n["h"] / 2
        s = [f'<g class="sd-nhan"><title>{escape(goi_y)}</title>'
             f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{n["w"]:.1f}" height="{n["h"]:.1f}" rx="8"/>']
        for i, dong in enumerate(n["dong"]):
            s.append(f'<text x="{x0 + 9:.1f}" y="{y0 + 5 + DONG_H * (i + 0.72):.1f}">{escape(dong)}</text>')
        s.append("</g>")
        g = "".join(s)
        if link:     # bấm vào nhãn: mở trang Thử thách với đề "từ hình cha tạo thành hình con"
            g = (f'<a href="/thu-thach?tu={c["tu"]}&amp;den={c["den"]}" '
                 f'aria-label="Thử thách: từ {c["tu"]} tạo thành {c["den"]}">{g}</a>')
        out.append(g)

    # Các nút: hình vẽ + tên
    for h in hinh:
        x, y = pos[h["ma"]]
        g = (f'<rect class="sd-nut" x="{x - NUT_W / 2:.1f}" y="{y - NUT_H / 2:.1f}" width="{NUT_W}" '
             f'height="{NUT_H}" rx="14"/>'
             + ve_bieu_tuong(h["ma"], x - 60, y - NUT_H / 2 + 10)
             + f'<text class="sd-ten" x="{x:.1f}" y="{y + NUT_H / 2 - 13:.1f}" text-anchor="middle">'
               f'{escape(h["ten"])}</text>')
        g = f'<g class="sd-o"><title>{escape(h["ten"])}</title>{g}</g>'
        if link:
            g = f'<a href="/hinh/{h["ma"]}">{g}</a>'
        out.append(g)
    out.append("</svg>")
    return "\n".join(out)
