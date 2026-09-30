"""
Nạp cơ sở tri thức (data/knowledge.py) vào Neo4j.

Chạy:  python -m src.seed
       python -m src.seed --export cypher/seed.cypher   (chỉ xuất file .cypher, không cần Neo4j)
"""
import argparse
import json
import sys
from pathlib import Path

from data import cong_thuc as CT
from data import knowledge as K

ROOT = Path(__file__).resolve().parent.parent

SCHEMA = [
    "CREATE CONSTRAINT hinh_ma IF NOT EXISTS FOR (h:Hinh) REQUIRE h.ma IS UNIQUE",
    "CREATE CONSTRAINT tinhchat_ma IF NOT EXISTS FOR (t:TinhChat) REQUIRE t.ma IS UNIQUE",
    "CREATE CONSTRAINT dauhieu_ma IF NOT EXISTS FOR (d:DauHieu) REQUIRE d.ma IS UNIQUE",
    "CREATE CONSTRAINT dailuong_ma IF NOT EXISTS FOR (d:DaiLuong) REQUIRE d.ma IS UNIQUE",
    "CREATE CONSTRAINT congthuc_ma IF NOT EXISTS FOR (c:CongThuc) REQUIRE c.ma IS UNIQUE",
]

NHAN = ["Hinh", "TinhChat", "DauHieu", "DaiLuong", "CongThuc"]
CLEAR = "MATCH (n) WHERE n:Hinh OR n:TinhChat OR n:DauHieu OR n:DaiLuong OR n:CongThuc DETACH DELETE n"

# Mỗi câu lệnh: (cypher, tên tham số, dữ liệu)
def build_statements():
    hinh = [dict(h) for h in K.HINH]
    tinh_chat = [dict(t, nhom_ten=K.NHOM_TEN[t["nhom"]], thu_tu=i)
                 for i, t in enumerate(K.TINH_CHAT)]
    la_mot = [{"con": c, "cha": p} for c, p in K.LA_MOT]
    co_tc = [{"hinh": h, "tc": t} for h, ts in K.CO_TINH_CHAT.items() for t in ts]
    mau_thuan = [{"a": a, "b": b, "ly_do": r} for a, b, r in K.MAU_THUAN]
    dau_hieu = [
        {
            "ma": d["ma"],
            "ten": d["ten"],
            "loai": "ket_luan" if d["ket_luan"] else "goi_y",
            "ghi_chu": d.get("ghi_chu", ""),
            "tru_khi": d.get("tru_khi", []),
            "ap_dung": d["ap_dung"],
            "ket_luan": d["ket_luan"],
            "can": d["can"],
        }
        for d in K.DAU_HIEU
    ]
    return [
        ("""UNWIND $rows AS r
            MERGE (h:Hinh {ma: r.ma})
            SET h.ten = r.ten, h.dinh_nghia = r.dinh_nghia, h.cap = r.cap, h.cot = r.cot""",
         hinh),
        ("""UNWIND $rows AS r
            MERGE (t:TinhChat {ma: r.ma})
            SET t.ten = r.ten, t.nhom = r.nhom, t.nhom_ten = r.nhom_ten, t.thu_tu = r.thu_tu""",
         tinh_chat),
        ("""UNWIND $rows AS r
            MATCH (c:Hinh {ma: r.con}), (p:Hinh {ma: r.cha})
            MERGE (c)-[:LA_MOT]->(p)""",
         la_mot),
        ("""UNWIND $rows AS r
            MATCH (h:Hinh {ma: r.hinh}), (t:TinhChat {ma: r.tc})
            MERGE (h)-[:CO_TINH_CHAT]->(t)""",
         co_tc),
        ("""UNWIND $rows AS r
            MATCH (a:TinhChat {ma: r.a}), (b:TinhChat {ma: r.b})
            MERGE (a)-[m:MAU_THUAN]->(b) SET m.ly_do = r.ly_do""",
         mau_thuan),
        ("""UNWIND $rows AS r
            MERGE (d:DauHieu {ma: r.ma})
            SET d.ten = r.ten, d.loai = r.loai, d.ghi_chu = r.ghi_chu, d.tru_khi = r.tru_khi
            WITH d, r
            MATCH (h:Hinh {ma: r.ap_dung})
            MERGE (d)-[:AP_DUNG_CHO]->(h)
            WITH d, r
            UNWIND r.can AS ma_tc
            MATCH (t:TinhChat {ma: ma_tc})
            MERGE (d)-[:CAN]->(t)""",
         dau_hieu),
        ("""UNWIND $rows AS r
            MATCH (d:DauHieu {ma: r.ma}), (k:Hinh {ma: r.ket_luan})
            MERGE (d)-[:KET_LUAN]->(k)""",
         [d for d in dau_hieu if d["ket_luan"]]),
        # ----- Công thức diện tích, chu vi, liên quan -----
        ("""UNWIND $rows AS r
            MATCH (h:Hinh {ma: r.hinh})
            MERGE (d:DaiLuong {ma: r.ma})
            SET d.bien = r.bien, d.ky_hieu = r.ky_hieu, d.ten = r.ten, d.kieu = r.kieu, d.thu_tu = r.thu_tu
            MERGE (h)-[:CO_DAI_LUONG]->(d)""",
         CT.ds_dai_luong()),
        ("""UNWIND $rows AS r
            MATCH (h:Hinh {ma: r.hinh})
            MERGE (c:CongThuc {ma: r.ma})
            SET c.loai = r.loai, c.loai_ten = r.loai_ten, c.hien_thi = r.hien_thi,
                c.bieu_thuc = r.bieu_thuc, c.ghi_chu = r.ghi_chu, c.thu_tu = r.thu_tu
            MERGE (h)-[:CO_CONG_THUC]->(c)
            WITH c, r
            MATCH (k:DaiLuong {ma: r.hinh + '.' + r.ket_qua})
            MERGE (c)-[:TINH_RA]->(k)
            WITH c, r
            UNWIND r.vao AS bien
            MATCH (v:DaiLuong {ma: r.hinh + '.' + bien})
            MERGE (c)-[:CAN_BIEN]->(v)""",
         CT.ds_cong_thuc()),
    ]


