"""
Pengujian Unit untuk Icon Converter (icon.icns & logo.png).
"""
import os
import unittest
import tempfile
import shutil
from PIL import Image
from src.utils.icon_converter import convert_logo_to_assets

class TestIconConverter(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.raw_logo = os.path.join(self.test_dir, "raw_logo.png")
        # Buat gambar dummy 512x512
        img = Image.new("RGBA", (512, 512), color="purple")
        img.save(self.raw_logo)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_convert_logo_to_assets_macos(self):
        """Memverifikasi bahwa icon.icns, icon.ico, dan logo.png berhasil dihasilkan."""
        icns_out = os.path.join(self.test_dir, "icon.icns")
        ico_out = os.path.join(self.test_dir, "icon.ico")
        png_out = os.path.join(self.test_dir, "logo.png")

        res = convert_logo_to_assets(
            primary_input=self.raw_logo,
            icns_output=icns_out,
            ico_output=ico_out,
            png_output=png_out
        )

        self.assertTrue(os.path.exists(icns_out))
        self.assertTrue(os.path.exists(ico_out))
        self.assertTrue(os.path.exists(png_out))
        self.assertGreater(os.path.getsize(icns_out), 0)
        self.assertGreater(os.path.getsize(png_out), 0)

if __name__ == "__main__":
    unittest.main()
