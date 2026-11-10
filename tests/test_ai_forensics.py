"""
Pengujian Unit untuk AI Forensics & C2PA Cleaner.
"""
import os
import unittest
import tempfile
import shutil
from PIL import Image, PngImagePlugin
from src.inspectors.ai_forensics import AIForensicsInspector
from src.cleaners.c2pa_cleaner import C2PACleaner

class TestAIForensics(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_detect_stable_diffusion_parameters(self):
        """Memverifikasi deteksi prompt Stable Diffusion dalam PNG chunk."""
        png_path = os.path.join(self.test_dir, "ai_image.png")
        img = Image.new("RGB", (100, 100), color="purple")
        
        meta = PngImagePlugin.PngInfo()
        meta.add_text("parameters", "a beautiful cyberpunk city at night, neon lights\nNegative prompt: ugly, blurry\nSteps: 20, Sampler: DPM++ 2M, Seed: 123456")
        img.save(png_path, "PNG", pnginfo=meta)

        info = AIForensicsInspector.inspect_ai_metadata(png_path)
        self.assertTrue(info["is_ai_generated"])
        self.assertEqual(info["generator"], "Stable Diffusion")
        self.assertIn("cyberpunk city", info["prompt"])

        # Test C2PACleaner
        res = C2PACleaner.clean_ai_and_c2pa(png_path, inplace=True)
        self.assertTrue(res["success"])

        # Verifikasi setelah dibersihkan
        info_cleaned = AIForensicsInspector.inspect_ai_metadata(png_path)
        self.assertFalse(info_cleaned["is_ai_generated"])
        self.assertIsNone(info_cleaned["prompt"])

    def test_detect_c2pa_manifest(self):
        """Memverifikasi deteksi bytes C2PA provenance."""
        dummy_c2pa = os.path.join(self.test_dir, "c2pa_mock.jpg")
        with open(dummy_c2pa, "wb") as f:
            f.write(b"\xff\xd8\xff\xe1\x00\x18c2pa contentCredentials jumbf mock binary data")

        info = AIForensicsInspector.inspect_ai_metadata(dummy_c2pa)
        self.assertTrue(info["is_ai_generated"])
        self.assertTrue(info["has_c2pa"])

if __name__ == "__main__":
    unittest.main()