def seed(driver, database="neo4j", log=print):
    with driver.session(database=database) as s:
        for q in SCHEMA:
            s.run(q).consume()
        s.run(CLEAR).consume()
        for cypher, rows in build_statements():
            s.run(cypher, rows=rows).consume()
        counts = s.run(
            """MATCH (n) WHERE n:Hinh OR n:TinhChat OR n:DauHieu OR n:DaiLuong OR n:CongThuc
               WITH labels(n)[0] AS nhan, count(*) AS so
               RETURN nhan, so ORDER BY nhan"""
        ).data()
        rels = s.run(
            "MATCH (:Hinh|TinhChat|DauHieu|DaiLuong|CongThuc)-[r]->() RETURN type(r) AS loai, count(*) AS so ORDER BY loai"
        ).data()
    log("Đã nạp tri thức vào Neo4j:")
    for c in counts:
        log(f"  - Nút {c['nhan']:<9}: {c['so']}")
    for r in rels:
        log(f"  - Quan hệ {r['loai']:<13}: {r['so']}")
    return counts, rels


# ---------------------------------------------------------------------------
# Xuất ra file .cypher thuần để dán vào Neo4j Browser (không cần Python driver)
# ---------------------------------------------------------------------------
def _lit(v):
    """Chuyển giá trị Python thành literal Cypher."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "[" + ", ".join(_lit(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k}: {_lit(x)}" for k, x in v.items()) + "}"
    raise TypeError(type(v))


def export_cypher(path):
    lines = [
        "// ==========================================================",
        "// Mô hình hoá tứ giác trong hình học phẳng với Neo4j",
        "// File sinh tự động từ data/knowledge.py  (python -m src.seed --export ...)",
        "// Cách dùng: mở Neo4j Browser, bật 'Enable multi statement query editor'",
        "// trong Settings, dán toàn bộ file và chạy.",
        "// ==========================================================",
        "",
    ]
    lines += [q + ";" for q in SCHEMA]
    lines += ["", CLEAR + ";", ""]
    for cypher, rows in build_statements():
        body = "\n".join(l.strip() for l in cypher.splitlines())
        body = body.replace("UNWIND $rows AS r", f"UNWIND {_lit(rows)} AS r", 1)
        lines += [body + ";", ""]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    print(f"Đã xuất {path}")


def main():
    ap = argparse.ArgumentParser(description="Nạp tri thức tứ giác vào Neo4j")
    ap.add_argument("--export", metavar="FILE", help="Chỉ xuất file .cypher")
    args = ap.parse_args()
    if args.export:
        export_cypher(args.export)
        return
    from src import config
    from src.db import get_driver

    try:
        driver = get_driver()
        driver.verify_connectivity()
    except Exception as e:  # noqa: BLE001
        print(f"Không kết nối được Neo4j tại {config.NEO4J_URI}: {e}", file=sys.stderr)
        print("Hãy kiểm tra Neo4j đã chạy và mật khẩu trong file .env.", file=sys.stderr)
        sys.exit(1)
    seed(driver, config.NEO4J_DATABASE)
    driver.close()


if __name__ == "__main__":
    main()
