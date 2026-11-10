"""
src/cli.py — MrClean Mac Headless CLI Interface (v2.0.0-macos)

Memungkinkan pengoperasian inspeksi, pembersihan metadata, penerapan preset,
dan spoofing melalui terminal/baris perintah tanpa memicu antarmuka GUI.
Mendukung piping JSON, skrip shell, dan integrasi Apple Shortcuts.

100% Offline & Zero-Telemetry.
"""
import sys
import os
import json
import argparse
from typing import List, Dict, Any, Optional

from src.inspectors import inspect_file
from src.cleaners import clean_file
from src.cleaners.preset_cleaner import PresetCleaner
from src.editors.spoofing import MetadataSpoofer
from src.utils.scanner import scan_folder

VERSION = "2.0.0-macos"

def _normalize_preset_key(preset: Optional[str]) -> Optional[str]:
    if not preset:
        return None
    p = preset.lower().strip()
    if p in ("dev", "developer"):
        return "developer"
    elif p in ("social", "social_media"):
        return "social_media"
    elif p in ("academic", "akad"):
        return "academic"
    return p

def handle_inspect(args: argparse.Namespace) -> int:
    """Menangani perintah inspeksi berkas atau direktori."""
    target = args.target
    if not os.path.exists(target):
        print(f"[ERROR] Target path tidak ditemukan: {target}", file=sys.stderr)
        return 1

    files_to_inspect = []
    if os.path.isdir(target):
        files_to_inspect = scan_folder(target, recursive=args.recursive)
    else:
        files_to_inspect = [target]

    if not files_to_inspect:
        print(f"[!] Tidak ada berkas yang dapat diinspeksi pada: {target}")
        return 0

    results = []
    for f in files_to_inspect:
        res = inspect_file(f)
        results.append(res)

    if args.json:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2, ensure_ascii=False))
        return 0

    # Format Teks Konsol
    print("=" * 65)
    print(f"[*] HASIL INSPEKSI METADATA ({len(results)} berkas)")
    print("=" * 65)
    for r in results:
        fname = os.path.basename(r.get("file_path", ""))
        category = r.get("category", "unknown")
        has_meta = "YA" if r.get("has_metadata") else "TIDAK"
        risk_score = r.get("privacy_risk_score", 0)
        risk_level = r.get("privacy_risk_level", "AMAN")
        ai_stego = "TERDETEKSI" if r.get("has_ai_watermark") else "BERSIH"

        print(f"Berkas      : {fname}")
        print(f"Kategori    : {category.upper()}")
        print(f"Ada Metadata: {has_meta} ({r.get('metadata_count', 0)} entri)")
        print(f"Skor Risiko : {risk_score}% [{risk_level}]")
        print(f"AI Stego    : {ai_stego}")

        details = r.get("categories", {})
        for cat_name, entries in details.items():
            if isinstance(entries, dict) and entries:
                print(f"  [{cat_name}]")
                for k, v in list(entries.items())[:5]:
                    print(f"    - {k}: {v}")
                if len(entries) > 5:
                    print(f"    ... dan {len(entries) - 5} entri lainnya")
        print("-" * 65)

    return 0

def handle_clean(args: argparse.Namespace) -> int:
    """Menangani pembersihan metadata berkas atau direktori."""
    target = args.target
    if not os.path.exists(target):
        print(f"[ERROR] Target path tidak ditemukan: {target}", file=sys.stderr)
        return 1

    files_to_clean = []
    if os.path.isdir(target):
        files_to_clean = scan_folder(target, recursive=args.recursive)
    else:
        files_to_clean = [target]

    if not files_to_clean:
        print(f"[!] Tidak ada berkas yang dapat dibersihkan pada: {target}")
        return 0

    preset_key = _normalize_preset_key(args.preset)
    success_count = 0
    fail_count = 0
    results = []

    for f in files_to_clean:
        if preset_key:
            res = PresetCleaner.clean_with_preset(f, preset_key, inplace=args.inplace)
        else:
            output_path = None
            if args.output and not args.inplace:
                if os.path.isdir(args.output):
                    fname = os.path.basename(f)
                    output_path = os.path.join(args.output, fname)
                else:
                    output_path = args.output
            res = clean_file(f, output_path=output_path, inplace=args.inplace)

        results.append(res)
        if res.get("success"):
            success_count += 1
        else:
            fail_count += 1

    if args.json:
        print(json.dumps({
            "total": len(files_to_clean),
            "success_count": success_count,
            "fail_count": fail_count,
            "results": results
        }, indent=2, ensure_ascii=False))
        return 0 if fail_count == 0 else 1

    print("=" * 65)
    print(f"[*] HASIL PEMBERSIHAN METADATA ({len(files_to_clean)} berkas)")
    if preset_key:
        print(f"[*] Preset Aktif: {preset_key.upper()}")
    print("=" * 65)
    for r in results:
        in_path = r.get("input_path", "")
        fname = os.path.basename(in_path) if in_path else "Unknown"
        if r.get("success"):
            out = r.get("output_path", in_path)
            print(f"[SUKSES] {fname} ➜ {out}")
        else:
            err = r.get("error", "Format tidak didukung")
            print(f"[GAGAL]  {fname}: {err}")
    print("-" * 65)
    print(f"Total: {len(files_to_clean)} | Sukses: {success_count} | Gagal: {fail_count}")

    return 0 if fail_count == 0 else 1

