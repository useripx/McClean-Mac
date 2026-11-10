"""
Unit Test: Metadata Inspectors
"""
import os
import shutil
import tempfile
import unittest
from PIL import Image
from pypdf import PdfWriter
from docx import Document
from src.inspectors import inspect_file
from src.inspectors.image_inspector import ImageInspector
from src.inspectors.pdf_inspector import PdfInspector
from src.inspectors.docx_inspector import DocxInspector
from src.inspectors.text_inspector import TextInspector

class TestInspectors(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_image_inspector(self):
        # 1. Buat gambar JPEG dummy dengan data EXIF
        img_path = os.path.join(self.test_dir, "sample.jpg")
        img = Image.new("RGB", (200, 150), color="red")
        exif = img.getexif()
        exif[0x010F] = "Sony Alpha"    # Make
        exif[0x0110] = "ILCE-7M4"      # Model
        exif[0x0131] = "Lightroom 12"  # Software
        img.save(img_path, format="JPEG", exif=exif)

        inspector = ImageInspector()
        self.assertTrue(inspector.can_inspect(img_path))

        res = inspector.inspect(img_path)
        self.assertTrue(res["has_metadata"])
        self.assertIn("EXIF Kamera & Perangkat", res["categories"])
        exif_info = res["categories"]["EXIF Kamera & Perangkat"]
        self.assertIn("Make", exif_info)
        self.assertEqual(exif_info["Make"], "Sony Alpha")
        self.assertEqual(exif_info["Model"], "ILCE-7M4")

    def test_pdf_inspector(self):
        # 2. Buat dokumen PDF dummy dengan metadata
        pdf_path = os.path.join(self.test_dir, "sample.pdf")
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        writer.add_metadata({
            "/Author": "Yogi Ario",
            "/Producer": "Test Python Producer",
            "/Title": "Dokumen Penting"
        })
        with open(pdf_path, "wb") as f:
            writer.write(f)

        inspector = PdfInspector()
        self.assertTrue(inspector.can_inspect(pdf_path))

        res = inspector.inspect(pdf_path)
        self.assertTrue(res["has_metadata"])
        meta = res["categories"]["Metadata Penulis & Aplikasi"]
        self.assertEqual(meta["Author"], "Yogi Ario")
        self.assertEqual(meta["Title"], "Dokumen Penting")

    def test_docx_inspector(self):
        # 3. Buat dokumen DOCX dummy
        docx_path = os.path.join(self.test_dir, "sample.docx")
        doc = Document()
        doc.add_paragraph("Ini adalah contoh isi dokumen.")
        doc.core_properties.author = "Yogi Ario"
        doc.core_properties.title = "Laporan Praktikum"
        doc.save(docx_path)

        inspector = DocxInspector()
        self.assertTrue(inspector.can_inspect(docx_path))

        res = inspector.inspect(docx_path)
        self.assertTrue(res["has_metadata"])
        props = res["categories"]["Properti Dokumen Word"]
        self.assertEqual(props["Penulis (Author)"], "Yogi Ario")
        self.assertEqual(props["Judul"], "Laporan Praktikum")

    def test_text_inspector_with_invisible_watermark(self):
        # 4. Buat berkas teks dengan zero-width character (steganografi AI)
        txt_path = os.path.join(self.test_dir, "ai_sample.txt")
        # Masukkan zero-width space (\u200B) dan zero-width joiner (\u200D)
        watermarked_text = "ChatGPT\u200B menghasilkan teks rahasia\u200D ini."
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(watermarked_text)

        inspector = TextInspector()
        self.assertTrue(inspector.can_inspect(txt_path))

        res = inspector.inspect(txt_path)
        self.assertTrue(res["has_ai_watermark"])
        self.assertGreater(res["metadata_count"], 0)
        self.assertIn("Rincian Watermark Tersembunyi", res["categories"])

    def test_dispatcher(self):
        # 5. Uji dispatcher umum
        txt_path = os.path.join(self.test_dir, "plain.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Teks biasa tanpa watermark.")

        res = inspect_file(txt_path)
        self.assertEqual(res["category"], "text")
        self.assertFalse(res["has_ai_watermark"])

if __name__ == "__main__":
    unittest.main()

