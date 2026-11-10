"""
Unit Test: Metadata Exporter Utility
"""
import os
import shutil
import tempfile
import unittest
from src.utils.exporter import export_to_json, export_to_text

class TestExporter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.sample_data = [
            {
                "file_path": "C:/dummy/test.jpg",
                "file_name": "test.jpg",
                "file_size": 1024,
                "category": "image",
                "has_metadata": True,
                "has_ai_watermark": False,
                "watermarks_detected": [],
                "categories": {
                    "General": {"Format": "JPEG"},
                    "EXIF": {"Make": "Canon"}
                }
            }
        ]

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_export_json(self):
        out_json = os.path.join(self.test_dir, "report.json")
        ok = export_to_json(self.sample_data, out_json)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(out_json))

    def test_export_text(self):
        out_txt = os.path.join(self.test_dir, "report.txt")
        ok = export_to_text(self.sample_data, out_txt)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(out_txt))
        with open(out_txt, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("METACLEAN — LAPORAN ANALISIS METADATA", content)
            self.assertIn("Canon", content)

if __name__ == "__main__":
    unittest.main()

