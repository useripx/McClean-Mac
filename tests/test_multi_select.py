"""
Unit Tests untuk Fitur Pemilihan & Pembersihan Multi-Berkas (Multi-Item Selection)
Memverifikasi bahwa aksi pembersihan hanya memproses berkas yang dipilih/dicentang,
sedangkan berkas lain yang tidak dipilih tetap utuh tanpa perubahan.
"""

import os
import unittest
import tempfile
import shutil
from PIL import Image
import piexif
from pypdf import PdfWriter, PdfReader

from src.cleaners import clean_file
from src.watermarks import AIWatermarkCleaner
from src.inspectors import inspect_file

class TestMultiSelectCleaning(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

        # 1. File A: Gambar dengan EXIF (Dipilih untuk dibersihkan)
        self.file_a = os.path.join(self.test_dir, "file_a.jpg")
        img_a = Image.new("RGB", (50, 50), color="red")
        exif_dict = {"0th": {piexif.ImageIFD.Artist: b"Author A", piexif.ImageIFD.Software: b"Tool A"}, "Exif": {}, "GPS": {}, "1st": {}}
        img_a.save(self.file_a, exif=piexif.dump(exif_dict))

        # 2. File B: PDF dengan Metadata (Dipilih untuk dibersihkan)
        self.file_b = os.path.join(self.test_dir, "file_b.pdf")
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        writer.add_metadata({"/Author": "Author B", "/Title": "Document B"})
        with open(self.file_b, "wb") as f:
            writer.write(f)

        # 3. File C: Gambar dengan EXIF (TIDAK DIPILIH - Harus tetap memiliki metadata)
        self.file_c = os.path.join(self.test_dir, "file_c.jpg")
        img_c = Image.new("RGB", (50, 50), color="green")
        exif_c = {"0th": {piexif.ImageIFD.Artist: b"Author C Untouched"}, "Exif": {}, "GPS": {}, "1st": {}}
        img_c.save(self.file_c, exif=piexif.dump(exif_c))

        # 4. File D: Markdown dengan Watermark AI (Dipilih untuk pembersihan watermark)
        self.file_d = os.path.join(self.test_dir, "file_d.md")
        with open(self.file_d, "w", encoding="utf-8") as f:
            # Mengandung Variation Selector-16 (\uFE0F)
            f.write("# Catatan Rahasia\uFE0F\nIni adalah teks dengan watermark AI.")

        # 5. File E: Markdown dengan Watermark AI (TIDAK DIPILIH)
        self.file_e = os.path.join(self.test_dir, "file_e.md")
        with open(self.file_e, "w", encoding="utf-8") as f:
            f.write("# Artikel\uFE0F Tidak Dipilih")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_clean_subset_of_selected_files_inplace(self):
        """Memverifikasi pembersihan hanya terjadi pada berkas terpilih (File A & B), bukan File C."""
        selected_paths = [self.file_a, self.file_b]

        for p in selected_paths:
            res = clean_file(p, inplace=True)
            self.assertTrue(res["success"])

        # Verifikasi File A (Terpilih): EXIF identitas & perangkat hilang
        info_a = inspect_file(self.file_a)
        self.assertNotIn("EXIF Kamera & Perangkat", info_a["categories"])

        # Verifikasi File B (Terpilih): Metadata PDF hilang total
        info_b = inspect_file(self.file_b)
        self.assertFalse(info_b["has_metadata"])

        # Verifikasi File C (TIDAK Terpilih): Metadata TETAP ADA dan utuh
        info_c = inspect_file(self.file_c)
        self.assertIn("EXIF Kamera & Perangkat", info_c["categories"])
        self.assertIn("Author C Untouched", str(info_c["categories"]["EXIF Kamera & Perangkat"]))

    def test_clean_ai_watermarks_subset_selected(self):
        """Memverifikasi pembersihan tanda air AI hanya terjadi pada berkas terpilih (File D), bukan File E."""
        selected_paths = [self.file_d]

        for p in selected_paths:
            res = AIWatermarkCleaner.clean_file(p, inplace=True)
            self.assertTrue(res["success"])

        # Verifikasi File D (Terpilih): Watermark hilang
        info_d = inspect_file(self.file_d)
        self.assertFalse(info_d["has_ai_watermark"])

        # Verifikasi File E (TIDAK Terpilih): Watermark TETAP ADA
        info_e = inspect_file(self.file_e)
        self.assertTrue(info_e["has_ai_watermark"])

if __name__ == "__main__":
    unittest.main()
