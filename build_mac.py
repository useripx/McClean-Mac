"""
MrClean Mac — Build & Packaging Script (.app & .dmg)

Fungsi:
1. Membangun bundel aplikasi macOS (dist/MrClean.app) menggunakan PyInstaller
   (mendukung arsitektur native Apple Silicon, Intel x86_64, atau Universal 2 Fat Binary).
2. Mengemas dist/MrClean.app menjadi installer Apple Disk Image (dist/MrClean-macOS.dmg)
   menggunakan create-dmg (tampilan visual drag-to-Applications) atau utilitas bawaan macOS (hdiutil).
"""
import os
import sys
import shutil
import argparse
import subprocess

def build_mac(universal=False, force_hdiutil=False):
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

    # Dukungan Universal 2 Fat Binary (arm64 + x86_64) jika diminta
    if universal and sys.platform == "darwin":
        cmd.append("--target-arch=universal2")
        print("[*] Mengaktifkan opsi Universal 2 Fat Binary (arm64 + x86_64)...")

    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")

    cmd.append("src/main.py")

    print(f"[*] Menjalankan perintah PyInstaller:")
    print("    " + " ".join(cmd))
    subprocess.run(cmd, check=True)

    app_path = os.path.join("dist", "MrClean.app")
    dmg_path = os.path.join("dist", "MrClean-macOS.dmg")

    # 2. Kemas menjadi berkas DMG di macOS
    if sys.platform == "darwin":
        if os.path.exists(app_path):
            if os.path.exists(dmg_path):
                os.remove(dmg_path)

            has_create_dmg = shutil.which("create-dmg") and not force_hdiutil

            if has_create_dmg:
                print("[*] Mengemas DMG menggunakan create-dmg (Stylized Drag-to-Applications)...")
                create_dmg_cmd = [
                    "create-dmg",
                    "--volname", "MrClean Installer",
                    "--window-pos", "200", "120",
                    "--window-size", "600", "400",
                    "--icon-size", "100",
                    "--icon", "MrClean.app", "160", "190",
                    "--hide-extension", "MrClean.app",
                    "--app-drop-link", "440", "190",
                    dmg_path,
                    app_path
                ]
                try:
                    subprocess.run(create_dmg_cmd, check=True)
                    print(f"[SUCCESS] Berkas Stylized DMG berhasil dibuat: {dmg_path}")
                except Exception as e:
                    print(f"[!] create-dmg gagal ({e}), beralih ke hdiutil standar...")
                    has_create_dmg = False

            if not has_create_dmg:
                print("[*] Mengemas MrClean.app ke berkas disk image (.dmg) via hdiutil...")
                dmg_cmd = [
                    "hdiutil", "create",
                    "-volname", "MrClean Installer",
                    "-srcfolder", app_path,
                    "-ov",
                    "-format", "UDZO",
                    dmg_path
                ]
                subprocess.run(dmg_cmd, check=True)
                print(f"[SUCCESS] Berkas installer macOS berhasil dibuat: {dmg_path}")
        else:
            print(f"[ERROR] Bundel aplikasi {app_path} tidak ditemukan!")
    else:
        print("[NOTE] Kompilasi PyInstaller selesai.")
        print("       (Pembuatan berkas .dmg via hdiutil/create-dmg memerlukan lingkungan macOS atau runner GitHub Actions).")

    print("=" * 60)
    print("[SUCCESS] PROSES BUILD SELESAI DENGAN SUKSES!")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MrClean Mac Build & Packaging Tool")
    parser.add_argument("--universal", action="store_true", help="Build Universal 2 binary (Apple Silicon + Intel)")
    parser.add_argument("--hdiutil-only", action="store_true", help="Gunakan hanya hdiutil bawaan tanpa create-dmg")
    args = parser.parse_args()

    build_mac(universal=args.universal, force_hdiutil=args.hdiutil_only)
