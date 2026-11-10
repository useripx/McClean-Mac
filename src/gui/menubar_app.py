"""
src/gui/menubar_app.py — macOS Menu Bar / Status Item Application (v2.0.0-macos)

Menghadirkan ikon status di bar atas layar macOS (NSStatusItem) untuk
memungkinkan pembersihan metadata kilat tanpa harus membuka jendela utama.
"""
import sys
import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from typing import Optional, List
from PIL import Image

try:
    import pystray
    from pystray import MenuItem as item
except ImportError:
    pystray = None

from src.cleaners import clean_file
from src.cleaners.preset_cleaner import PresetCleaner
from src.utils.mac_shell_integration import MacShellIntegration

class MrCleanMenuBarApp:
    """Aplikasi Menu Bar macOS (Status Item)."""

    def __init__(self, icon_path: Optional[str] = None):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.icon_path = icon_path or os.path.join(self.project_root, "assets", "logo.png")
        self.icon = None
        self._setup_icon()

    def _get_image(self) -> Image.Image:
        """Memuat gambar ikon status bar (22x22 standar macOS Menu Bar)."""
        if os.path.exists(self.icon_path):
            img = Image.open(self.icon_path)
            return img.resize((22, 22), Image.Resampling.LANCZOS)
        # Fallback jika aset belum di-generate
        return Image.new("RGBA", (22, 22), color=(40, 120, 240, 255))

    def _setup_icon(self):
        """Menyiapkan struktur menu dan status item pystray."""
        if pystray is None:
            return

        image = self._get_image()
        menu = pystray.Menu(
            item("MrClean Mac (v2.0.0)", None, enabled=False),
            pystray.Menu.SEPARATOR,
            item("🧹 Pembersihan Kilat (Quick Clean)...", self.on_quick_clean),
            item("⚡ Preset Pembersihan", pystray.Menu(
                item("💻 Developer (Samarkan Path)", lambda: self.on_quick_clean_preset("developer")),
                item("📱 Media Sosial (Hapus EXIF & GPS)", lambda: self.on_quick_clean_preset("social_media")),
                item("🎓 Akademik (Hapus Author & Watermark)", lambda: self.on_quick_clean_preset("academic")),
            )),
            pystray.Menu.SEPARATOR,
            item("🖥️ Buka Jendela Utama MrClean", self.on_open_main_app),
            pystray.Menu.SEPARATOR,
            item("❌ Keluar (Quit)", self.on_quit)
        )

        self.icon = pystray.Icon("MrClean", image, "MrClean Mac", menu)

    def _prompt_files(self) -> List[str]:
        """Menampilkan dialog pemilih berkas macOS tanpa menampilkan root window Tk."""
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        files = filedialog.askopenfilenames(
            title="Pilih Berkas untuk Dibersihkan (MrClean)",
            parent=root
        )
        root.destroy()
        return list(files) if files else []

    def on_quick_clean(self, icon=None, item=None):
        """Melakukan pembersihan berkas standar secara in-place."""
        files = self._prompt_files()
        if not files:
            return

        success_count = 0
        for f in files:
            res = clean_file(f, inplace=True)
            if res.get("success"):
                success_count += 1

        msg = f"Berhasil membersihkan {success_count} dari {len(files)} berkas."
        MacShellIntegration.notify_user("Pembersihan Kilat Selesai", msg)

    def on_quick_clean_preset(self, preset_key: str):
        """Melakukan pembersihan berkas menggunakan profil preset."""
        files = self._prompt_files()
        if not files:
            return

        success_count = 0
        for f in files:
            res = PresetCleaner.clean_with_preset(f, preset_key, inplace=True)
            if res.get("success"):
                success_count += 1

        preset_title = preset_key.replace("_", " ").title()
        msg = f"Preset {preset_title}: {success_count} dari {len(files)} berkas berhasil dibersihkan."
        MacShellIntegration.notify_user("Pembersihan Preset Selesai", msg)

    def on_open_main_app(self, icon=None, item=None):
        """Meluncurkan jendela GUI utama MrClean."""
        # Menjalankan proses utama terpisah
        script_path = os.path.join(self.project_root, "src", "main.py")
        subprocess.Popen([sys.executable, script_path])

    def on_quit(self, icon=None, item=None):
        """Menghentikan menu bar app."""
        if self.icon:
            self.icon.stop()

    def run(self):
        """Menjalankan loop status item menu bar."""
        if self.icon:
            self.icon.run()

def run_menubar_app():
    """Fungsi runner untuk dipanggil via CLI / script."""
    app = MrCleanMenuBarApp()
    app.run()

if __name__ == "__main__":
    run_menubar_app()
