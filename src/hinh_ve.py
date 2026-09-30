"""Hình vẽ minh hoạ (SVG) cho từng loại tứ giác, ghi rõ ký hiệu các đại lượng."""
from html import escape

# pts: A, B, C, D ; canh: (i, j, nhãn) ; cheo: (i, j, nhãn) ; phu: đoạn nét đứt (p, q, nhãn)
# goc: (đỉnh, nhãn) ; vuong: các đỉnh có góc vuông cần đánh dấu
VE = {
    "TU_GIAC": {
        "pts": [(40, 180), (80, 50), (260, 35), (300, 190)],
        "canh": [(0, 1, "a"), (1, 2, "b"), (2, 3, "c"), (3, 0, "d")],
        "cheo": [(0, 2, "d₁"), (1, 3, "d₂", 0.72)], "phi": True,
    },
    "HINH_THANG": {
        "pts": [(30, 180), (310, 180), (230, 55), (90, 55)],
        "canh": [(0, 1, "a"), (2, 3, "b"), (1, 2, "c"), (3, 0, "d")],
        "phu": [((90, 55), (90, 180), "h"), ((60, 117.5), (270, 117.5), "m")],
        "vuong_tai": [((90, 180), (1, 0))],
    },
    "HINH_THANG_CAN": {
        "pts": [(30, 180), (310, 180), (230, 55), (110, 55)],
        "canh": [(0, 1, "a"), (2, 3, "b"), (1, 2, "c"), (3, 0, "c")],
        "cheo": [(0, 2, "d")],
        "phu": [((110, 55), (110, 180), "h")],
        "goc": [(0, "α"), (1, "α")],
        "vuong_tai": [((110, 180), (1, 0))],
    },
    "HINH_THANG_VUONG": {
        "pts": [(40, 180), (300, 180), (200, 55), (40, 55)],
        "canh": [(0, 1, "a"), (2, 3, "b"), (1, 2, "c"), (3, 0, "h")],
        "vuong": [0, 3],
    },
    "HINH_BINH_HANH": {
        "pts": [(30, 180), (240, 180), (310, 55), (100, 55)],
        "canh": [(0, 1, "a"), (3, 0, "b")],
        "cheo": [(0, 2, "d₁"), (1, 3, "d₂")],
        "phu": [((100, 55), (100, 180), "hₐ")],
        "goc": [(0, "α")],
        "vuong_tai": [((100, 180), (1, 0))],
    },
    "HINH_CHU_NHAT": {
        "pts": [(40, 180), (300, 180), (300, 50), (40, 50)],
        "canh": [(0, 1, "a"), (1, 2, "b")],
        "cheo": [(0, 2, "d")],
        "vuong": [0, 1, 2, 3],
    },
    "HINH_THOI": {
        "pts": [(170, 18), (300, 110), (170, 202), (40, 110)],
        "canh": [(0, 1, "a"), (1, 2, "a"), (2, 3, "a"), (3, 0, "a")],
        "cheo": [(1, 3, "d₁"), (0, 2, "d₂")],
        "goc": [(0, "α")],
    },
    "HINH_VUONG": {
        "pts": [(95, 190), (245, 190), (245, 40), (95, 40)],
        "canh": [(0, 1, "a"), (1, 2, "a")],
        "cheo": [(0, 2, "d")],
        "vuong": [0, 1, 2, 3],
    },
    "HINH_DIEU": {
        "pts": [(170, 18), (270, 88), (170, 205), (70, 88)],
        "canh": [(0, 1, "a"), (3, 0, "a"), (1, 2, "b"), (2, 3, "b")],
        "cheo": [(0, 2, "d₁", 0.72), (1, 3, "d₂")],
    },
}


def _tru(p, q): return (p[0] - q[0], p[1] - q[1])
def _chuan(v):
    n = (v[0] ** 2 + v[1] ** 2) ** 0.5 or 1
    return (v[0] / n, v[1] / n)


