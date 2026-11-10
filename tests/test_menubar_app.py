"""
tests/test_menubar_app.py — Pengujian macOS Menu Bar Status Item App
"""
import unittest
from PIL import Image
from src.gui.menubar_app import MrCleanMenuBarApp

class TestMenuBarApp(unittest.TestCase):
    """Pengujian inisialisasi dan konfigurasi Menu Bar Status Item."""

    def test_menubar_app_initialization(self):
        """Memverifikasi inisialisasi status item dan dimensi ikon 22x22."""
        app = MrCleanMenuBarApp()
        self.assertIsNotNone(app.icon)
        self.assertEqual(app.icon.title, "MrClean Mac")

        img = app._get_image()
        self.assertIsInstance(img, Image.Image)
        self.assertEqual(img.size, (22, 22))

if __name__ == "__main__":
    unittest.main()
