"""
tools/create_release.py — Otomatisasi Pembuatan Rilis & Tagging Git (MrClean Mac)

Fungsi:
1. Memvalidasi format tag Semantic Versioning (misal: v1.1.0).
2. Memverifikasi seluruh unit tests lulus 100% PASS sebelum rilis diizinkan.
3. Menjalankan sinkronisasi filtered release ke branch 'main' (Pilar 2).
4. Membuat Git annotated tag dan melakukan push ke remote origin (memicu GitHub Actions CI/CD).
"""
import os
import sys
import re
import subprocess
import argparse

# Pastikan root direktori proyek terdaftar dalam sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SEMVER_PATTERN = re.compile(r"^v\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$")

def validate_tag(tag: str) -> bool:
    """Memvalidasi apakah string tag memenuhi format semver (contoh: v1.1.0 atau v1.0.0-macos)."""
    return bool(SEMVER_PATTERN.match(tag))

def run_cmd(cmd, check=True):
    print(f"[CMD] {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 and check:
        print(f"[ERROR] {res.stderr}")
        sys.exit(res.returncode)
    return res.stdout.strip()

def create_release(tag: str, message: str = "", push: bool = True, skip_tests: bool = False):
    print("=" * 60)
    print(f"[*] MEMULAI PROSES RILIS RESMI: {tag}")
    print("=" * 60)

    # 1. Validasi Tag
    if not validate_tag(tag):
        print(f"[ERROR] Format tag '{tag}' tidak valid! Gunakan format SemVer seperti 'v1.1.0' atau 'v1.0.0-macos'.")
        sys.exit(1)

    # 2. Pastikan repo bersih
    status = run_cmd(["git", "status", "--porcelain"])
    if status:
        print("[!] Workspace belum bersih. Harap commit atau simpan perubahan terlebih dahulu.")
        sys.exit(1)

    # 3. Jalankan Pengujian Otomatis (Testing Gate)
    if not skip_tests:
        print("[*] Menjalankan test suite otomatis sebelum rilis...")
        test_res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])
        if test_res.returncode != 0:
            print("[ERROR] Rilis DIBATALKAN: Pengujian unit tidak mencapai 100% PASS!")
            sys.exit(1)
        print("[SUCCESS] Seluruh unit tests lulus 100% PASS!")

    current_branch = run_cmd(["git", "branch", "--show-current"])

    # 4. Sinkronisasi rilis ke branch main via tools/sync_to_main.py
    print("[*] Menjalankan sinkronisasi filtered release ke branch 'main'...")
    from tools.sync_to_main import sync_to_main
    sync_to_main(push_to_remote=False)

    # 5. Berpindah ke main untuk tagging
    run_cmd(["git", "checkout", "main"])

    tag_msg = message if message else f"Release {tag} - MrClean Mac"
    print(f"[*] Membuat tag git: {tag}...")
    run_cmd(["git", "tag", "-a", tag, "-m", tag_msg])

    # 6. Push ke remote jika diminta
    if push:
        print("[*] Melakukan push branch main dan tag ke origin...")
        run_cmd(["git", "push", "origin", "main"])
        run_cmd(["git", "push", "origin", tag])
        print(f"[SUCCESS] Tag {tag} dan branch main berhasil di-push ke GitHub!")

    # 7. Kembali ke branch pengembang
    run_cmd(["git", "checkout", current_branch])

    print("=" * 60)
    print(f"[SUCCESS] RILIS {tag} BERHASIL DIPROSES!")
    print(f"          GitHub Actions akan otomatis membangun biner DMG di cloud.")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MrClean Mac Release Tool")
    parser.add_argument("tag", help="Tag versi rilis (contoh: v1.1.0)")
    parser.add_argument("-m", "--message", default="", help="Pesan rilis")
    parser.add_argument("--no-push", action="store_true", help="Jangan push ke remote")
    parser.add_argument("--skip-tests", action="store_true", help="Lewati tahapan pengujian unit")
    args = parser.parse_args()

    create_release(tag=args.tag, message=args.message, push=not args.no_push, skip_tests=args.skip_tests)
