"""
MrClean Mac — macOS Shell & Finder Integration
Mengelola integrasi native macOS:
1. macOS Finder Quick Action / Service (~/Library/Services/Bersihkan Metadata dengan MrClean.workflow)
2. Notifikasi desktop native macOS via osascript.
"""
import os
import sys
import shutil
import subprocess
from typing import Tuple, List

class MacShellIntegration:
    """Pengelola integrasi sistem operasi native macOS (Finder Quick Actions & Notifikasi)."""

    SERVICE_NAME = "Bersihkan Metadata dengan MrClean.workflow"
    SERVICES_DIR = os.path.expanduser("~/Library/Services")
    APP_NAME = "MrClean"

    @classmethod
    def get_service_path(cls) -> str:
        """Mengembalikan path lengkap ke folder Quick Action workflow."""
        return os.path.join(cls.SERVICES_DIR, cls.SERVICE_NAME)

    @classmethod
    def get_executable_or_command(cls) -> str:
        """Menentukan perintah eksekusi MrClean di macOS."""
        if getattr(sys, 'frozen', False):
            # Bundel biner .app di macOS (/Applications/MrClean.app/Contents/MacOS/MrClean)
            return sys.executable
        else:
            main_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
            return f'"{sys.executable}" "{main_script}"'

    @classmethod
    def is_installed(cls) -> bool:
        """Mengecek apakah Quick Action sudah terpasang di ~/Library/Services/."""
        return os.path.exists(cls.get_service_path())

    @classmethod
    def install(cls) -> Tuple[bool, str]:
        """
        Memasang Finder Quick Action (.workflow) ke direktori ~/Library/Services/.
        """
        service_path = cls.get_service_path()
        try:
            os.makedirs(service_path, exist_ok=True)
            contents_dir = os.path.join(service_path, "Contents")
            os.makedirs(contents_dir, exist_ok=True)

            cmd = cls.get_executable_or_command()

            # 1. Info.plist untuk Workflow
            info_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSServices</key>
    <array>
        <dict>
            <key>NSMenuItem</key>
            <dict>
                <key>default</key>
                <string>Bersihkan Metadata dengan MrClean</string>
            </dict>
            <key>NSMessage</key>
            <string>runWorkflowAsService</string>
            <key>NSRequiredContext</key>
            <dict>
                <key>NSApplicationIdentifier</key>
                <string>com.apple.finder</string>
            </dict>
            <key>NSSendFileTypes</key>
            <array>
                <string>public.item</string>
            </array>
        </dict>
    </array>
</dict>
</plist>"""
            with open(os.path.join(contents_dir, "Info.plist"), "w", encoding="utf-8") as f:
                f.write(info_plist)

            # 2. Skrip Runner Automator (document.wflow)
            wflow = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>AMApplicationBuild</key>
    <string>523</string>
    <key>AMApplicationVersion</key>
    <string>2.10</string>
    <key>AMDocumentVersion</key>
    <string>2</string>
    <key>actions</key>
    <array>
        <dict>
            <key>action</key>
            <dict>
                <key>COMMAND_STRING</key>
                <string>for f in "$@"; do {cmd} "$f"; done</string>
            </dict>
        </dict>
    </array>
</dict>
</plist>"""
            with open(os.path.join(contents_dir, "document.wflow"), "w", encoding="utf-8") as f:
                f.write(wflow)

            return True, f"Quick Action Finder berhasil dipasang ke {service_path}"
        except Exception as e:
            return False, f"Gagal memasang Finder Quick Action: {str(e)}"

    @classmethod
    def uninstall(cls) -> Tuple[bool, str]:
        """Menghapus Finder Quick Action dari ~/Library/Services/."""
        service_path = cls.get_service_path()
        if not os.path.exists(service_path):
            return True, "Quick Action Finder belum terpasang."

        try:
            shutil.rmtree(service_path)
            return True, "Quick Action Finder berhasil dicopot."
        except Exception as e:
            return False, f"Gagal mencopot Finder Quick Action: {str(e)}"

    @classmethod
    def notify_user(cls, title: str, message: str, sound: str = "Glass") -> bool:
        """
        Mengirimkan notifikasi banner sistem native macOS menggunakan osascript.
        """
        if sys.platform != "darwin":
            # Di luar macOS (misal saat running di Windows atau Linux CI), fallback silent success
            return True

        safe_title = title.replace('"', '\\"')
        safe_message = message.replace('"', '\\"')
        script = f'display notification "{safe_message}" with title "{safe_title}" sound name "{sound}"'
        try:
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            return res.returncode == 0
        except Exception:
            return False
