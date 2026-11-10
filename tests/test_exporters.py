"""
Unit Tests untuk Modul Exporters (MarkdownExporter & PDFExporter)
Memverifikasi keabsahan struktur output laporan PDF dan Markdown.
"""

import os
import unittest
import tempfile
import shutil
from pypdf import PdfReader

from src.utils.md_exporter import MarkdownExporter
from src.utils.pdf_exporter import PDFExporter

class TestExporters(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.sample_items = [
            {
                "file_name": "clean_doc.pdf",
                "file_path": os.path.join(self.test_dir, "clean_doc.pdf"),
                "file_size": 15000,
                "category": "pdf",
                "has_metadata": False,
                "has_ai_watermark": False,
                "ai_watermark_details": None,
                "metadata": {}
            },
            {
                "file_name": "meta_photo.jpg",
                "file_path": os.path.join(self.test_dir, "meta_photo.jpg"),
                "file_size": 204800,
                "category": "image",
                "has_metadata": True,
                "has_ai_watermark": False,
                "ai_watermark_details": None,
                "metadata": {
                    "EXIF": {
                        "Artist": "Yogi Ario",
                        "Software": "Adobe Photoshop 2026",
                        "Camera": "Sony A7 IV"
                    }
                }
            },
            {
                "file_name": "ai_article.md",
                "file_path": os.path.join(self.test_dir, "ai_article.md"),
                "file_size": 4200,
                "category": "text",
                "has_metadata": False,
                "has_ai_watermark": True,
                "ai_watermark_details": {
                    "Variation Selector 16 (U+FE0F)": "1 karakter ditemukan"
                },
                "metadata": {}
            }
        ]

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_markdown_exporter(self):
        """Memverifikasi ekspor laporan Markdown menghasilkan berkas valid dengan tabel."""
        md_path = os.path.join(self.test_dir, "report.md")
        ok = MarkdownExporter.export(self.sample_items, md_path)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(md_path))

        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("# 🛡️ Laporan Inspeksi Metadata & Tanda Air AI — Mrclean", content)
        self.assertIn("clean_doc.pdf", content)
        self.assertIn("meta_photo.jpg", content)
        self.assertIn("ai_article.md", content)
        self.assertIn("Yogi Ario", content)
        self.assertIn("Sony A7 IV", content)
        self.assertIn("Tanda Air / Steganografi AI Terdeteksi", content)

    def test_pdf_exporter(self):
        """Memverifikasi ekspor laporan PDF menghasilkan dokumen PDF valid yang terbaca."""
        pdf_path = os.path.join(self.test_dir, "report.pdf")
        ok = PDFExporter.export(self.sample_items, pdf_path)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 500)

        # Verifikasi bahwa PDF dapat diparsing oleh pypdf
        reader = PdfReader(pdf_path)
        self.assertGreater(len(reader.pages), 0)
        text_first_page = reader.pages[0].extract_text()
        self.assertIn("Laporan Analisis Metadata", text_first_page)

if __name__ == "__main__":
    unittest.main()

