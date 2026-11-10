"""
Unit Test: Metadata Cleaners
"""
import os
import shutil
import tempfile
import unittest
from PIL import Image
from pypdf import PdfWriter
from docx import Document
from src.cleaners import clean_file
from src.cleaners.image_cleaner import ImageCleaner
from src.cleaners.pdf_cleaner import PdfCleaner
from src.cleaners.docx_cleaner import DocxCleaner
from src.cleaners.text_cleaner import TextCleaner
from src.inspectors.image_inspector import ImageInspector
from src.inspectors.pdf_inspector import PdfInspector
from src.inspectors.docx_inspector import DocxInspector
from src.inspectors.text_inspector import TextInspector

class TestCleaners(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_image_cleaner(self):
        # Buat gambar dengan EXIF
        in_path = os.path.join(self.test_dir, "foto_exif.jpg")
        out_path = os.path.join(self.test_dir, "foto_clean.jpg")
        img = Image.new("RGB", (300, 200), color="green")
        exif = img.getexif()
        exif[0x010F] = "Canon"
        exif[0x0110] = "EOS R5"
        img.save(in_path, format="JPEG", exif=exif)

        cleaner = ImageCleaner()
        res = cleaner.clean(in_path, out_path)
        self.assertTrue(res["success"])
        self.assertTrue(os.path.exists(out_path))

        # Verifikasi hasil pembersihan dengan inspektor
        inspector = ImageInspector()
        inspect_res = inspector.inspect(out_path)
        # EXIF harus kosong
        self.assertNotIn("EXIF Kamera & Perangkat", inspect_res["categories"])
        # Dimensi gambar harus tetap utuh (300 x 200)
        self.assertIn("300 x 200 piksel", inspect_res["categories"]["Umum"]["Dimensi"])

    def test_pdf_cleaner(self):
        # Buat PDF dengan Author
        in_path = os.path.join(self.test_dir, "dokumen.pdf")
        out_path = os.path.join(self.test_dir, "dokumen_clean.pdf")
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        writer.add_metadata({"/Author": "Secret Author", "/Producer": "Confidential"})
        with open(in_path, "wb") as f:
            writer.write(f)

        cleaner = PdfCleaner()
        res = cleaner.clean(in_path, out_path)
        self.assertTrue(res["success"])

        # Verifikasi hasil pembersihan
        inspector = PdfInspector()
        inspect_res = inspector.inspect(out_path)
        self.assertFalse(inspect_res["has_metadata"])

    def test_docx_cleaner(self):
        # Buat DOCX dengan Author
        in_path = os.path.join(self.test_dir, "surat.docx")
        out_path = os.path.join(self.test_dir, "surat_clean.docx")
        doc = Document()
        doc.add_paragraph("Isi surat rahasia.")
        doc.core_properties.author = "Yogi Ario"
        doc.save(in_path)

        cleaner = DocxCleaner()
        res = cleaner.clean(in_path, out_path)
        self.assertTrue(res["success"])

        # Verifikasi hasil pembersihan
        inspector = DocxInspector()
        inspect_res = inspector.inspect(out_path)
        self.assertFalse(inspect_res["has_metadata"])

    def test_markdown_cleaner(self):
        # Uji khusus berkas README.md dengan Variation Selector-16 (U+FE0F) dan Zero-Width Space
        in_path = os.path.join(self.test_dir, "README.md")
        out_path = os.path.join(self.test_dir, "README_clean.md")
        
        md_content = "# Judul Proyek\uFE0F\n\nDeskripsi teks AI rahasia\u200B di sini."
        with open(in_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Uji via clean_file dispatcher utama
        res = clean_file(in_path, out_path)
        self.assertTrue(res["success"])
        self.assertTrue(os.path.exists(out_path))

        # Verifikasi hasil pembersihan menggunakan TextInspector
        inspector = TextInspector()
        inspect_res = inspector.inspect(out_path)
        self.assertFalse(inspect_res["has_ai_watermark"])
        self.assertEqual(inspect_res["metadata_count"], 0)

        with open(out_path, "r", encoding="utf-8") as f:
            cleaned_text = f.read()
        self.assertEqual(cleaned_text, "# Judul Proyek\n\nDeskripsi teks AI rahasia di sini.")

    def test_markdown_cleaner_inplace(self):
        # Uji pembersihan langsung di tempat (in-place) pada berkas asli
        target_path = os.path.join(self.test_dir, "DIRECT_README.md")
        content = "# Dokumentasi\uFE0F\n\nTeks rahasia\u200D AI."
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Jalankan clean_file dengan inplace=True
        res = clean_file(target_path, inplace=True)
        self.assertTrue(res["success"])
        self.assertTrue(res["inplace"])

        # Verifikasi bahwa berkas asli sekarang 100% bersih tanpa watermark
        inspector = TextInspector()
        inspect_res = inspector.inspect(target_path)
        self.assertFalse(inspect_res["has_ai_watermark"])
        self.assertEqual(inspect_res["metadata_count"], 0)

        with open(target_path, "r", encoding="utf-8") as f:
            new_content = f.read()
        self.assertEqual(new_content, "# Dokumentasi\n\nTeks rahasia AI.")

    def test_html_cleaner(self):
        # Uji berkas HTML berkode
        in_path = os.path.join(self.test_dir, "index.html")
        out_path = os.path.join(self.test_dir, "index_clean.html")

        html_content = "<html>\u200C<body><h1>Halo\u200D Dunia</h1></body></html>"
        with open(in_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        res = clean_file(in_path, out_path)
        self.assertTrue(res["success"])

        inspector = TextInspector()
        inspect_res = inspector.inspect(out_path)
        self.assertFalse(inspect_res["has_ai_watermark"])

    def test_code_cleaner(self):
        # Uji berkas skrip Python (.py)
        in_path = os.path.join(self.test_dir, "app.py")
        out_path = os.path.join(self.test_dir, "app_clean.py")

        code_content = "def hello():\n    print('Hello\u200B World')\n"
        with open(in_path, "w", encoding="utf-8") as f:
            f.write(code_content)

        res = clean_file(in_path, out_path)
        self.assertTrue(res["success"])

        with open(out_path, "r", encoding="utf-8") as f:
            cleaned_code = f.read()
        self.assertEqual(cleaned_code, "def hello():\n    print('Hello World')\n")

    def test_dispatcher_clean(self):
        in_path = os.path.join(self.test_dir, "auto.jpg")
        img = Image.new("RGB", (100, 100), color="yellow")
        img.save(in_path, format="JPEG")

        res = clean_file(in_path)
        self.assertTrue(res["success"])
        self.assertTrue(os.path.exists(res["output_path"]))

if __name__ == "__main__":
    unittest.main()
