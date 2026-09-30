"""
Ứng dụng web: Mô hình hoá tứ giác trong hình học phẳng với Neo4j.

Chạy:  python app.py      rồi mở http://localhost:5000
"""
from flask import Flask, abort, jsonify, render_template, request

from data.cong_thuc import VI_DU_TINH
from data.knowledge import VI_DU
from src import config, db, repo
from src.engine import Neo4jStore, suy_luan
from src.hinh_ve import ve
from src.svg import so_do
from src.tinh_toan import Q_CONG_THUC, Neo4jCongThuc, dinh_dang, tinh

app = Flask(__name__)
app.json.ensure_ascii = False
app.json.compact = False

# Có thể thay bằng hàm chạy truy vấn khác (dùng khi kiểm thử)
RUN = db.run


class Neo4jOffline(Exception):
    pass


def q(cypher, **params):
    try:
        return RUN(cypher, **params)
    except Exception as e:  # noqa: BLE001
        raise Neo4jOffline(str(e)) from e


def thu_tu_tinh_chat():
    """Thứ tự chuẩn của tính chất (theo thuộc tính thu_tu trong Neo4j) để hiển thị ổn định."""
    ds = q(repo.Q_DS_TINH_CHAT)
    tt = {}
    for i, t in enumerate(ds):
        tt[t["ma"]] = i
        tt[t["ten"]] = i
    return ds, tt


def sap_xep(ds, tt):
    return sorted(ds, key=lambda x: tt.get(x, 999))


def du_lieu_chung():
    hinh = q(repo.Q_DS_HINH)
    if not hinh:
        raise Neo4jOffline("Cơ sở dữ liệu chưa có tri thức. Hãy chạy: python -m src.seed")
    la_mot = [(r["con"], r["cha"]) for r in q(repo.Q_DS_LA_MOT)]
    return hinh, la_mot


@app.errorhandler(Neo4jOffline)
def offline(e):
    return render_template("offline.html", loi=str(e), uri=config.NEO4J_URI), 503


@app.context_processor
def inject():
    return {"neo4j_uri": config.NEO4J_URI}


@app.template_filter("so")
def loc_so(x):
    return dinh_dang(x)


DON_VI = ["", "mm", "cm", "dm", "m", "km"]


def nhom_cong_thuc(ds):
    """Gom công thức theo loại (Diện tích, Chu vi, ...) giữ nguyên thứ tự."""
    nhom = {}
    for c in ds:
        nhom.setdefault(c["loai_ten"], []).append(c)
    uu_tien = ["Diện tích", "Chu vi"]
    return dict(sorted(nhom.items(), key=lambda kv: (uu_tien.index(kv[0]) if kv[0] in uu_tien else 9)))


def doc_so(s):
    s = (s or "").strip().replace(",", ".")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return "loi"


@app.route("/")
def nhan_dang():
    hinh, la_mot = du_lieu_chung()
    ten_hinh = {h["ma"]: h["ten"] for h in hinh}
    tinh_chat, tt = thu_tu_tinh_chat()
    ten_tc = {t["ma"]: t["ten"] for t in tinh_chat}
    nhom = {}
    for t in tinh_chat:
        nhom.setdefault(t["nhom_ten"], []).append(t)

    ban_dau = request.args.get("hinh", "TU_GIAC")
    if ban_dau not in ten_hinh:
        ban_dau = "TU_GIAC"
    chon = [t for t in request.args.getlist("tc") if t in ten_tc]
    da_gui = "hinh" in request.args

    kq = store = None
    if da_gui:
        store = Neo4jStore(q)
        kq = suy_luan(store, ban_dau, chon)
        for b in kq.buoc:
            b.can = sap_xep(b.can, tt)
        gt = {t: v for t, v in kq.tinh_chat.items() if v == "giả thiết"}
        kq.tinh_chat = {**gt, **{t: kq.tinh_chat[t] for t in sap_xep(kq.tinh_chat, tt) if t not in gt}}

    ct_kl = None
    if kq and len(kq.ket_luan) == 1 and not kq.mau_thuan:
        ct_kl = nhom_cong_thuc(Neo4jCongThuc(q).cong_thuc(kq.ket_luan[0]))
    svg = so_do(hinh, la_mot,
                suy_ra=kq.hinh_suy_ra if kq else (),
                ket_luan=kq.ket_luan if kq else (),
                ban_dau=ban_dau if kq else None)
    return render_template("nhan_dang.html", hinh=hinh, nhom=nhom, ban_dau=ban_dau,
                           chon=chon, kq=kq, store=store, ten_hinh=ten_hinh,
                           ten_tc=ten_tc, svg=svg, ct_kl=ct_kl)


