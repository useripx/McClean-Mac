"""
tests/test_notarization_script.py — Pengujian Skrip Notarisasi Apple Developer
"""
import os
import unittest
from tools.notarize_mac import (
    build_codesign_command,
    build_notarize_command,
    build_staple_command,
    notarize_app
)

class TestNotarizationScript(unittest.TestCase):
    """Pengujian generator perintah codesign dan notarytool."""

    def test_build_codesign_command(self):
        """Memverifikasi struktur flag codesign yang aman dan ketat."""
        cmd = build_codesign_command("dist/MrClean.app", "Developer ID: Yogi Ario (1234567890)")
        self.assertIn("codesign", cmd)
        self.assertIn("--deep", cmd)
        self.assertIn("--force", cmd)
        self.assertIn("--options", cmd)
        self.assertIn("runtime", cmd)
        self.assertIn("dist/MrClean.app", cmd)

    def test_build_notarize_command(self):
        """Memverifikasi pembentukan perintah xcrun notarytool submit."""
        cmd = build_notarize_command(
            "dist/MrClean-macOS.dmg",
            "developer@example.com",
            "TEAM123456",
            "secret-app-password"
        )
        self.assertIn("xcrun", cmd)
        self.assertIn("notarytool", cmd)
        self.assertIn("submit", cmd)
        self.assertIn("--apple-id", cmd)
        self.assertIn("developer@example.com", cmd)
        self.assertIn("--team-id", cmd)
        self.assertIn("TEAM123456", cmd)
        self.assertIn("--password", cmd)
        self.assertIn("secret-app-password", cmd)
        self.assertIn("--wait", cmd)

    def test_build_staple_command(self):
        """Memverifikasi perintah stapling tiket notarisasi."""
        cmd = build_staple_command("dist/MrClean-macOS.dmg")
        self.assertEqual(cmd, ["xcrun", "stapler", "staple", "dist/MrClean-macOS.dmg"])

    def test_notarize_app_dry_run(self):
        """Memverifikasi bahwa mode dry-run berjalan sukses tanpa error."""
        res = notarize_app(
            app_path="dist/MrClean.app",
            dmg_path="dist/MrClean-macOS.dmg",
            identity="Developer ID Application: Dummy",
            apple_id="dummy@example.com",
            team_id="DUMMY123",
            password="dummy-password",
            dry_run=True
        )
        self.assertEqual(res, 0)

if __name__ == "__main__":
    unittest.main()
