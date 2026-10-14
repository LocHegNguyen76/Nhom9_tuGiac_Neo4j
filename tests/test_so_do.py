"""Kiểm thử sơ đồ tri thức dạng hình ảnh (trang Đồ thị tri thức)."""
import unittest

from data import knowledge as K
from src.so_do_tri_thuc import canh_suy_ra, ve_so_do

T = {t["ma"]: (i, t) for i, t in enumerate(K.TINH_CHAT)}
DAU_HIEU = [{"ma": d["ma"], "ten": d["ten"], "tu": d["ap_dung"], "den": d["ket_luan"],
             "can": [{"ma": c, "ngan": T[c][1]["ngan"], "thu_tu": T[c][0]} for c in d["can"]]}
            for d in K.DAU_HIEU if d["ket_luan"]]
HINH = [dict(h) for h in K.HINH]


class TestSoDo(unittest.TestCase):
    def setUp(self):
        self.canh = canh_suy_ra(HINH, K.LA_MOT, DAU_HIEU)
        self.theo = {(c["tu"], c["den"]): c for c in self.canh}

    def test_moi_quan_he_la_mot_co_mot_mui_ten_co_dieu_kien(self):
        self.assertEqual(len(self.canh), len(K.LA_MOT))
        for con, cha in K.LA_MOT:
            c = self.theo[(cha, con)]                     # mũi tên đi từ hình cha xuống hình con
            self.assertTrue(c["dau_hieu"], (cha, con))

    def test_dau_hieu_truc_tiep(self):
        c = self.theo[("HINH_BINH_HANH", "HINH_CHU_NHAT")]
        self.assertFalse(c["gian_tiep"])
        self.assertEqual([d["ma"] for d in c["dau_hieu"]], ["DH13", "DH14"])

    def test_dau_hieu_tu_hinh_to_tien(self):
        # Không có dấu hiệu Hình thang -> Hình bình hành: dùng dấu hiệu từ Tứ giác
        c = self.theo[("HINH_THANG", "HINH_BINH_HANH")]
        self.assertTrue(c["gian_tiep"])
        self.assertEqual({d["tu"] for d in c["dau_hieu"]}, {"TU_GIAC"})

    def test_svg(self):
        svg = ve_so_do(HINH, self.canh)
        self.assertEqual(svg.count('href="/hinh/'), len(HINH))
        self.assertEqual(svg.count('class="sd-canh"'), len(K.LA_MOT))
        self.assertIn("+ 1 góc vuông", svg)
        self.assertIn("<polygon", svg)
        self.assertEqual(ve_so_do(HINH, self.canh), svg)      # kết quả ổn định (được nhớ lại)


class TestSoDoPhanCap(unittest.TestCase):
    """Sơ đồ phân cấp ở trang Nhận dạng / tra cứu."""

    def test_ve_va_to_mau(self):
        from src.engine import MemoryStore, suy_luan
        from src.svg import so_do
        kq = suy_luan(MemoryStore(K), "HINH_BINH_HANH", ["CHEO_VUONG_GOC", "CHEO_BANG"])
        svg = so_do(HINH, K.LA_MOT, suy_ra=kq.hinh_suy_ra, ket_luan=kq.ket_luan, ban_dau="HINH_BINH_HANH",
                    buoc=[(b.ap_dung, b.ket_luan, b.ma) for b in kq.buoc])
        self.assertEqual(svg.count('href="/hinh/'), len(HINH))
        self.assertEqual(svg.count('class="canh'), len(K.LA_MOT))
        self.assertIn("DH20", svg)                     # bước HCN -> Hình vuông được ghi mã dấu hiệu
        self.assertIn('class="nut on kl"', svg)        # hình vuông là kết luận
