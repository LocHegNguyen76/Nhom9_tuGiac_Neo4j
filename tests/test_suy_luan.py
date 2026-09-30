"""Kiểm thử cơ sở tri thức và bộ suy luận (không cần Neo4j).

Chạy:  python -m pytest -q   hoặc   python -m unittest discover tests
"""
import unittest

from data import knowledge as K
from src.engine import MemoryStore, suy_luan

S = MemoryStore(K)


def kl(hinh, *tc):
    return suy_luan(S, hinh, list(tc))


class TestTriThuc(unittest.TestCase):
    def test_ma_hop_le(self):
        hinh = {h["ma"] for h in K.HINH}
        tc = {t["ma"] for t in K.TINH_CHAT}
        for c, p in K.LA_MOT:
            self.assertIn(c, hinh); self.assertIn(p, hinh)
        for h, ts in K.CO_TINH_CHAT.items():
            self.assertIn(h, hinh)
            for t in ts:
                self.assertIn(t, tc)
        for d in K.DAU_HIEU:
            self.assertIn(d["ap_dung"], hinh)
            if d["ket_luan"]:
                self.assertIn(d["ket_luan"], hinh)
            for t in d["can"]:
                self.assertIn(t, tc)

    def test_khong_trung_ma(self):
        for ds in (K.HINH, K.TINH_CHAT, K.DAU_HIEU):
            ma = [x["ma"] for x in ds]
            self.assertEqual(len(ma), len(set(ma)))

    def test_ket_luan_la_hinh_con(self):
        """Hình kết luận của mỗi dấu hiệu phải là hình con của hình áp dụng."""
        for d in K.DAU_HIEU:
            if d["ket_luan"]:
                self.assertIn(d["ap_dung"], S.to_tien({d["ket_luan"]}), d["ma"])

    def test_moi_hinh_deu_nhan_biet_duoc(self):
        for h in K.HINH:
            if h["ma"] == "TU_GIAC":
                continue
            self.assertTrue(any(d["ket_luan"] == h["ma"] for d in K.DAU_HIEU), h["ma"])


class TestSuyLuan(unittest.TestCase):
    def test_hbh_cheo_vuong_goc_va_bang_la_hinh_vuong(self):
        r = kl("HINH_BINH_HANH", "CHEO_VUONG_GOC", "CHEO_BANG")
        self.assertEqual(r.ket_luan, ["HINH_VUONG"])
        self.assertEqual({b.ma for b in r.buoc} >= {"DH14", "DH17"}, True)

    def test_hinh_thang_canh_ben_bang_chua_ket_luan(self):
        r = kl("HINH_THANG", "CANH_BEN_BANG")
        self.assertEqual(r.ket_luan, ["HINH_THANG"])
        self.assertEqual([g["ma"] for g in r.goi_y], ["GY01"])

    def test_hinh_thang_canh_ben_bang_khong_song_song(self):
        r = kl("HINH_THANG", "CANH_BEN_BANG", "CANH_BEN_KHONG_SS")
        self.assertEqual(r.ket_luan, ["HINH_THANG_CAN"])
        self.assertEqual(r.goi_y, [])

    def test_hinh_thang_canh_ben_bang_va_song_song(self):
        r = kl("HINH_THANG", "CANH_BEN_BANG", "SS_2_CAP")
        self.assertEqual(r.ket_luan, ["HINH_BINH_HANH"])
        self.assertEqual(r.goi_y, [])

    def test_cheo_trung_diem_va_bang_la_hcn(self):
        self.assertEqual(kl("TU_GIAC", "CHEO_TRUNG_DIEM", "CHEO_BANG").ket_luan, ["HINH_CHU_NHAT"])

    def test_bon_canh_bang_mot_goc_vuong(self):
        self.assertEqual(kl("TU_GIAC", "BON_CANH_BANG", "MOT_GOC_VUONG").ket_luan, ["HINH_VUONG"])

    def test_thang_cheo_bang_goc_vuong_la_hcn(self):
        self.assertEqual(kl("HINH_THANG", "CHEO_BANG", "MOT_GOC_VUONG").ket_luan, ["HINH_CHU_NHAT"])

    def test_thang_vuong(self):
        self.assertEqual(kl("TU_GIAC", "SS_1_CAP", "MOT_GOC_VUONG").ket_luan, ["HINH_THANG_VUONG"])

    def test_dieu_co_canh_song_song_la_thoi(self):
        self.assertEqual(kl("TU_GIAC", "HAI_CAP_KE_BANG", "SS_1_CAP").ket_luan, ["HINH_THOI"])

    def test_ba_goc_vuong_hai_canh_ke(self):
        self.assertEqual(kl("TU_GIAC", "BA_GOC_VUONG", "HAI_CANH_KE_BANG").ket_luan, ["HINH_VUONG"])

    def test_khong_gia_thiet(self):
        self.assertEqual(kl("TU_GIAC").ket_luan, ["TU_GIAC"])
        self.assertEqual(kl("HINH_THOI").ket_luan, ["HINH_THOI"])

    def test_mau_thuan(self):
        r = kl("TU_GIAC", "SS_2_CAP", "CANH_BEN_KHONG_SS")
        self.assertTrue(r.mau_thuan)
        r2 = kl("HINH_BINH_HANH", "CANH_BEN_KHONG_SS")
        self.assertTrue(r2.mau_thuan)

    def test_hinh_vuong_ke_thua_moi_tinh_chat(self):
        r = kl("HINH_VUONG")
        self.assertEqual(set(r.tinh_chat), {t["ma"] for t in K.TINH_CHAT} - {"CANH_BEN_KHONG_SS"})

    def test_vi_du_khong_loi(self):
        for v in K.VI_DU:
            r = kl(v["hinh"], *v["tc"])
            self.assertTrue(r.ket_luan)


if __name__ == "__main__":
    unittest.main()