@app.route("/hinh/<ma>")
def tra_cuu(ma):
    hinh, la_mot = du_lieu_chung()
    rows = q(repo.Q_CHI_TIET_HINH, ma=ma)
    if not rows:
        abort(404)
    ct = rows[0]
    cot = {h["ma"]: h["cot"] for h in hinh}
    ct["cha"] = sorted([c for c in ct["cha"] if c], key=lambda c: cot[c["ma"]])
    ct["con"] = sorted([c for c in ct["con"] if c], key=lambda c: cot[c["ma"]])
    ten = ct["hinh"]["ten"]
    _, tt = thu_tu_tinh_chat()
    tinh_chat = q(repo.Q_TINH_CHAT_CUA_HINH, ma=ma, ten=ten)
    nhan_biet = q(repo.Q_DAU_HIEU_NHAN_BIET, ma=ma)
    di_tiep = q(repo.Q_DAU_HIEU_DI_TIEP, ma=ma)
    for d in nhan_biet + di_tiep:
        d["can"] = sap_xep(d["can"], tt)
    for t in tinh_chat:
        t["tu_hinh"] = sorted(t["tu_hinh"])
    svg = so_do(hinh, la_mot, suy_ra=Neo4jStore(q).to_tien({ma}), ket_luan=[ma])
    cong_thuc = nhom_cong_thuc(Neo4jCongThuc(q).cong_thuc(ma))
    return render_template("hinh.html", ct=ct, tinh_chat=tinh_chat, nhan_biet=nhan_biet,
                           di_tiep=di_tiep, svg=svg, hinh=hinh, cong_thuc=cong_thuc, hinh_ve=ve(ma))


@app.route("/tinh-toan")
def tinh_toan():
    hinh, _ = du_lieu_chung()
    ten_hinh = {h["ma"]: h["ten"] for h in hinh}
    ma = request.args.get("hinh", "HINH_CHU_NHAT")
    if ma not in ten_hinh:
        ma = "HINH_CHU_NHAT"
    kho = Neo4jCongThuc(q)
    dai_luong = kho.dai_luong(ma)
    cong_thuc = kho.cong_thuc(ma)
    don_vi = request.args.get("dv", "cm")
    if don_vi not in DON_VI:
        don_vi = "cm"

    gia_tri_form, nhap, loi_dinh_dang = {}, {}, []
    if request.args.get("vd"):
        gia_tri_form = {k: dinh_dang(v) for k, v in VI_DU_TINH.get(ma, {}).items()}
    else:
        gia_tri_form = {d["bien"]: request.args.get(d["bien"], "") for d in dai_luong}
    ky_hieu = {d["bien"]: d["ky_hieu"] for d in dai_luong}
    for bien, chuoi in gia_tri_form.items():
        x = doc_so(chuoi)
        if x == "loi":
            loi_dinh_dang.append(f"“{chuoi}” không phải là số ({ky_hieu[bien]}).")
        elif x is not None:
            nhap[bien] = x

    kq = None
    da_tinh = "tinh" in request.args or request.args.get("vd")
    if da_tinh and not loi_dinh_dang:
        kq = tinh(dai_luong, cong_thuc, nhap)
    ct_theo_ma = {c["ma"]: c for c in cong_thuc}
    can_cho = {bien: [[ky_hieu[v] for v in c["vao"]] for c in cong_thuc if c["ket_qua"] == bien]
               for bien in ("S", "P")}
    kieu = {d["bien"]: d["kieu"] for d in dai_luong}
    return render_template("tinh_toan.html", hinh=hinh, ma=ma, ten=ten_hinh[ma],
                           dai_luong=dai_luong, cong_thuc=nhom_cong_thuc(cong_thuc),
                           ct_theo_ma=ct_theo_ma, gia_tri_form=gia_tri_form, kq=kq,
                           loi_dinh_dang=loi_dinh_dang, da_tinh=da_tinh, don_vi=don_vi,
                           DON_VI=DON_VI, ky_hieu=ky_hieu, can_cho=can_cho, kieu=kieu, hinh_ve=ve(ma),
                           q_cong_thuc=Q_CONG_THUC)


