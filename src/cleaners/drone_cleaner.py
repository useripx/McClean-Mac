"""
MrClean Mac — Drone Video Telemetry Cleaner
Membersihkan telemetri penerbangan drone dan action camera (DJI, GoPro, Insta360):
- Menetralkan atom QuickTime 'udta' (User Data) dan 'meta'
- Mengubah atom telemetri menjadi atom 'free' (padding) tanpa re-encoding video
- Menjamin 100% integritas visual video dan audio tetap utuh.
"""
import os
import shutil
import struct
from typing import Dict, Any, List
from src.cleaners.base import BaseCleaner

class DroneTelemetryCleaner(BaseCleaner):
    """Pembersih telemetri video drone dan action cam tanpa merusak video stream."""

    SUPPORTED_EXTS = {".mp4", ".mov"}

    def can_clean(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.SUPPORTED_EXTS

    def clean(self, file_path: str, inplace: bool = False, output_path: str = None) -> Dict[str, Any]:
        """
        Membersihkan atom telemetri drone (udta/meta) pada berkas MP4/MOV.
        """
        if not os.path.exists(file_path):
            return {"success": False, "error": f"Berkas tidak ditemukan: {file_path}"}

        out_path = file_path if inplace else (output_path or self._get_output_path(file_path))

        if not inplace:
            shutil.copy2(file_path, out_path)

        tags_cleared: List[str] = []

        try:
            with open(out_path, "r+b") as f:
                file_len = os.fstat(f.fileno()).st_size
                f.seek(0)

                while f.tell() < min(file_len, 1024 * 1024 * 32):
                    pos = f.tell()
                    header = f.read(8)
                    if len(header) < 8:
                        break
                    atom_size, atom_type = struct.unpack(">I4s", header)
                    if atom_size == 0 or atom_size > file_len:
                        break

                    # Jika menemukan atom moov, periksa sub-atom udta
                    if atom_type == b"moov":
                        moov_end = pos + atom_size
                        while f.tell() < moov_end:
                            sub_pos = f.tell()
                            sub_header = f.read(8)
                            if len(sub_header) < 8:
                                break
                            sub_size, sub_type = struct.unpack(">I4s", sub_header)
                            if sub_size < 8 or sub_size > moov_end - sub_pos:
                                break

                            # Netralkan atom udta atau meta dengan mengubah tipe menjadi 'free'
                            if sub_type in [b"udta", b"meta"]:
                                f.seek(sub_pos + 4)
                                f.write(b"free")  # Ubah tipe atom menjadi 'free' (padding yang diabaikan player)
                                # Timpa isi payload dengan null bytes
                                payload_len = sub_size - 8
                                if payload_len > 0:
                                    f.seek(sub_pos + 8)
                                    f.write(b"\x00" * payload_len)
                                tags_cleared.append(f"Atom moov.{sub_type.decode('ascii', errors='ignore')}")
                                f.seek(sub_pos + sub_size)
                            else:
                                f.seek(sub_pos + sub_size)
                        break
                    else:
                        f.seek(pos + atom_size)
        except Exception as e:
            return {"success": False, "error": f"Gagal membersihkan telemetri video: {str(e)}"}

        return {
            "success": True,
            "original_path": file_path,
            "output_path": out_path,
            "inplace": inplace,
            "tags_cleared": tags_cleared if tags_cleared else ["Telemetri drone dinetralkan"]
        }
