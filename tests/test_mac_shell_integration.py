"""
Pengujian Unit untuk macOS Shell & Finder Integration (MacShellIntegration).
"""
import os
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from src.utils.mac_shell_integration import MacShellIntegration

class TestMacShellIntegration(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_services_dir = MacShellIntegration.SERVICES_DIR
        # Arahkan folder services ke temp dir agar tidak mengganggu sistem
        MacShellIntegration.SERVICES_DIR = self.test_dir

    def tearDown(self):
        MacShellIntegration.SERVICES_DIR = self.original_services_dir
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_install_and_uninstall_lifecycle(self):
        """Memverifikasi siklus hidup instalasi dan pencopotan Quick Action Finder."""
        self.assertFalse(MacShellIntegration.is_installed())

        # Test Install
        ok, msg = MacShellIntegration.install()
        self.assertTrue(ok)
        self.assertTrue(MacShellIntegration.is_installed())

        service_path = MacShellIntegration.get_service_path()
        self.assertTrue(os.path.isdir(service_path))
        self.assertTrue(os.path.isfile(os.path.join(service_path, "Contents", "Info.plist")))
        self.assertTrue(os.path.isfile(os.path.join(service_path, "Contents", "document.wflow")))

        # Test Uninstall
        ok_un, msg_un = MacShellIntegration.uninstall()
        self.assertTrue(ok_un)
        self.assertFalse(MacShellIntegration.is_installed())

    def test_executable_command_resolution(self):
        """Memverifikasi format string perintah eksekusi."""
        cmd = MacShellIntegration.get_executable_or_command()
        self.assertIn("main.py", cmd)

    @patch("subprocess.run")
    def test_notify_user_macos(self, mock_run):
        """Memverifikasi pengiriman notifikasi osascript pada macOS."""
        mock_run.return_value = MagicMock(returncode=0)
        with patch("sys.platform", "darwin"):
            res = MacShellIntegration.notify_user("MrClean Mac", "Pembersihan Selesai!")
            self.assertTrue(res)
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            self.assertEqual(args[0], "osascript")
            self.assertIn("Pembersihan Selesai!", args[2])

if __name__ == "__main__":
    unittest.main()
