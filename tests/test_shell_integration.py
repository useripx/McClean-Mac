"""
Pengujian Unit untuk Windows Shell Integration (Menu Klik Kanan).
"""
import sys
import unittest
from src.utils.shell_integration import WindowsShellIntegration

class TestWindowsShellIntegration(unittest.TestCase):

    def test_command_string_generation(self):
        """Memverifikasi perintah shell mencakup path dan parameter %1."""
        cmd = WindowsShellIntegration.get_executable_or_script_command()
        self.assertIn('"%1"', cmd)
        self.assertTrue(cmd.startswith('"'))

    @unittest.skipUnless(sys.platform == "win32", "Hanya berjalan di sistem operasi Windows")
    def test_install_and_uninstall_lifecycle(self):
        """Memverifikasi siklus hidup pemasangan dan pencopotan menu registri HKCU."""
        # 1. Pasang
        ok, msg = WindowsShellIntegration.install()
        self.assertTrue(ok, f"Install gagal: {msg}")
        self.assertTrue(WindowsShellIntegration.is_installed())

        # 2. Copot
        ok_un, msg_un = WindowsShellIntegration.uninstall()
        self.assertTrue(ok_un, f"Uninstall gagal: {msg_un}")
        self.assertFalse(WindowsShellIntegration.is_installed())

if __name__ == "__main__":
    unittest.main()