def _giao(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def ve(ma):
    v = VE.get(ma)
    if not v:
        return ""
    pts = v["pts"]
    g = (sum(p[0] for p in pts) / 4, sum(p[1] for p in pts) / 4)
    out = ['<svg class="hinh-ve" viewBox="0 0 340 225" xmlns="http://www.w3.org/2000/svg" role="img" '
           f'aria-label="Hình vẽ minh hoạ">']
    out.append('<polygon class="hv-da" points="' + " ".join(f"{x},{y}" for x, y in pts) + '"/>')

    def nhan(x, y, s, cls="hv-nhan"):
        out.append(f'<text class="{cls}" x="{x:.0f}" y="{y:.0f}" text-anchor="middle" '
                   f'dominant-baseline="middle">{escape(s)}</text>')

    for c in v.get("cheo", []):
        i, j, s = c[:3]
        t = c[3] if len(c) > 3 else 0.3
        p, q = pts[i], pts[j]
        out.append(f'<line class="hv-net" x1="{p[0]}" y1="{p[1]}" x2="{q[0]}" y2="{q[1]}"/>')
        mx, my = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        d = _chuan((-(q[1] - p[1]), q[0] - p[0]))
        nhan(mx + d[0] * 11, my + d[1] * 11, s, "hv-nhan phu")
    for p, q, s in v.get("phu", []):
        out.append(f'<line class="hv-net" x1="{p[0]}" y1="{p[1]}" x2="{q[0]}" y2="{q[1]}"/>')
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        if p[0] == q[0]:
            nhan(mx + 13, p[1] + (q[1] - p[1]) * 0.3, s, "hv-nhan phu")
        else:
            nhan(mx + 40, my - 10, s, "hv-nhan phu")
    for (x, y), (dx, dy) in v.get("vuong_tai", []):
        k = 9
        out.append(f'<polyline class="hv-vuong" points="{x + dx * k},{y} {x + dx * k},{y - k} {x},{y - k}"/>')
    for i, j, s in v.get("canh", []):
        p, q = pts[i], pts[j]
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        d = _chuan(_tru((mx, my), g))
        nhan(mx + d[0] * 15, my + d[1] * 15, s)
    for k in v.get("vuong", []):
        p = pts[k]
        a = _chuan(_tru(pts[(k + 1) % 4], p)); b = _chuan(_tru(pts[(k - 1) % 4], p))
        s = 11
        out.append(f'<polyline class="hv-vuong" points="{p[0] + a[0] * s:.1f},{p[1] + a[1] * s:.1f} '
                   f'{p[0] + (a[0] + b[0]) * s:.1f},{p[1] + (a[1] + b[1]) * s:.1f} '
                   f'{p[0] + b[0] * s:.1f},{p[1] + b[1] * s:.1f}"/>')
    for k, s in v.get("goc", []):
        p = pts[k]
        a = _chuan(_tru(pts[(k + 1) % 4], p)); b = _chuan(_tru(pts[(k - 1) % 4], p))
        r = 20
        out.append(f'<path class="hv-cung" d="M{p[0] + a[0] * r:.1f},{p[1] + a[1] * r:.1f} '
                   f'A{r},{r} 0 0 {0 if (a[0] * b[1] - a[1] * b[0]) < 0 else 1} '
                   f'{p[0] + b[0] * r:.1f},{p[1] + b[1] * r:.1f}"/>')
        m = _chuan((a[0] + b[0], a[1] + b[1]))
        nhan(p[0] + m[0] * 32, p[1] + m[1] * 32, s, "hv-nhan goc")
    if v.get("phi"):
        o = _giao(pts[0], pts[2], pts[1], pts[3])
        nhan(o[0] + 4, o[1] + 17, "φ", "hv-nhan goc")
    for k, ten in enumerate("ABCD"):
        p = pts[k]
        d = _chuan(_tru(p, g))
        nhan(p[0] + d[0] * 13, p[1] + d[1] * 13, ten, "hv-dinh")
    out.append("</svg>")
    return "\n".join(out)
