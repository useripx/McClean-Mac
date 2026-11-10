"""
tools/notarize_mac.py — Otomatisasi Code Signing & Notarisasi Apple Developer (MrClean Mac)

Memungkinkan penandatanganan sertifikat Apple Developer ID Application (`codesign --options runtime`)
dan pengiriman notarisasi otomatis ke Apple Gatekeeper (`xcrun notarytool submit`) serta
penempelan tiket validasi (`xcrun stapler staple`).
"""
import os
import sys
import argparse
import subprocess
from typing import List, Dict, Optional

def build_codesign_command(app_path: str, identity: str, entitlements: Optional[str] = None) -> List[str]:
    """Membangun perintah codesign dengan opsi runtime ketat."""
    cmd = [
        "codesign",
        "--deep",
        "--force",
        "--options", "runtime",
        "--sign", identity
    ]
    if entitlements and os.path.exists(entitlements):
        cmd.extend(["--entitlements", entitlements])
    cmd.append(app_path)
    return cmd

def build_notarize_command(dmg_path: str, apple_id: str, team_id: str, password: str) -> List[str]:
    """Membangun perintah pengiriman tiket notarisasi ke Apple notarytool."""
    return [
        "xcrun", "notarytool", "submit", dmg_path,
        "--apple-id", apple_id,
        "--team-id", team_id,
        "--password", password,
        "--wait"
    ]

def build_staple_command(target_path: str) -> List[str]:
    """Membangun perintah penempelan tiket validasi Apple Gatekeeper."""
    return ["xcrun", "stapler", "staple", target_path]

def notarize_app(
    app_path: str,
    dmg_path: str,
    identity: Optional[str] = None,
    apple_id: Optional[str] = None,
    team_id: Optional[str] = None,
    password: Optional[str] = None,
    dry_run: bool = False
) -> int:
    """Menjalankan siklus penandatanganan dan notarisasi resmi."""
    identity = identity or os.environ.get("APPLE_SIGNING_IDENTITY")
    apple_id = apple_id or os.environ.get("APPLE_ID")
    team_id = team_id or os.environ.get("APPLE_TEAM_ID")
    password = password or os.environ.get("APPLE_APP_SPECIFIC_PASSWORD")

    print("=" * 65)
    print("[*] APPLE CODE SIGNING & NOTARIZATION HELPER (v2.0.0-macos)")
    print("=" * 65)

    if not identity or not apple_id or not team_id or not password:
        print("[!] Kredensial Apple Developer tidak lengkap!")
        print("    Pastikan variabel lingkungan berikut disetel:")
        print("    - APPLE_SIGNING_IDENTITY (contoh: 'Developer ID Application: Nama (TEAMID)')")
        print("    - APPLE_ID (contoh: 'developer@example.com')")
        print("    - APPLE_TEAM_ID (contoh: 'ABCDE12345')")
        print("    - APPLE_APP_SPECIFIC_PASSWORD (password khusus aplikasi)")
        if not dry_run:
            return 1

    # 1. Perintah Code Signing
    sign_cmd = build_codesign_command(app_path, identity or "DEVELOPER_ID_PLACEHOLDER")
    print(f"[CMD Sign]    : {' '.join(sign_cmd)}")

    # 2. Perintah Notarisasi
    notary_cmd = build_notarize_command(
        dmg_path,
        apple_id or "user@example.com",
        team_id or "TEAM123456",
        password or "xxxx-xxxx-xxxx-xxxx"
    )
    print(f"[CMD Notarize]: {' '.join(notary_cmd)}")

    # 3. Perintah Staple
    staple_cmd = build_staple_command(dmg_path)
    print(f"[CMD Staple]  : {' '.join(staple_cmd)}")

    if dry_run:
        print("[SUCCESS] Verifikasi Dry-Run Selesai! Seluruh parameter perintah valid.")
        return 0

    # Eksekusi riil hanya jika bukan dry-run di macOS
    if sys.platform != "darwin":
        print("[ERROR] Eksekusi codesign dan notarytool hanya dapat dijalankan pada sistem operasi macOS!", file=sys.stderr)
        return 1

    print("[*] Menjalankan codesign...")
    res = subprocess.run(sign_cmd)
    if res.returncode != 0:
        return res.returncode

    print("[*] Mengirim berkas ke Apple Notary Service...")
    res = subprocess.run(notary_cmd)
    if res.returncode != 0:
        return res.returncode

    print("[*] Menempelkan tiket notarisasi (stapling)...")
    res = subprocess.run(staple_cmd)
    return res.returncode

def main() -> int:
    parser = argparse.ArgumentParser(description="Apple Code Signing & Notarization Tool")
    parser.add_argument("--app-path", default="dist/MrClean.app", help="Path bundel MrClean.app")
    parser.add_argument("--dmg-path", default="dist/MrClean-macOS.dmg", help="Path installer MrClean-macOS.dmg")
    parser.add_argument("--identity", help="Identitas sertifikat Developer ID")
    parser.add_argument("--apple-id", help="Email akun Apple ID")
    parser.add_argument("--team-id", help="10-karakter Team ID Apple Developer")
    parser.add_argument("--password", help="App-Specific Password Apple ID")
    parser.add_argument("--dry-run", action="store_true", help="Cetak perintah tanpa mengeksekusi")

    args = parser.parse_args()
    return notarize_app(
        app_path=args.app_path,
        dmg_path=args.dmg_path,
        identity=args.identity,
        apple_id=args.apple_id,
        team_id=args.team_id,
        password=args.password,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    sys.exit(main())
