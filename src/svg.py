"""Vẽ sơ đồ phân cấp tứ giác thành SVG (không cần thư viện ngoài)."""
from html import escape

W_COL, H_ROW, PAD_X, PAD_Y = 200, 105, 110, 45
BOX_W, BOX_H = 176, 44


def _pos(h):
    return PAD_X + h["cot"] * W_COL, PAD_Y + h["cap"] * H_ROW


def so_do(hinh, la_mot, suy_ra=(), ket_luan=(), ban_dau=None, link=True, buoc=()):
    """
    hinh:     list dict {ma, ten, cap, cot}
    la_mot:   list (con, cha)
    suy_ra:   các hình đã suy ra (tô màu nhạt)
    ket_luan: các hình kết luận (tô đậm)
    buoc:     list (tu, den, nhan) — các mũi tên suy luận cần làm nổi bật
    """
    pos = {h["ma"]: _pos(h) for h in hinh}
    max_x = max(x for x, _ in pos.values()) + PAD_X
    max_y = max(y for _, y in pos.values()) + PAD_Y + 10
    suy_ra, ket_luan = set(suy_ra), set(ket_luan)
    canh_suy_luan = {(a, b) for a, b, _ in buoc}

    out = [f'<svg class="so-do" viewBox="0 0 {max_x:.0f} {max_y:.0f}" '
           f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sơ đồ phân cấp tứ giác">',
           '<defs><marker id="mui" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
           'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
           'class="mui"/></marker>'
           '<marker id="mui2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
           'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
           'class="mui-sl"/></marker></defs>']

    # Cạnh LA_MOT: từ hình con (dưới) lên hình cha (trên)
    for con, cha in la_mot:
        (x1, y1), (x2, y2) = pos[con], pos[cha]
        active = con in suy_ra and cha in suy_ra
        sl = (cha, con) in canh_suy_luan
        cls = "canh sl" if sl else ("canh on" if active else "canh")
        out.append(f'<line class="{cls}" x1="{x1:.0f}" y1="{y1 - BOX_H / 2:.0f}" '
                   f'x2="{x2:.0f}" y2="{y2 + BOX_H / 2 + 3:.0f}" '
                   f'marker-end="url(#{"mui2" if sl else "mui"})"/>')

    for h in hinh:
        x, y = pos[h["ma"]]
        cls = "nut"
        if h["ma"] in suy_ra:
            cls += " on"
        if h["ma"] in ket_luan:
            cls += " kl"
        if h["ma"] == ban_dau:
            cls += " bd"
        rect = (f'<rect class="{cls}" x="{x - BOX_W / 2:.0f}" y="{y - BOX_H / 2:.0f}" '
                f'width="{BOX_W}" height="{BOX_H}" rx="10"/>'
                f'<text class="{cls}" x="{x:.0f}" y="{y + 5:.0f}" text-anchor="middle">'
                f'{escape(h["ten"])}</text>')
        if link:
            rect = f'<a href="/hinh/{h["ma"]}">{rect}</a>'
        out.append(f'<g>{rect}</g>')
    out.append("</svg>")
    return "\n".join(out)
