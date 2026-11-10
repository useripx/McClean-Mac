"""
Pengujian Unit untuk Quick Clean Presets.
"""
import os
import unittest
import tempfile
import shutil
from PIL import Image
from src.cleaners.preset_cleaner import PresetCleaner
from src.inspectors import inspect_file

class TestQuickCleanPresets(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_social_media_preset_image(self):
        """Memverifikasi preset media sosial membersihkan metadata pada gambar."""
        img_path = os.path.join(self.test_dir, "photo.jpg")
        img = Image.new("RGB", (100, 100), color="blue")
        exif = img.getexif()
        exif[271] = "Apple"  # Make
        exif[272] = "iPhone 15 Pro"  # Model
        img.save(img_path, exif=exif)

        res = PresetCleaner.clean_with_preset(img_path, preset_key="social_media", inplace=True)
        self.assertTrue(res.get("success"))

        info = inspect_file(img_path)
        self.assertNotIn("EXIF Kamera & Perangkat", info.get("categories", {}))

    def test_developer_preset_code_file(self):
        """Memverifikasi preset developer menyamarkan path C:\\Users\\yogi\\ dan /Users/yogi/ serta membersihkan zero-width watermark."""
        code_path = os.path.join(self.test_dir, "script.py")
        content_with_leak = "# Author: Yogi\n# Path: C:\\Users\\yogi\\Desktop\\secret.py\n# Mac Path: /Users/yogia/Projects/secret.py\nprint('hello\uFE0Fworld')\n"
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(content_with_leak)

        res = PresetCleaner.clean_with_preset(code_path, preset_key="developer", inplace=True)
        self.assertTrue(res.get("success"))

        with open(code_path, "r", encoding="utf-8") as f:
            cleaned_code = f.read()

        self.assertNotIn("C:\\Users\\yogi", cleaned_code)
        self.assertNotIn("/Users/yogia", cleaned_code)
        self.assertNotIn("\uFE0F", cleaned_code)
        self.assertIn("C:\\Users\\User", cleaned_code)
        self.assertIn("/Users/user", cleaned_code)

if __name__ == "__main__":
    unittest.main()
