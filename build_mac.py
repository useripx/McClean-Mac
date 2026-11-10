"""
MrClean Mac — Build & Packaging Script (.app & .dmg)

Fungsi:
1. Membangun bundel aplikasi macOS (dist/MrClean.app) menggunakan PyInstaller.
2. Mengemas dist/MrClean.app menjadi installer Apple Disk Image (dist/MrClean-macOS.dmg)
   menggunakan utilitas bawaan macOS (hdiutil).
"""
import os
import sys
import shutil
import subprocess

def build_mac():
    print("=" * 60)
    print("[*] MEMULAI KOMPILASI MRCLEAN UNTUK MACOS...")
    print("=" * 60)

    # Pastikan ikon resmi macOS tersedia
    icon_path = "assets/icon.icns"
    if not os.path.exists(icon_path):
        print(f"[*] Ikon {icon_path} belum ditemukan, mencoba membuat dari aset...")
        try:
            from src.utils.icon_converter import convert_logo_to_assets
            convert_logo_to_assets()
        except Exception as e:
            print(f"[!] Warning: Gagal membuat icon otomatis: {e}")

    # Separator untuk --add-data (Windows ';' vs Unix ':')
    sep = ";" if sys.platform == "win32" else ":"
    add_data_arg = f"assets{sep}assets"

    # 1. Jalankan PyInstaller untuk membuat .app bundle
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--windowed",
        "--onedir",
        "--name=MrClean",
        f"--add-data={add_data_arg}",
        "--collect-all=customtkinter",
        "--collect-all=reportlab",
        "--clean",
        "-y"
    ]

    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")

    cmd.append("src/main.py")

    print(f"[*] Menjalankan perintah PyInstaller:")
    print("    " + " ".join(cmd))
    subprocess.run(cmd, check=True)

    app_path = os.path.join("dist", "MrClean.app")
    dmg_path = os.path.join("dist", "MrClean-macOS.dmg")

    # 2. Kemas menjadi berkas DMG menggunakan utilitas native macOS (hdiutil)
    if sys.platform == "darwin":
        if os.path.exists(app_path):
            print("[*] Mengemas MrClean.app ke berkas disk image (.dmg)...")
            if os.path.exists(dmg_path):
                os.remove(dmg_path)

            dmg_cmd = [
                "hdiutil", "create",
                "-volname", "MrClean Installer",
                "-srcfolder", app_path,
                "-ov",
                "-format", "UDZO",
                dmg_path
            ]
            print(f"[*] Menjalankan hdiutil: {' '.join(dmg_cmd)}")
            subprocess.run(dmg_cmd, check=True)
            print(f"[SUCCESS] Berkas installer macOS berhasil dibuat: {dmg_path}")
        else:
            print(f"[ERROR] Bundel aplikasi {app_path} tidak ditemukan!")
    else:
        print("[NOTE] Kompilasi PyInstaller selesai.")
        print("       (Pembuatan berkas .dmg via hdiutil memerlukan lingkungan macOS atau runner GitHub Actions).")

    print("=" * 60)
    print("[SUCCESS] PROSES BUILD SELESAI DENGAN SUKSES!")
    print("=" * 60)

if __name__ == "__main__":
    build_mac()
