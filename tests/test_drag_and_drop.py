"""
Pengujian Unit untuk fitur Drag and Drop & macOS OpenDocument Event.
"""
import os
import unittest
import tempfile
import shutil
from src.gui.app import MetaCleanApp

class TestDragAndDrop(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.file1 = os.path.join(self.test_dir, "test1.txt")
        self.file2 = os.path.join(self.test_dir, "space file.jpg")
        with open(self.file1, "w") as f:
            f.write("test content")
        with open(self.file2, "w") as f:
            f.write("fake jpg")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_parse_dropped_files_with_spaces_and_braces(self):
        """Memverifikasi parsing string drop data dengan spasi dan format kurung kurawal."""
        # Format TkinterDnD: {/path/to/space file.jpg} /path/to/test1.txt
        raw_data = f"{{{self.file2}}} {self.file1}"
        parsed = MetaCleanApp.parse_dropped_files(raw_data)

        self.assertEqual(len(parsed), 2)
        self.assertIn(os.path.abspath(self.file1), parsed)
        self.assertIn(os.path.abspath(self.file2), parsed)

    def test_parse_dropped_files_non_existent_filtered(self):
        """Memverifikasi bahwa file yang tidak ada disaring keluar."""
        fake_file = os.path.join(self.test_dir, "does_not_exist.png")
        raw_data = f"{self.file1} {fake_file}"
        parsed = MetaCleanApp.parse_dropped_files(raw_data)

        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0], os.path.abspath(self.file1))

    def test_parse_empty_data(self):
        """Memverifikasi bahwa string kosong mengembalikan list kosong."""
        self.assertEqual(MetaCleanApp.parse_dropped_files(""), [])
        self.assertEqual(MetaCleanApp.parse_dropped_files(None), [])

if __name__ == "__main__":
    unittest.main()
