"""
Bộ suy luận tiến (forward chaining) nhận dạng tứ giác.

Thuật toán (lặp đến khi không suy ra thêm được gì — điểm bất động):

    1. Tập HÌNH đã biết  H = {hình ban đầu}
       Tập TÍNH CHẤT đã biết T = giả thiết người dùng chọn
    2. Bổ sung vào H mọi hình tổ tiên (qua LA_MOT*), vào T mọi tính chất
       của các hình trong H (qua LA_MOT*0..-[:CO_TINH_CHAT]).
    3. Tìm các dấu hiệu (:DauHieu) chưa dùng mà
           hình AP_DUNG_CHO ∈ H  và  mọi tính chất CAN ⊆ T
       -> thêm hình KET_LUAN vào H, ghi lại bước suy luận.
    4. Nếu có dấu hiệu mới thì quay lại bước 2, ngược lại dừng.
    5. Kết luận = các hình trong H không có "hình con" nào cũng thuộc H
       (hình cụ thể nhất).

Mọi truy vấn tri thức đều chạy trên Neo4j (Neo4jStore). MemoryStore là bản
cài đặt tương đương bằng Python thuần, chỉ dùng cho kiểm thử tự động.
"""
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Các câu Cypher dùng trong quá trình suy luận
# ---------------------------------------------------------------------------
Q_TO_TIEN = """
MATCH (h:Hinh)-[:LA_MOT*0..]->(a:Hinh)
WHERE h.ma IN $hinh
RETURN DISTINCT a.ma AS ma"""

Q_TINH_CHAT_KE_THUA = """
MATCH (h:Hinh)-[:LA_MOT*0..]->(a:Hinh)-[:CO_TINH_CHAT]->(t:TinhChat)
WHERE h.ma IN $hinh
RETURN t.ma AS tc, collect(DISTINCT a.ma) AS tu_hinh"""

Q_DAU_HIEU_THOA = """
MATCH (d:DauHieu)-[:AP_DUNG_CHO]->(h:Hinh)
WHERE h.ma IN $hinh AND NOT d.ma IN $da_dung
WITH d, h, [(d)-[:CAN]->(t:TinhChat) | t.ma] AS can
WHERE all(x IN can WHERE x IN $tinh_chat)
OPTIONAL MATCH (d)-[:KET_LUAN]->(k:Hinh)
RETURN d.ma AS ma, d.ten AS ten, d.loai AS loai, d.ghi_chu AS ghi_chu,
       d.tru_khi AS tru_khi, h.ma AS ap_dung, can, k.ma AS ket_luan
ORDER BY ma"""

Q_MAU_THUAN = """
MATCH (a:TinhChat)-[m:MAU_THUAN]-(b:TinhChat)
WHERE a.ma IN $tinh_chat AND b.ma IN $tinh_chat AND a.ma < b.ma
RETURN a.ma AS a, b.ma AS b, m.ly_do AS ly_do"""

Q_CU_THE_NHAT = """
MATCH (h:Hinh) WHERE h.ma IN $hinh
  AND NOT EXISTS { MATCH (c:Hinh)-[:LA_MOT]->(h) WHERE c.ma IN $hinh }
RETURN h.ma AS ma ORDER BY h.cap DESC"""


# ---------------------------------------------------------------------------
# Kho tri thức
# ---------------------------------------------------------------------------
class Neo4jStore:
    """Truy vấn tri thức trên Neo4j và ghi lại các câu Cypher đã chạy."""

    def __init__(self, run):
        self._run = run
        self.log = []  # [(tên, cypher, số lần chạy)]

    def _q(self, name, cypher, **params):
        for item in self.log:
            if item[0] == name:
                item[2] += 1
                break
        else:
            self.log.append([name, cypher.strip(), 1])
        return self._run(cypher, **params)

    def to_tien(self, hinh):
        return {r["ma"] for r in self._q("Tìm hình tổ tiên", Q_TO_TIEN, hinh=list(hinh))}

    def tinh_chat_ke_thua(self, hinh):
        rows = self._q("Tính chất kế thừa", Q_TINH_CHAT_KE_THUA, hinh=list(hinh))
        return {r["tc"]: sorted(r["tu_hinh"]) for r in rows}

    def dau_hieu_thoa(self, hinh, tinh_chat, da_dung):
        return self._q("Dấu hiệu thoả mãn", Q_DAU_HIEU_THOA, hinh=list(hinh),
                       tinh_chat=list(tinh_chat), da_dung=list(da_dung))

    def mau_thuan(self, tinh_chat):
        return self._q("Kiểm tra mâu thuẫn", Q_MAU_THUAN, tinh_chat=list(tinh_chat))

    def cu_the_nhat(self, hinh):
        return [r["ma"] for r in self._q("Hình cụ thể nhất", Q_CU_THE_NHAT, hinh=list(hinh))]


