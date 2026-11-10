"""
Unit Test: File & Folder Scanner
"""
import os
import shutil
import tempfile
import unittest
from src.utils.scanner import scan_files, get_file_category

class TestScanner(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Buat dummy files di folder sementara
        self.img_file = os.path.join(self.test_dir, "test1.jpg")
        self.pdf_file = os.path.join(self.test_dir, "document.pdf")
        self.txt_file = os.path.join(self.test_dir, "notes.txt")
        self.doc_file = os.path.join(self.test_dir, "report.docx")

        for fpath in [self.img_file, self.pdf_file, self.txt_file, self.doc_file]:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write("dummy content")

        # Buat subdirektori
        self.sub_dir = os.path.join(self.test_dir, "sub")
        os.makedirs(self.sub_dir, exist_ok=True)
        self.sub_img = os.path.join(self.sub_dir, "nested.png")
        with open(self.sub_img, "w", encoding="utf-8") as f:
            f.write("dummy nested")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_file_category(self):
        self.assertEqual(get_file_category("foto.jpg"), "image")
        self.assertEqual(get_file_category("arsip.pdf"), "pdf")
        self.assertEqual(get_file_category("tugas.docx"), "docx")
        self.assertEqual(get_file_category("musik.mp3"), "media")
        self.assertEqual(get_file_category("README.md"), "markdown")
        self.assertEqual(get_file_category("index.html"), "coding")
        self.assertEqual(get_file_category("script.py"), "coding")
        self.assertEqual(get_file_category("artikel.txt"), "text")
        self.assertEqual(get_file_category("unknown.xyz"), "unknown")

    def test_scan_single_file(self):
        results = scan_files([self.img_file])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "test1.jpg")
        self.assertEqual(results[0]["category"], "image")

    def test_scan_folder_recursive(self):
        results = scan_files([self.test_dir], recursive=True)
        # Mengharapkan 5 file (4 di root + 1 di subfolder)
        self.assertEqual(len(results), 5)
        names = {r["name"] for r in results}
        self.assertIn("test1.jpg", names)
        self.assertIn("nested.png", names)

    def test_scan_folder_non_recursive(self):
        results = scan_files([self.test_dir], recursive=False)
        # Mengharapkan 4 file di root folder saja
        self.assertEqual(len(results), 4)
        names = {r["name"] for r in results}
        self.assertNotIn("nested.png", names)

if __name__ == "__main__":
    unittest.main()

