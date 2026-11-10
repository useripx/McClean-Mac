"""
tests/test_cli.py — Pengujian Headless CLI MrClean Mac (v2.0.0-macos)
"""
import os
import sys
import json
import shutil
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

from PIL import Image
import piexif

from src.cli import main, VERSION

class TestCLI(unittest.TestCase):
    """Pengujian fungsionalitas Headless CLI MrClean Mac."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        # Buat dummy image dengan EXIF
        self.img_path = os.path.join(self.temp_dir, "test_cli.jpg")
        img = Image.new("RGB", (100, 100), color=(120, 150, 180))
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Make: b"Apple",
                piexif.ImageIFD.Model: b"iPhone 15 Pro",
                piexif.ImageIFD.Software: b"iOS 17.4"
            },
            "Exif": {},
            "GPS": {
                piexif.GPSIFD.GPSLatitude: ((37, 1), (46, 1), (2976, 100)),
                piexif.GPSIFD.GPSLatitudeRef: b"N"
            }
        }
        exif_bytes = piexif.dump(exif_dict)
        img.save(self.img_path, exif=exif_bytes)

        # Buat dummy source code dengan local path
        self.code_path = os.path.join(self.temp_dir, "test_code.py")
        with open(self.code_path, "w", encoding="utf-8") as f:
            f.write("# Author: yogi\n# Path: /Users/yogi/secret/app.py\nprint('hello')\n")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_version(self):
        """Memverifikasi bahwa flag --version menampilkan versi yang benar."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            try:
                main(["-v"])
            except SystemExit as e:
                self.assertEqual(e.code, 0)
            output = fake_out.getvalue()
            self.assertIn("MrClean Mac", output)
            self.assertIn(VERSION, output)

    def test_cli_inspect_text_output(self):
        """Memverifikasi perintah inspect dengan format konsol teks standar."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            exit_code = main(["inspect", self.img_path])
            self.assertEqual(exit_code, 0)
            output = fake_out.getvalue()
            self.assertIn("HASIL INSPEKSI METADATA", output)
            self.assertIn("test_cli.jpg", output)
            self.assertIn("IMAGE", output)

    def test_cli_inspect_json_output(self):
        """Memverifikasi perintah inspect dengan flag --json menghasilkan JSON valid."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            exit_code = main(["inspect", self.img_path, "--json"])
            self.assertEqual(exit_code, 0)
            output = fake_out.getvalue()
            data = json.loads(output)
            self.assertEqual(data.get("category"), "image")
            self.assertTrue(data.get("has_metadata"))
            self.assertTrue(any("EXIF" in k for k in data.get("categories", {}).keys()))

    def test_cli_clean_file_to_output_dir(self):
        """Memverifikasi perintah clean menyimpan berkas bersih ke folder target."""
        out_dir = os.path.join(self.temp_dir, "cleaned_output")
        os.makedirs(out_dir, exist_ok=True)

        with patch("sys.stdout", new=StringIO()) as fake_out:
            exit_code = main(["clean", self.img_path, "-o", out_dir])
            self.assertEqual(exit_code, 0)
            output = fake_out.getvalue()
            self.assertIn("[SUKSES]", output)

            expected_out = os.path.join(out_dir, "test_cli.jpg")
            self.assertTrue(os.path.exists(expected_out))

    def test_cli_clean_with_preset_dev_inplace(self):
        """Memverifikasi perintah clean dengan preset developer in-place."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            exit_code = main(["clean", self.code_path, "--preset", "dev", "--inplace"])
            self.assertEqual(exit_code, 0)
            output = fake_out.getvalue()
            self.assertIn("[SUKSES]", output)

        with open(self.code_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("/Users/yogi/secret/", content)
        self.assertIn("/Users/user/secret/", content)

    def test_cli_spoof_image(self):
        """Memverifikasi perintah spoof menyuntikkan profil kamera sintetis."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            exit_code = main(["spoof", self.img_path, "--profile", "canon", "--inplace"])
            self.assertEqual(exit_code, 0)
            output = fake_out.getvalue()
            self.assertIn("[SUKSES]", output)
            self.assertIn("CANON", output)

    def test_cli_non_existent_target(self):
        """Memverifikasi bahwa target berkas yang tidak ada menghasilkan exit code 1."""
        non_existent = os.path.join(self.temp_dir, "ghost_file.jpg")
        with patch("sys.stderr", new=StringIO()) as fake_err:
            exit_code = main(["inspect", non_existent])
            self.assertEqual(exit_code, 1)
            err_msg = fake_err.getvalue()
            self.assertIn("[ERROR]", err_msg)

if __name__ == "__main__":
    unittest.main()
