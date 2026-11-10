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

def sync_to_main():
    print("[*] MEMULAI SINKRONISASI FILTERED RELEASE KE BRANCH 'main'...")
    
    # 1. Pastikan repo bersih
    status = run_cmd(["git", "status", "--porcelain"])
    if status:
        print("[!] Workspace belum bersih. Commit atau stash perubahan terlebih dahulu.")
        sys.exit(1)
        
    current_branch = run_cmd(["git", "branch", "--show-current"])
    print(f"[*] Branch saat ini: {current_branch}")
    
    # 2. Checkout atau buat branch main
    branches = run_cmd(["git", "branch", "--list", "main"])
    if not branches:
        run_cmd(["git", "checkout", "-b", "main"])
    else:
        run_cmd(["git", "checkout", "main"])
        
    # 3. Merge isi develop
    print("[*] Menggabungkan perubahan dari develop...")
    run_cmd(["git", "merge", current_branch, "--no-commit", "--no-ff"], check=False)
    
    # 4. Hapus folder catatan pengembang dari staging area main
    print("[*] Menyaring dan membuang folder catatan internal dari branch main...")
    for item in EXCLUDED_PATHS:
        if os.path.exists(item):
            run_cmd(["git", "rm", "-rf", "--cached", item], check=False)
            print(f"    - Excluded: {item}")
            
    print("[SUCCESS] Branch main siap di-commit secara bersih untuk rilis produksi.")

if __name__ == "__main__":
    sync_to_main()
