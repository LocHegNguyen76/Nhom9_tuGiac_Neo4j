"""
Vẽ sơ đồ phân cấp tứ giác thành SVG (trang Nhận dạng và trang tra cứu một hình).

- Mỗi hình vẽ bằng chính hình đó (dùng chung hình vẽ với trang Đồ thị tri thức).
- Mũi tên đi từ hình tổng quát xuống hình đặc biệt hơn (theo quan hệ LA_MOT).
- Mỗi mũi tên có điểm đi/đến riêng trên cạnh của ô và là đường cong mềm,
  nên các mũi tên không dồn vào một điểm và ít cắt nhau.
"""
from html import escape

from src.so_do_tri_thuc import COT_RIENG, ve_bieu_tuong

NUT_W, NUT_H = 150, 90           # kích thước một ô hình
COT_W = 188                      # khoảng cách giữa hai cột
KHOANG_TANG = 62                 # khoảng trống giữa hai tầng
LE = 18
TI_LE_HINH = 0.6                 # hình vẽ 120x80 thu nhỏ còn 72x48
CACH_CONG = 20                   # khoảng cách giữa các điểm nối trên cùng một cạnh ô


def _vi_tri(hinh):
    cot = {h["ma"]: COT_RIENG.get(h["ma"], h["cot"]) for h in hinh}
    min_cot = min(cot.values())
    return {h["ma"]: (LE + NUT_W / 2 + (cot[h["ma"]] - min_cot) * COT_W,
                      LE + 14 + NUT_H / 2 + h["cap"] * (NUT_H + KHOANG_TANG)) for h in hinh}


def _cong(ds, tam, lay_x):
    """Chia các điểm nối dọc theo cạnh ô, sắp theo vị trí ngang của đầu bên kia."""
    ds = sorted(ds, key=lay_x)
    n = len(ds)
    return {k: tam + (i - (n - 1) / 2) * CACH_CONG for i, k in enumerate(ds)}