class MemoryStore:
    """Cài đặt tương đương bằng Python thuần (dùng cho unit test)."""

    def __init__(self, K):
        self.K = K
        self.cha = {}
        for c, p in K.LA_MOT:
            self.cha.setdefault(c, set()).add(p)
        self.cap = {h["ma"]: h["cap"] for h in K.HINH}
        self.log = []

    def to_tien(self, hinh):
        kq, stack = set(), list(hinh)
        while stack:
            h = stack.pop()
            if h not in kq:
                kq.add(h)
                stack.extend(self.cha.get(h, ()))
        return kq

    def tinh_chat_ke_thua(self, hinh):
        kq = {}
        for a in self.to_tien(hinh):
            for t in self.K.CO_TINH_CHAT.get(a, []):
                kq.setdefault(t, set()).add(a)
        return {t: sorted(v) for t, v in kq.items()}

    def dau_hieu_thoa(self, hinh, tinh_chat, da_dung):
        out = []
        for d in self.K.DAU_HIEU:
            if d["ap_dung"] in hinh and d["ma"] not in da_dung and set(d["can"]) <= set(tinh_chat):
                out.append({"ma": d["ma"], "ten": d["ten"],
                            "loai": "ket_luan" if d["ket_luan"] else "goi_y",
                            "ghi_chu": d.get("ghi_chu", ""), "tru_khi": d.get("tru_khi", []),
                            "ap_dung": d["ap_dung"], "can": d["can"], "ket_luan": d["ket_luan"]})
        return sorted(out, key=lambda r: r["ma"])

    def mau_thuan(self, tinh_chat):
        return [{"a": min(a, b), "b": max(a, b), "ly_do": r}
                for a, b, r in self.K.MAU_THUAN if a in tinh_chat and b in tinh_chat]

    def cu_the_nhat(self, hinh):
        hinh = set(hinh)
        kq = [h for h in hinh if not any(h in self.cha.get(c, ()) for c in hinh)]
        return sorted(kq, key=lambda h: -self.cap[h])


# ---------------------------------------------------------------------------
# Kết quả
# ---------------------------------------------------------------------------
@dataclass
class Buoc:
    vong: int
    ma: str
    ten: str
    ap_dung: str
    can: list
    ket_luan: str
    nguon_tc: dict  # tính chất -> "giả thiết" hoặc danh sách hình suy ra nó


@dataclass
class KetQua:
    hinh_ban_dau: str
    gia_thiet: list
    hinh_suy_ra: set = field(default_factory=set)
    tinh_chat: dict = field(default_factory=dict)
    buoc: list = field(default_factory=list)
    goi_y: list = field(default_factory=list)
    mau_thuan: list = field(default_factory=list)
    ket_luan: list = field(default_factory=list)
    so_vong: int = 0


def suy_luan(store, hinh_ban_dau="TU_GIAC", gia_thiet=(), max_vong=50):
    gia_thiet = list(dict.fromkeys(gia_thiet))
    kq = KetQua(hinh_ban_dau=hinh_ban_dau, gia_thiet=gia_thiet)
    hinh = {hinh_ban_dau}
    da_dung = []
    goi_y_tam = []

    for vong in range(1, max_vong + 1):
        hinh = store.to_tien(hinh)
        ke_thua = store.tinh_chat_ke_thua(hinh)
        tinh_chat = {t: "giả thiết" for t in gia_thiet}
        for t, tu in ke_thua.items():
            tinh_chat.setdefault(t, tu)

        moi = store.dau_hieu_thoa(hinh, tinh_chat.keys(), da_dung)
        kq.so_vong = vong
        if not moi:
            break
        # Ưu tiên dấu hiệu dùng nhiều giả thiết gốc nhất (lời giải tự nhiên hơn)
        moi.sort(key=lambda d: (sum(tinh_chat[c] != "giả thiết" for c in d["can"]), d["ma"]))
        for d in moi:
            da_dung.append(d["ma"])
            if d["ket_luan"] in hinh:
                continue  # hình này đã biết, bỏ qua bước thừa
            if d["ket_luan"]:
                kq.buoc.append(Buoc(vong, d["ma"], d["ten"], d["ap_dung"], d["can"],
                                    d["ket_luan"], {c: tinh_chat[c] for c in d["can"]}))
                hinh.add(d["ket_luan"])
            else:
                goi_y_tam.append(d)

    kq.hinh_suy_ra = hinh
    kq.tinh_chat = tinh_chat
    kq.goi_y = [g for g in goi_y_tam if not set(g["tru_khi"] or []) & hinh]
    kq.mau_thuan = store.mau_thuan(tinh_chat.keys())
    kq.ket_luan = store.cu_the_nhat(hinh)
    return kq