@app.route("/api/tinh-toan")
def api_tinh_toan():
    """API JSON: /api/tinh-toan?hinh=HINH_THOI&d1=6&d2=8"""
    ma = request.args.get("hinh", "HINH_CHU_NHAT")
    kho = Neo4jCongThuc(q)
    dai_luong = kho.dai_luong(ma)
    nhap = {}
    for d in dai_luong:
        x = doc_so(request.args.get(d["bien"]))
        if isinstance(x, float):
            nhap[d["bien"]] = x
    kq = tinh(dai_luong, kho.cong_thuc(ma), nhap)
    return jsonify({
        "hinh": ma, "nhap": nhap,
        "ket_qua": {b: round(x, 6) for b, x in kq.gia_tri.items()},
        "cac_buoc": [{"cong_thuc": b["ct"]["hien_thi"], "thay_so": b["thay_so"], "gia_tri": round(b["gia_tri"], 6)}
                     for b in kq.buoc],
        "loi_nhap": kq.loi_nhap,
        "khong_nhat_quan": [{"cong_thuc": x["ct"]["hien_thi"], "tinh_duoc": x["tinh_duoc"], "da_co": x["da_co"]}
                            for x in kq.khong_nhat_quan],
    })


@app.route("/do-thi")
def do_thi():
    hinh, la_mot = du_lieu_chung()
    _, tt = thu_tu_tinh_chat()
    dau_hieu = q(repo.Q_DS_DAU_HIEU)
    for d in dau_hieu:
        d["can"] = sap_xep(d["can"], tt)
    return render_template("do_thi.html", svg=so_do(hinh, la_mot),
                           nut=q(repo.Q_THONG_KE_NUT), canh=q(repo.Q_THONG_KE_CANH),
                           dau_hieu=dau_hieu, truy_van=repo.TRUY_VAN_MAU)


@app.route("/vi-du")
def vi_du():
    du_lieu_chung()
    ten_tc = {t["ma"]: t["ten"] for t in thu_tu_tinh_chat()[0]}
    ten_hinh = {h["ma"]: h["ten"] for h in q(repo.Q_DS_HINH)}
    ds = []
    for v in VI_DU:
        kq = suy_luan(Neo4jStore(q), v["hinh"], v["tc"])
        ds.append({**v, "kq": kq})
    return render_template("vi_du.html", ds=ds, ten_tc=ten_tc, ten_hinh=ten_hinh)


@app.route("/api/suy-luan")
def api_suy_luan():
    """API JSON: /api/suy-luan?hinh=HINH_BINH_HANH&tc=CHEO_BANG&tc=CHEO_VUONG_GOC"""
    kq = suy_luan(Neo4jStore(q), request.args.get("hinh", "TU_GIAC"), request.args.getlist("tc"))
    return jsonify({
        "hinh_ban_dau": kq.hinh_ban_dau,
        "gia_thiet": kq.gia_thiet,
        "ket_luan": kq.ket_luan,
        "hinh_suy_ra": sorted(kq.hinh_suy_ra),
        "cac_buoc": [b.__dict__ for b in kq.buoc],
        "goi_y": [g["ghi_chu"] for g in kq.goi_y],
        "mau_thuan": kq.mau_thuan,
    })


if __name__ == "__main__":
    print(f"Mở trình duyệt tại http://localhost:{config.APP_PORT}")
    app.run(host="127.0.0.1", port=config.APP_PORT, debug=False)