def handle_spoof(args: argparse.Namespace) -> int:
    """Menangani penyuntikan metadata sintetis (spoofing)."""
    target = args.target
    if not os.path.exists(target):
        print(f"[ERROR] Target path tidak ditemukan: {target}", file=sys.stderr)
        return 1

    profile = args.profile.lower() if args.profile else "random"
    res = MetadataSpoofer.spoof(target, profile_name=profile, inplace=args.inplace)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res.get("success") else 1

    if res.get("success"):
        print(f"[SUKSES] Metadata palsu berhasil disuntikkan!")
        print(f"Berkas : {res.get('output_path')}")
        print(f"Profil : {res.get('profile', profile).upper()}")
        return 0
    else:
        print(f"[GAGAL] {res.get('error')}", file=sys.stderr)
        return 1

def build_parser() -> argparse.ArgumentParser:
    """Membangun parser argumen CLI MrClean."""
    parser = argparse.ArgumentParser(
        prog="mrclean",
        description="MrClean Mac — Offline Metadata Inspector, Cleaner & Anonymizer"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"MrClean Mac v{VERSION}"
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Perintah yang tersedia")

    # 1. inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspeksi metadata dan risiko privasi berkas")
    p_inspect.add_argument("target", help="Path berkas atau direktori yang akan diinspeksi")
    p_inspect.add_argument("--json", action="store_true", help="Keluarkan hasil dalam format JSON terstruktur")
    p_inspect.add_argument("-r", "--recursive", action="store_true", help="Pindai sub-direktori secara rekursif")
    p_inspect.set_defaults(func=handle_inspect)

    # 2. clean
    p_clean = subparsers.add_parser("clean", help="Bersihkan metadata sensitif dari berkas")
    p_clean.add_argument("target", help="Path berkas atau direktori yang akan dibersihkan")
    p_clean.add_argument(
        "--preset",
        choices=["dev", "developer", "social", "social_media", "academic"],
        help="Gunakan preset pembersihan cepat (dev, social, academic)"
    )
    p_clean.add_argument("--inplace", action="store_true", help="Timpa berkas asli secara langsung")
    p_clean.add_argument("-o", "--output", help="Folder tujuan atau path berkas keluaran")
    p_clean.add_argument("-r", "--recursive", action="store_true", help="Bersihkan berkas dalam sub-direktori secara rekursif")
    p_clean.add_argument("--json", action="store_true", help="Keluarkan ringkasan hasil dalam format JSON")
    p_clean.set_defaults(func=handle_clean)

    # 3. spoof
    p_spoof = subparsers.add_parser("spoof", help="Suntikkan metadata sintetis (Canon/Nikon/Sony) pada gambar")
    p_spoof.add_argument("target", help="Path berkas gambar yang akan disamarkan")
    p_spoof.add_argument(
        "--profile",
        choices=["canon", "nikon", "sony", "random"],
        default="random",
        help="Pilihan profil kamera sintetis (default: random)"
    )
    p_spoof.add_argument("--inplace", action="store_true", help="Timpa berkas asli secara langsung")
    p_spoof.add_argument("--json", action="store_true", help="Keluarkan ringkasan hasil dalam format JSON")
    p_spoof.set_defaults(func=handle_spoof)

    return parser

def main(argv: Optional[List[str]] = None) -> int:
    """Fungsi utama CLI entry point."""
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        parser.print_help()
        return 0

    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        return args.func(args)

    parser.print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main())
