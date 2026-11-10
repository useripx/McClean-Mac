"""
tests/test_homebrew_cask.py — Pengujian Integritas Formula Homebrew Cask (MrClean Mac)
"""
import os
import unittest

class TestHomebrewCask(unittest.TestCase):
    """Memvalidasi integritas dan kelengkapan formula Homebrew Cask."""

    def setUp(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.cask_path = os.path.join(self.project_root, "packaging", "homebrew", "mrclean.rb")
        self.readme_path = os.path.join(self.project_root, "packaging", "homebrew", "README.md")

    def test_cask_file_exists(self):
        """Memverifikasi bahwa file formula mrclean.rb dan README.md ada."""
        self.assertTrue(os.path.exists(self.cask_path), "Berkas mrclean.rb tidak ditemukan!")
        self.assertTrue(os.path.exists(self.readme_path), "Berkas README.md Homebrew tidak ditemukan!")

    def test_cask_dsl_structure(self):
        """Memverifikasi sintaks dan struktur blok Cask DSL Ruby."""
        with open(self.cask_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('cask "mrclean" do', content)
        self.assertIn('version "2.0.0"', content)
        self.assertIn('url "https://github.com/useripx/McClean-Mac/releases/download/v#{version}/MrClean-macOS.dmg"', content)
        self.assertIn('app "MrClean.app"', content)
        self.assertIn('binary "#{appdir}/MrClean.app/Contents/MacOS/MrClean", target: "mrclean"', content)
        self.assertIn('zap trash:', content)

if __name__ == "__main__":
    unittest.main()
