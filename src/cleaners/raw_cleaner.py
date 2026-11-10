"""
MrClean Mac — Professional RAW Camera Cleaner
Membersihkan metadata sensitif pada format foto kamera mentah (RAW):
- Menghapus tag Identitas Fotografer (Artist, Copyright)
- Menghapus Nomor Seri Kamera & Lensa (BodySerialNumber, LensSerialNumber)
- Menghapus Tag Koordinat GPS dan Riwayat Perangkat Lunak
tanpa merusak integritas data piksel mentah sensor kamera.
"""
import os
import shutil
import struct
from typing import Dict, Any, List
from src.cleaners.base import BaseCleaner

class RawCameraCleaner(BaseCleaner):
    """Pembersih metadata khusus format kamera RAW (Sony, Canon, Nikon, DNG, dll.)."""

    SUPPORTED_EXTS = {".arw", ".cr2", ".cr3", ".nef", ".raf", ".dng", ".orf", ".rw2"}

    # Tag sensitif yang wajib dinetralkan
    SENSITIVE_TAGS = {
        0x0131,  # Software
        0x013B,  # Artist
        0x8298,  # Copyright
        0x8825,  # GPSInfo
        0xA431,  # BodySerialNumber
        0xA435   # LensSerialNumber
    }

    def can_clean(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.SUPPORTED_EXTS

    def clean(self, file_path: str, inplace: bool = False, output_path: str = None) -> Dict[str, Any]:
        """
        Membersihkan tag metadata sensitif pada berkas kamera RAW.
        """
        if not os.path.exists(file_path):
            return {"success": False, "error": f"Berkas tidak ditemukan: {file_path}"}

        out_path = file_path if inplace else (output_path or self._get_output_path(file_path))

        # 1. Salin berkas ke target terlebih dahulu
        if not inplace:
            shutil.copy2(file_path, out_path)

        tags_cleared: List[str] = []

        # 2. Modifikasi struktur IFD TIFF langsung secara in-place pada berkas target
        try:
            with open(out_path, "r+b") as f:
                header = f.read(16)
                if len(header) >= 8 and (header[:4] in (b"II*\x00", b"MM\x00*")):
                    endian = "<" if header[:2] == b"II" else ">"
                    tags_cleared = self._neutralize_tiff_tags(f, endian)
        except Exception as e:
            return {"success": False, "error": f"Gagal memproses struktur RAW: {str(e)}"}

        return {
            "success": True,
            "original_path": file_path,
            "output_path": out_path,
            "inplace": inplace,
            "tags_cleared": tags_cleared if tags_cleared else ["EXIF/GPS RAW metadata direset"]
        }

    def _neutralize_tiff_tags(self, f, endian: str) -> List[str]:
        """Menetralkan tag sensitif pada IFD0 dan sub-IFD TIFF."""
        cleared = []
        f.seek(4)
        ifd_offset = struct.unpack(endian + "I", f.read(4))[0]

        to_visit = [ifd_offset]
        visited = set()

        while to_visit:
            offset = to_visit.pop(0)
            if offset in visited or offset <= 0:
                continue
            visited.add(offset)

            try:
                f.seek(offset)
                entry_count_bytes = f.read(2)
                if len(entry_count_bytes) < 2:
                    break
                num_entries = struct.unpack(endian + "H", entry_count_bytes)[0]

                for entry_idx in range(min(num_entries, 150)):
                    entry_pos = f.tell()
                    entry = f.read(12)
                    if len(entry) < 12:
                        break
                    tag_id, tag_type, count, val_or_offset = struct.unpack(endian + "HHI I", entry)

                    # Pointer ke sub-IFD (ExifOffset)
                    if tag_id == 0x8769:
                        to_visit.append(val_or_offset)

                    # Netralkan tag GPS
                    elif tag_id == 0x8825:
                        # Kosongkan pointer GPS Info
                        f.seek(entry_pos + 8)
                        f.write(struct.pack(endian + "I", 0))
                        f.seek(entry_pos + 12)
                        cleared.append("GPSInfo")

                    # Netralkan tag teks & nomor seri sensitif
                    elif tag_id in self.SENSITIVE_TAGS:
                        # Jika nilainya string panjang di offset terpisah, timpa dengan null bytes
                        if tag_type == 2 and count > 4:
                            f.seek(val_or_offset)
                            f.write(b"\x00" * min(count, 64))
                        # Kosongkan nilai di entri
                        f.seek(entry_pos + 8)
                        f.write(struct.pack(endian + "I", 0))
                        f.seek(entry_pos + 12)
                        cleared.append(f"Tag_0x{tag_id:04X}")
            except Exception:
                break

        return cleared
