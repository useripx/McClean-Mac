"""
MetaClean — Windows Shell Integration (Context Menu)
Mengelola penambahan pintasan menu klik kanan Windows Explorer (HKCU)
agar pengguna dapat membersihkan metadata langsung dari file explorer tanpa hak Administrator.
"""
import os
import sys
from typing import Tuple

try:
    import winreg
except ImportError:
    winreg = None

class WindowsShellIntegration:
    """Pengelola registrasi menu klik kanan Windows Explorer via HKCU."""

    MENU_TEXT_FILE = "🛡️ Bersihkan Metadata dengan Mrclean"
    MENU_TEXT_DIR = "📁 Pindai & Bersihkan dengan Mrclean"
    KEY_NAME = "Mrclean"

    @classmethod
    def get_executable_or_script_command(cls) -> str:
        """Menentukan perintah eksekusi yang tepat (apakah .exe atau python main.py)."""
        if getattr(sys, 'frozen', False):
            # Berjalan sebagai .exe mandiri
            exe_path = os.path.abspath(sys.executable)
            return f'"{exe_path}" "%1"'
        else:
            # Berjalan via Python interpreter
            py_exe = os.path.abspath(sys.executable)
            main_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
            return f'"{py_exe}" "{main_script}" "%1"'

    @classmethod
    def get_icon_path(cls) -> str:
        """Menemukan path ikon .ico aplikasi."""
        candidates = [
            os.path.abspath("assets/icon.ico"),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icon.ico"))
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return ""

    @classmethod
    def is_installed(cls) -> bool:
        """Mengecek apakah menu klik kanan sudah terpasang di registri HKCU."""
        if not winreg or sys.platform != "win32":
            return False
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\*\shell\{cls.KEY_NAME}"):
                return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    @classmethod
    def install(cls) -> Tuple[bool, str]:
        """Memasang menu klik kanan untuk semua berkas dan folder di bawah HKCU."""
        if not winreg or sys.platform != "win32":
            return False, "Sistem operasi bukan Windows atau winreg tidak tersedia."

        try:
            cmd = cls.get_executable_or_script_command()
            icon = cls.get_icon_path()

            # 1. Daftarkan untuk Berkas Tunggal (*)
            file_key_path = rf"Software\Classes\*\shell\{cls.KEY_NAME}"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, file_key_path) as k:
                winreg.SetValueEx(k, "", 0, winreg.REG_SZ, cls.MENU_TEXT_FILE)
                if icon:
                    winreg.SetValueEx(k, "Icon", 0, winreg.REG_SZ, icon)

            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"{file_key_path}\command") as cmd_k:
                winreg.SetValueEx(cmd_k, "", 0, winreg.REG_SZ, cmd)

            # 2. Daftarkan untuk Direktori / Folder
            dir_key_path = rf"Software\Classes\Directory\shell\{cls.KEY_NAME}"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, dir_key_path) as k:
                winreg.SetValueEx(k, "", 0, winreg.REG_SZ, cls.MENU_TEXT_DIR)
                if icon:
                    winreg.SetValueEx(k, "Icon", 0, winreg.REG_SZ, icon)

            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"{dir_key_path}\command") as cmd_k:
                winreg.SetValueEx(cmd_k, "", 0, winreg.REG_SZ, cmd)

            return True, "Menu klik kanan Windows Explorer berhasil dipasang!"

        except Exception as e:
            return False, f"Gagal memasang menu registri: {str(e)}"

    @classmethod
    def uninstall(cls) -> Tuple[bool, str]:
        """Menghapus menu klik kanan dari registri HKCU."""
        if not winreg or sys.platform != "win32":
            return False, "Sistem operasi bukan Windows."

        targets = [
            rf"Software\Classes\*\shell\{cls.KEY_NAME}",
            rf"Software\Classes\Directory\shell\{cls.KEY_NAME}"
        ]

        try:
            for t in targets:
                try:
                    # Hapus subkey command terlebih dahulu
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, rf"{t}\command")
                except FileNotFoundError:
                    pass
                try:
                    # Hapus key utama
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, t)
                except FileNotFoundError:
                    pass

            return True, "Menu klik kanan Windows Explorer berhasil dicopot!"

        except Exception as e:
            return False, f"Gagal mencopot menu registri: {str(e)}"
