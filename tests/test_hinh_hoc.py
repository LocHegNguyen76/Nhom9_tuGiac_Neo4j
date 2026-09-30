"""Kiểm thử nhận diện tính chất từ toạ độ + suy luận ra đúng hình (trang Thử thách)."""
import unittest

from data import knowledge as K
from src.engine import MemoryStore, suy_luan
from src.hinh_hoc import kiem_tra_hop_le, tinh_chat

S = MemoryStore(K)


def hinh(*pts):
    ok, ly_do = kiem_tra_hop_le(pts)
    assert ok, ly_do
    return suy_luan(S, "TU_GIAC", tinh_chat(pts)).ket_luan


class TestNhanDienTuToaDo(unittest.TestCase):
    def test_tu_giac_thuong(self):
        pts = ((1, 2), (11, 1), (13, 9), (4, 12))
        self.assertEqual(tinh_chat(pts), [])
        self.assertEqual(hinh(*pts), ["TU_GIAC"])

    def test_hai_canh_ke_bang_va_goc_vuong_van_la_tu_giac(self):
        # Có góc vuông và hai cạnh kề bằng nhau nhưng không có cạnh song song -> vẫn là tứ giác
        pts = ((2, 3), (11, 1), (13, 9), (4, 12))
        self.assertIn("MOT_GOC_VUONG", tinh_chat(pts))
        self.assertEqual(hinh(*pts), ["TU_GIAC"])

    def test_hinh_thang(self):
        self.assertEqual(hinh((0, 0), (10, 0), (8, 4), (1, 4)), ["HINH_THANG"])

    def test_hinh_thang_can(self):
        self.assertEqual(hinh((0, 0), (10, 0), (7, 4), (3, 4)), ["HINH_THANG_CAN"])

    def test_hinh_thang_vuong(self):
        self.assertEqual(hinh((0, 0), (10, 0), (6, 4), (0, 4)), ["HINH_THANG_VUONG"])

    def test_hinh_binh_hanh(self):
        self.assertEqual(hinh((0, 0), (8, 0), (11, 5), (3, 5)), ["HINH_BINH_HANH"])

    def test_hinh_chu_nhat(self):
        self.assertEqual(hinh((0, 0), (8, 0), (8, 5), (0, 5)), ["HINH_CHU_NHAT"])

    def test_hinh_chu_nhat_nghieng(self):
        self.assertEqual(hinh((0, 0), (4, 2), (1, 8), (-3, 6)), ["HINH_CHU_NHAT"])

    def test_hinh_thoi(self):
        self.assertEqual(hinh((0, 0), (5, 0), (8, 4), (3, 4)), ["HINH_THOI"])

    def test_hinh_vuong(self):
        self.assertEqual(hinh((0, 0), (6, 0), (6, 6), (0, 6)), ["HINH_VUONG"])

    def test_hinh_vuong_nghieng(self):
        self.assertEqual(hinh((3, 0), (7, 3), (4, 7), (0, 4)), ["HINH_VUONG"])

    def test_hinh_dieu(self):
        self.assertEqual(hinh((5, 0), (9, 3), (5, 10), (1, 3)), ["HINH_DIEU"])

    def test_khong_hop_le(self):
        self.assertFalse(kiem_tra_hop_le([(0, 0), (4, 0), (0, 4), (4, 4)])[0])   # tự cắt
        self.assertFalse(kiem_tra_hop_le([(0, 0), (4, 0), (1, 1), (0, 4)])[0])   # lõm
        self.assertFalse(kiem_tra_hop_le([(0, 0), (2, 0), (4, 0), (0, 4)])[0])   # thẳng hàng
        self.assertFalse(kiem_tra_hop_le([(0, 0), (0, 0), (4, 4), (0, 4)])[0])   # trùng


if __name__ == "__main__":
    unittest.main()
