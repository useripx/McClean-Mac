#!/usr/bin/env bash
# ==============================================================================
# integrations/shortcuts/clean_file.sh — Skrip Shell Pendukung Apple Shortcuts
# ==============================================================================
# Skrip ini digunakan di dalam aksi "Run Shell Script" pada aplikasi Shortcuts
# (Pintasan) di macOS.
#
# Penggunaan:
#   clean_file.sh [preset] [file_path_1] [file_path_2] ...
#
# Preset yang didukung:
#   - dev (samarkan path lokal)
#   - social (hapus EXIF & GPS)
#   - academic (hapus Author dokumen)
#   - none (pembersihan lossless umum)
# ==============================================================================

set -e

PRESET="${1:-none}"
shift 1 || true

# 1. Cari binary eksekusi MrClean
if [ -f "/Applications/MrClean.app/Contents/MacOS/MrClean" ]; then
    MRCLEAN_BIN="/Applications/MrClean.app/Contents/MacOS/MrClean"
elif command -v mrclean >/dev/null 2>&1; then
    MRCLEAN_BIN="$(command -v mrclean)"
elif command -v python3 >/dev/null 2>&1; then
    MRCLEAN_BIN="python3 -m src.cli"
else
    osascript -e 'display notification "Python 3 atau MrClean.app tidak ditemukan!" with title "MrClean Error"'
    exit 1
fi

SUCCESS_COUNT=0
TOTAL_COUNT=0

for TARGET in "$@"; do
    if [ ! -e "$TARGET" ]; then
        continue
    fi
    TOTAL_COUNT=$((TOTAL_COUNT + 1))

    if [ "$PRESET" = "none" ]; then
        $MRCLEAN_BIN clean "$TARGET" --inplace
    else
        $MRCLEAN_BIN clean "$TARGET" --preset "$PRESET" --inplace
    fi

    if [ $? -eq 0 ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    fi
done

# Kirim banner notifikasi desktop macOS
if [ $SUCCESS_COUNT -gt 0 ]; then
    osascript -e "display notification \"Berhasil membersihkan $SUCCESS_COUNT dari $TOTAL_COUNT berkas secara aman.\" with title \"MrClean Mac\" sound name \"Glass\""
else
    osascript -e "display notification \"Pembersihan berkas gagal atau format tidak didukung.\" with title \"MrClean Peringatan\" sound name \"Basso\""
fi

exit 0
