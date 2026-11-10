"""
Unit Test: AI Watermarks & Steganography Cleaner
"""
import os
import shutil
import tempfile
import unittest
from src.watermarks.ai_cleaner import AIWatermarkCleaner
from src.inspectors.text_inspector import TextInspector

class TestAIWatermarks(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_clean_text_watermarks_string(self):
        # Teks dengan invisible characters: U+200B (ZWSP), U+200C (ZWNJ), U+200D (ZWJ), U+FEFF (BOM), U+FE00 (Variation Selector)
        raw_text = "Artikel\u200B ini ditulis\u200C secara orisinal\u200D tanpa\uFEFF jejak\uFE00 AI."
        expected_text = "Artikel ini ditulis secara orisinal tanpa jejak AI."

        cleaned, stats = AIWatermarkCleaner.clean_text_watermarks(raw_text)
        self.assertEqual(cleaned, expected_text)
        self.assertEqual(stats["total_watermarks_removed"], 5)
        self.assertIn("Zero-Width Space (U+200B)", stats["breakdown"])
        self.assertIn("Zero-Width Joiner (U+200D)", stats["breakdown"])

    def test_clean_file_text_watermarks(self):
        file_path = os.path.join(self.test_dir, "ai_prompt_output.txt")
        out_path = os.path.join(self.test_dir, "clean_output.txt")

        watermarked_content = "Halo Mas Yogi!\u200B\u200D Sistem siap diuji."
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(watermarked_content)

        res = AIWatermarkCleaner.clean_file(file_path, out_path)
        self.assertTrue(res["success"])
        self.assertEqual(res["watermarks_removed"], 2)

        # Verifikasi dengan inspektor
        inspector = TextInspector()
        inspect_res = inspector.inspect(out_path)
        self.assertFalse(inspect_res["has_ai_watermark"])
        self.assertEqual(inspect_res["metadata_count"], 0)

if __name__ == "__main__":
    unittest.main()

