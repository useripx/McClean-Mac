"""
tools/sync_to_main.py — Skrip Sinkronisasi Rilis Bersih ke Branch main

Fungsi:
Menjaga kepatuhan Pilar 2 (Clean main):
Branch 'main' adalah mahkota produksi yang hanya memuat kode runtime:
(src/, assets/, requirements.txt, README.md, LICENSE, build_mac.py, .github/, .gitignore)
dan MENYARING KELUAR folder/catatan internal pengembang:
(Docs/, changelog/, aturan/, AGENTS.md, GEMINI.md).
"""

import os
import subprocess
import sys
import shutil

EXCLUDED_PATHS = [
    "Docs",
    "changelog",
    "aturan",
    "AGENTS.md",
    "GEMINI.md"
]

def run_cmd(cmd, check=True):
    print(f"[CMD] {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 and check:
        print(f"[ERROR] {res.stderr}")
        sys.exit(res.returncode)
    return res.stdout.strip()

def sync_to_main(push_to_remote=True):
    print("=" * 60)
    print("[*] MEMULAI SINKRONISASI FILTERED RELEASE KE BRANCH 'main'...")
    print("=" * 60)
    
    # 1. Pastikan repo bersih
    status = run_cmd(["git", "status", "--porcelain"])
    if status:
        print("[!] Workspace belum bersih. Commit atau stash perubahan terlebih dahulu.")
        sys.exit(1)
        
    current_branch = run_cmd(["git", "branch", "--show-current"])
    print(f"[*] Branch sumber: {current_branch}")
    
    # 2. Cek apakah branch main sudah ada
    branches = run_cmd(["git", "branch", "--list", "main"])
    if not branches:
        print("[*] Membuat branch 'main' baru dari branch saat ini...")
        run_cmd(["git", "checkout", "-b", "main"])
    else:
        print("[*] Berpindah ke branch 'main'...")
        run_cmd(["git", "checkout", "main"])
        print("[*] Menggabungkan perubahan terbaru dari develop...")
        run_cmd(["git", "merge", current_branch, "--no-commit", "--no-ff"], check=False)
        
    # 3. Hapus folder catatan pengembang dari branch main
    print("[*] Menyaring dan membuang folder catatan internal dari branch main...")
    for item in EXCLUDED_PATHS:
        if os.path.exists(item):
            run_cmd(["git", "rm", "-rf", item], check=False)
            if os.path.exists(item):
                if os.path.isdir(item):
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    os.remove(item)
            print(f"    - Berhasil disaring: {item}")
            
    # 4. Buat commit rilis produksi bersih
    diff_staged = run_cmd(["git", "diff", "--cached", "--name-only"])
    if diff_staged:
        print("[*] Melakukan commit rilis produksi di branch main...")
        run_cmd(["git", "commit", "-m", "release: v1.0.0-macos clean production runtime"])
    else:
        print("[*] Tidak ada perubahan baru untuk di-commit di branch main.")
        
    # 5. Push ke remote origin main jika diminta
    if push_to_remote:
        print("[*] Melakukan push branch main ke remote origin...")
        run_cmd(["git", "push", "-u", "origin", "main"])
        print("[SUCCESS] Branch main berhasil di-push ke remote origin!")
        
    # 6. Kembali ke branch kerja develop
    print(f"[*] Mengembalikan posisi branch kerja ke '{current_branch}'...")
    run_cmd(["git", "checkout", current_branch])
    
    print("=" * 60)
    print("[SUCCESS] SINKRONISASI SELESAI. BRANCH MAIN 100% BERSIH!")
    print(f"          Posisi aktif saat ini kembali di branch '{current_branch}'.")
    print("=" * 60)

if __name__ == "__main__":
    sync_to_main()
