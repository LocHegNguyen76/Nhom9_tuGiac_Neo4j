"""
Ứng dụng web: Mô hình hoá tứ giác trong hình học phẳng với Neo4j.

Chạy:  python app.py      rồi mở http://localhost:5000
"""
from flask import Flask, abort, jsonify, render_template, request

from data.knowledge import VI_DU
from src import config, db, repo
from src.engine import Neo4jStore, suy_luan
from src.svg import so_do

app = Flask(__name__)
app.json.ensure_ascii = False

# Có thể thay bằng hàm chạy truy vấn khác (dùng khi kiểm thử)
RUN = db.run


class Neo4jOffline(Exception):
    pass


def q(cypher, **params):
    try:
        return RUN(cypher, **params)
    except Exception as e:  # noqa: BLE001
        raise Neo4jOffline(str(e)) from e


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


@app.route("/")
def nhan_dang():
    hinh, la_mot = du_lieu_chung()
    ten_hinh = {h["ma"]: h["ten"] for h in hinh}
    tinh_chat = q(repo.Q_DS_TINH_CHAT)
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

    svg = so_do(hinh, la_mot,
                suy_ra=kq.hinh_suy_ra if kq else (),
                ket_luan=kq.ket_luan if kq else (),
                ban_dau=ban_dau if kq else None)
    return render_template("nhan_dang.html", hinh=hinh, nhom=nhom, ban_dau=ban_dau,
                           chon=chon, kq=kq, store=store, ten_hinh=ten_hinh,
                           ten_tc=ten_tc, svg=svg)


@app.route("/hinh/<ma>")
def tra_cuu(ma):
    hinh, la_mot = du_lieu_chung()
    rows = q(repo.Q_CHI_TIET_HINH, ma=ma)
    if not rows:
        abort(404)
    ct = rows[0]
    ten = ct["hinh"]["ten"]
    tinh_chat = q(repo.Q_TINH_CHAT_CUA_HINH, ma=ma, ten=ten)
    nhan_biet = q(repo.Q_DAU_HIEU_NHAN_BIET, ma=ma)
    di_tiep = q(repo.Q_DAU_HIEU_DI_TIEP, ma=ma)
    svg = so_do(hinh, la_mot, suy_ra=Neo4jStore(q).to_tien({ma}), ket_luan=[ma])
    return render_template("hinh.html", ct=ct, tinh_chat=tinh_chat, nhan_biet=nhan_biet,
                           di_tiep=di_tiep, svg=svg, hinh=hinh)


@app.route("/do-thi")
def do_thi():
    hinh, la_mot = du_lieu_chung()
    return render_template("do_thi.html", svg=so_do(hinh, la_mot),
                           nut=q(repo.Q_THONG_KE_NUT), canh=q(repo.Q_THONG_KE_CANH),
                           dau_hieu=q(repo.Q_DS_DAU_HIEU), truy_van=repo.TRUY_VAN_MAU)


@app.route("/vi-du")
def vi_du():
    du_lieu_chung()
    ten_tc = {t["ma"]: t["ten"] for t in q(repo.Q_DS_TINH_CHAT)}
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
