"""
Pengujian Unit untuk Metadata Spoofing & Anonymizer.
"""
import os
import unittest
import tempfile
import shutil
from PIL import Image
from src.editors.spoofing import MetadataSpoofer
from src.inspectors import inspect_file

class TestMetadataSpoofing(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_spoof_jpeg_image(self):
        """Memverifikasi penyuntikan metadata sintetis Canon pada gambar JPEG."""
        jpg_path = os.path.join(self.test_dir, "clean_photo.jpg")
        img = Image.new("RGB", (150, 150), color="green")
        img.save(jpg_path, "JPEG")

        res = MetadataSpoofer.spoof(jpg_path, profile_name="canon", inplace=True)
        self.assertTrue(res["success"])
        self.assertEqual(res["profile_applied"], "Canon EOS 5D Mark IV")

        info = inspect_file(jpg_path)
        exif = info.get("categories", {}).get("EXIF Kamera & Perangkat", {})
        self.assertEqual(exif.get("Make"), "Canon")
        self.assertEqual(exif.get("Model"), "Canon EOS 5D Mark IV")
        self.assertNotIn("Lokasi GPS", info.get("categories", {}))

if __name__ == "__main__":
    unittest.main()