def so_do(hinh, la_mot, suy_ra=(), ket_luan=(), ban_dau=None, link=True, buoc=(), con_chau=()):
    """
    hinh:     list dict {ma, ten, cap, cot}
    la_mot:   list (con, cha)
    suy_ra:   các hình đã suy ra được / hình tổng quát hơn (tô xanh nhạt)
    ket_luan: các hình kết luận / hình đang xem (viền xanh đậm)
    ban_dau:  hình ban đầu (viền xanh lá)
    buoc:     list (tu, den, ma_dau_hieu) — các bước suy luận cần làm nổi bật
    con_chau: các hình đặc biệt hơn (tô xanh lá nhạt, dùng ở trang tra cứu)
    """
    pos = _vi_tri(hinh)
    W = max(x for x, _ in pos.values()) + NUT_W / 2 + LE
    H = max(y for _, y in pos.values()) + NUT_H / 2 + LE
    suy_ra, ket_luan, con_chau = set(suy_ra), set(ket_luan), set(con_chau)
    sang = suy_ra | ket_luan | ({ban_dau} if ban_dau else set())
    canh = [(cha, con) for con, cha in la_mot if cha in pos and con in pos]

    # Bước suy luận: trên mũi tên LA_MOT thì tô mũi tên, còn lại ghi mã dấu hiệu cạnh ô kết luận
    dh_canh, dh_nut = {}, {}
    for tu, den, ma in buoc:
        if (tu, den) in canh:
            dh_canh.setdefault((tu, den), []).append(ma)
        else:
            dh_nut.setdefault(den, []).append(ma)

    di = {}
    den = {}
    for cha, con in canh:
        di.setdefault(cha, []).append((cha, con))
        den.setdefault(con, []).append((cha, con))
    cong_di, cong_den = {}, {}
    for m, ds in di.items():
        cong_di.update(_cong(ds, pos[m][0], lambda c: pos[c[1]][0]))
    for m, ds in den.items():
        cong_den.update(_cong(ds, pos[m][0], lambda c: pos[c[0]][0]))

    out = [f'<svg class="so-do" viewBox="0 0 {W:.0f} {H:.0f}" xmlns="http://www.w3.org/2000/svg" '
           f'role="img" aria-label="Sơ đồ phân cấp tứ giác">',
           '<defs>'
           '<marker id="sd2-mui" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" '
           'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="mui"/></marker>'
           '<marker id="sd2-mui-on" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" '
           'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="mui-on"/></marker>'
           '<marker id="sd2-mui-sl" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" '
           'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="mui-sl"/></marker>'
           '<marker id="sd2-mui-cc" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" '
           'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="mui-cc"/></marker>'
           '</defs>']

    # Mũi tên: thường vẽ trước, nổi bật vẽ sau cho nằm trên
    nhan_dh = []
    ds_canh = []
    for cha, con in canh:
        if (cha, con) in dh_canh:
            loai = "sl"
        elif cha in sang and con in sang:
            loai = "on"
        elif con in con_chau and (cha in con_chau or cha in ket_luan):
            loai = "cc"
        else:
            loai = ""
        ds_canh.append((loai, cha, con))
    thu_tu = {"": 0, "cc": 1, "on": 2, "sl": 3}
    for loai, cha, con in sorted(ds_canh, key=lambda c: thu_tu[c[0]]):
        x1, y1 = cong_di[(cha, con)], pos[cha][1] + NUT_H / 2
        x2, y2 = cong_den[(cha, con)], pos[con][1] - NUT_H / 2 - 2
        k = (y2 - y1) * 0.5
        mui = {"": "sd2-mui", "on": "sd2-mui-on", "sl": "sd2-mui-sl", "cc": "sd2-mui-cc"}[loai]
        out.append(f'<path class="canh {loai}" d="M{x1:.1f},{y1:.1f} C{x1:.1f},{y1 + k:.1f} '
                   f'{x2:.1f},{y2 - k:.1f} {x2:.1f},{y2:.1f}" marker-end="url(#{mui})"/>')
        if loai == "sl":
            nhan_dh.append(((x1 + x2) / 2, (y1 + y2) / 2, ", ".join(dh_canh[(cha, con)])))

    for x, y, chu in nhan_dh:
        w = len(chu) * 7.2 + 12
        out.append(f'<g class="nhan-dh"><rect x="{x - w / 2:.1f}" y="{y - 10:.1f}" width="{w:.1f}" height="20" rx="10"/>'
                   f'<text x="{x:.1f}" y="{y + 4.5:.1f}" text-anchor="middle">{escape(chu)}</text></g>')

    # Các ô hình
    for h in hinh:
        ma = h["ma"]
        x, y = pos[ma]
        cls = "nut"
        if ma in suy_ra:
            cls += " on"
        if ma in con_chau:
            cls += " cc"
        if ma in ket_luan:
            cls += " kl"
        if ma == ban_dau:
            cls += " bd"
        hinh_ve = ve_bieu_tuong(ma, 0, 0)
        g = (f'<rect class="{cls}" x="{x - NUT_W / 2:.1f}" y="{y - NUT_H / 2:.1f}" width="{NUT_W}" '
             f'height="{NUT_H}" rx="12"/>'
             f'<g class="hinh-nho{" mo" if cls == "nut" and sang else ""}" '
             f'transform="translate({x - 60 * TI_LE_HINH:.1f},{y - NUT_H / 2 + 8:.1f}) scale({TI_LE_HINH})">'
             f'{hinh_ve}</g>'
             f'<text class="{cls}" x="{x:.1f}" y="{y + NUT_H / 2 - 11:.1f}" text-anchor="middle">{escape(h["ten"])}</text>')
        if ma in dh_nut:
            chu = ", ".join(dh_nut[ma])
            w = len(chu) * 7.2 + 12
            g += (f'<g class="nhan-dh"><rect x="{x + NUT_W / 2 - w + 6:.1f}" y="{y - NUT_H / 2 - 12:.1f}" '
                  f'width="{w:.1f}" height="20" rx="10"/><text x="{x + NUT_W / 2 - w / 2 + 6:.1f}" '
                  f'y="{y - NUT_H / 2 + 2.5:.1f}" text-anchor="middle">{escape(chu)}</text></g>')
        g = f'<g class="o-hinh"><title>{escape(h["ten"])}</title>{g}</g>'
        if link:
            g = f'<a href="/hinh/{ma}">{g}</a>'
        out.append(g)
    out.append("</svg>")
    return "\n".join(out)
