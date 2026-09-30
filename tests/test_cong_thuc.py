"""Kiểm thử công thức diện tích, chu vi và bộ tính toán (không cần Neo4j)."""
import math
import unittest

from data import cong_thuc as CT
from data import knowledge as K
from src.tinh_toan import MemoryCongThuc, tinh

M = MemoryCongThuc(CT)


def giai(hinh, **nhap):
    return tinh(M.dai_luong(hinh), M.cong_thuc(hinh), nhap)


class TestDuLieuCongThuc(unittest.TestCase):
    def test_moi_hinh_co_dien_tich_va_chu_vi(self):
        for h in K.HINH:
            loai = {c[0] for c in CT.CONG_THUC[h["ma"]]}
            self.assertIn("dien_tich", loai, h["ma"])
            self.assertIn("chu_vi", loai, h["ma"])

    def test_bien_hop_le(self):
        for c in CT.ds_cong_thuc():
            bien = {d[0] for d in CT.DAI_LUONG[c["hinh"]]}
            self.assertIn(c["ket_qua"], bien, c["ma"])
            self.assertTrue(set(c["vao"]) <= bien, c["ma"])
            self.assertNotIn(c["ket_qua"], c["vao"], c["ma"])

    def test_vi_du_tinh_duoc_S_va_P(self):
        for h, v in CT.VI_DU_TINH.items():
            r = giai(h, **v)
            self.assertIn("S", r.gia_tri, h)
            self.assertIn("P", r.gia_tri, h)
            self.assertFalse(r.khong_nhat_quan, h)


class TestTinhToan(unittest.TestCase):
    def test_hinh_vuong(self):
        r = giai("HINH_VUONG", a=5)
        self.assertAlmostEqual(r.gia_tri["S"], 25)
        self.assertAlmostEqual(r.gia_tri["P"], 20)
        self.assertAlmostEqual(r.gia_tri["d"], 5 * math.sqrt(2))

    def test_hinh_vuong_tu_duong_cheo(self):
        r = giai("HINH_VUONG", d=10)
        self.assertAlmostEqual(r.gia_tri["S"], 50)

    def test_chu_nhat(self):
        r = giai("HINH_CHU_NHAT", a=4, b=3)
        self.assertAlmostEqual(r.gia_tri["d"], 5)
        self.assertAlmostEqual(r.gia_tri["S"], 12)
        self.assertAlmostEqual(r.gia_tri["P"], 14)

    def test_chu_nhat_tu_S_va_P(self):
        r = giai("HINH_CHU_NHAT", S=12, P=14)
        self.assertAlmostEqual(r.gia_tri["a"], 4)
        self.assertAlmostEqual(r.gia_tri["b"], 3)

    def test_hinh_thoi(self):
        r = giai("HINH_THOI", d1=6, d2=8)
        self.assertAlmostEqual(r.gia_tri["a"], 5)
        self.assertAlmostEqual(r.gia_tri["S"], 24)
        self.assertAlmostEqual(r.gia_tri["h"], 4.8)

    def test_hinh_thang(self):
        r = giai("HINH_THANG", a=10, b=6, h=4)
        self.assertAlmostEqual(r.gia_tri["S"], 32)
        self.assertAlmostEqual(r.gia_tri["m"], 8)

    def test_hinh_thang_can(self):
        r = giai("HINH_THANG_CAN", a=10, b=4, h=4)
        self.assertAlmostEqual(r.gia_tri["c"], 5)
        self.assertAlmostEqual(r.gia_tri["P"], 24)
        self.assertAlmostEqual(r.gia_tri["alpha"], math.degrees(math.atan(8 / 6)))

    def test_binh_hanh(self):
        r = giai("HINH_BINH_HANH", a=6, b=4, alpha=30)
        self.assertAlmostEqual(r.gia_tri["S"], 12)
        self.assertAlmostEqual(r.gia_tri["ha"], 2)
        self.assertAlmostEqual(r.gia_tri["d1"] ** 2 + r.gia_tri["d2"] ** 2, 2 * (36 + 16))

    def test_tu_giac_goc_con_lai(self):
        r = giai("TU_GIAC", A=90, B=90, C=90)
        self.assertAlmostEqual(r.gia_tri["D"], 90)

    def test_khong_nhat_quan(self):
        r = giai("HINH_VUONG", a=5, S=30)
        self.assertTrue(r.khong_nhat_quan)

    def test_du_lieu_khong_hop_le(self):
        self.assertTrue(giai("HINH_VUONG", a=-3).loi_nhap)
        self.assertTrue(giai("HINH_THOI", a=5, alpha=200).loi_nhap)
        r = giai("HINH_THANG_CAN", a=10, b=4, c=2)   # cạnh bên quá ngắn
        self.assertNotIn("h", r.gia_tri)
        self.assertTrue(r.khong_ap_dung)


if __name__ == "__main__":
    unittest.main()
