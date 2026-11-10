"""
MrClean Mac — Drone & Action Camera Telemetry Inspector
Mengekstrak telemetri penerbangan drone (DJI, Autel, Skydio) dan action camera (GoPro, Insta360):
- Model Drone & Serial Number Pesawat / Pilot
- Titik Lepas Landas (Home Point GPS) & Ketinggian Penerbangan (Altitude)
- Jejak Telemetri Subtitle Stream (QuickTime udta / meta atom & GPMF stream)
"""
import os
import re
import struct
from typing import Dict, Any, List
from src.inspectors.base import BaseInspector
from src.inspectors.risk_scorer import calculate_privacy_risk

class DroneTelemetryInspector(BaseInspector):
    """Inspektor telemetri penerbangan drone & action camera pada berkas video MP4/MOV."""

    SUPPORTED_EXTS = {".mp4", ".mov"}

    # Pola Regex Subtitle Telemetri Drone (misal DJI OSD text stream)
    DJI_SUBTITLE_PATTERN = re.compile(
        r"\[(?:latitude|lat)\s*:\s*([+-]?\d+\.?\d*)\]\s*\[(?:longitude|long|lon)\s*:\s*([+-]?\d+\.?\d*)\]",
        re.IGNORECASE
    )
    ALTITUDE_PATTERN = re.compile(r"\[(?:altitude|alt|rel_alt)\s*:\s*([+-]?\d+\.?\d*)(?:m)?\]", re.IGNORECASE)
    DRONE_MODEL_PATTERN = re.compile(r"(DJI\s+[A-Za-z0-9\- ]+|Mavic|Mini \d|Phantom|Inspire|Avata|Matrice)", re.IGNORECASE)

    def can_inspect(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.SUPPORTED_EXTS

    def inspect(self, file_path: str) -> Dict[str, Any]:
        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "category": "drone_video",
            "has_metadata": False,
            "metadata_count": 0,
            "categories": {},
            "has_ai_watermark": False,
            "watermarks_detected": []
        }

        drone_info = {}
        gps_info = {}

        try:
            with open(file_path, "rb") as f:
                atoms = self._scan_quicktime_atoms(f)
                
                # 1. Cari data di User Data Atom (udta)
                for atom_path, data in atoms.items():
                    if "udta" in atom_path or "meta" in atom_path:
                        text_content = data.decode("latin-1", errors="ignore")
                        
                        # Cek model drone
                        model_match = self.DRONE_MODEL_PATTERN.search(text_content)
                        if model_match:
                            drone_info["Model Drone / Kamera"] = model_match.group(1).strip()

                        # Cek GPS di udta / subtitle
                        gps_match = self.DJI_SUBTITLE_PATTERN.search(text_content)
                        if gps_match:
                            lat = float(gps_match.group(1))
                            lon = float(gps_match.group(2))
                            gps_info["Latitude"] = f"{lat:.6f}"
                            gps_info["Longitude"] = f"{lon:.6f}"

                        alt_match = self.ALTITUDE_PATTERN.search(text_content)
                        if alt_match:
                            gps_info["Ketinggian (Altitude)"] = f"{alt_match.group(1)} meter"

                        # Cek GoPro GPMF
                        if b"gpmd" in data or b"GPMF" in data:
                            drone_info["Sensor Telemetri"] = "GoPro GPMF Stream (Akselerometer, Gyro, GPS)"
        except Exception:
            pass

        if drone_info:
            result["categories"]["Telemetri Drone & Kamera Aksi"] = drone_info
        if gps_info:
            result["categories"]["Lokasi GPS"] = gps_info

        total_tags = len(drone_info) + len(gps_info)
        result["metadata_count"] = total_tags
        result["has_metadata"] = (total_tags > 0)

        # Hitung skor risiko privasi
        risk = calculate_privacy_risk(result)
        result["risk_score"] = risk["score"]
        result["risk_level"] = risk["level"]
        result["risk_color"] = risk["color"]
        result["risk_reasons"] = risk["reasons"]
        result["risk_recommendation"] = risk["recommendation"]

        return result

    def _scan_quicktime_atoms(self, f) -> Dict[str, bytes]:
        """Memindai atom-atom QuickTime level teratas dan 'moov.udta'."""
        atoms = {}
        file_len = os.fstat(f.fileno()).st_size
        f.seek(0)

        while f.tell() < min(file_len, 1024 * 1024 * 16):  # Pindai hingga 16 MB pertama
            pos = f.tell()
            header = f.read(8)
            if len(header) < 8:
                break
            atom_size, atom_type_raw = struct.unpack(">I4s", header)
            atom_type = atom_type_raw.decode("latin-1", errors="ignore")

            if atom_size == 0:
                break
            if atom_size == 1:
                # 64-bit size
                ext_size = f.read(8)
                if len(ext_size) < 8:
                    break
                atom_size = struct.unpack(">Q", ext_size)[0]
                header_len = 16
            else:
                header_len = 8

            # Telusuri atom moov untuk mencari udta
            if atom_type == "moov":
                moov_end = pos + atom_size
                while f.tell() < moov_end:
                    sub_pos = f.tell()
                    sub_header = f.read(8)
                    if len(sub_header) < 8:
                        break
                    sub_size, sub_type_raw = struct.unpack(">I4s", sub_header)
                    sub_type = sub_type_raw.decode("latin-1", errors="ignore")
                    if sub_size < 8 or sub_size > moov_end - sub_pos:
                        break

                    if sub_type in ["udta", "meta"]:
                        payload_len = min(sub_size - 8, 1024 * 128)
                        atoms[f"moov.{sub_type}"] = f.read(payload_len)
                        f.seek(sub_pos + sub_size)
                    else:
                        f.seek(sub_pos + sub_size)
                break
            else:
                f.seek(pos + atom_size)

        return atoms
