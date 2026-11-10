"""
MetaClean — Image Metadata Inspector
Mengekstrak EXIF, GPS, kamera, software, dimensi, dan chunk data teks pada format gambar.
"""
import os
from typing import Dict, Any
from PIL import Image, ExifTags
from src.inspectors.base import BaseInspector

class ImageInspector(BaseInspector):
    SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp", ".gif"}

    def can_inspect(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.SUPPORTED_EXTS

    def _convert_gps_coords(self, coords, ref) -> str:
        """Mengonversi koordinat derajat menit detik ke format string desimal."""
        try:
            d = float(coords[0])
            m = float(coords[1])
            s = float(coords[2])
            val = d + (m / 60.0) + (s / 3600.0)
            if ref in ["S", "W"]:
                val = -val
            return f"{val:.6f}° {ref}"
        except Exception:
            return f"{coords} {ref}"

    def inspect(self, file_path: str) -> Dict[str, Any]:
        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "category": "image",
            "has_metadata": False,
            "metadata_count": 0,
            "categories": {},
            "has_ai_watermark": False,
            "watermarks_detected": []
        }

        try:
            with Image.open(file_path) as img:
                # 1. Kategori Informasi Umum Gambar
                general_info = {
                    "Format": img.format,
                    "Mode Warna": img.mode,
                    "Dimensi": f"{img.width} x {img.height} piksel"
                }
                result["categories"]["Umum"] = general_info

                exif_data = {}
                gps_data = {}
                png_info = {}

                # 2. Ekstraksi EXIF jika tersedia
                raw_exif = img.getexif()
                if raw_exif:
                    for tag_id, value in raw_exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        if tag_name == "GPSInfo":
                            # GPS tags
                            try:
                                for gps_id, gps_val in value.items():
                                    gps_tag_name = ExifTags.GPSTAGS.get(gps_id, str(gps_id))
                                    gps_data[gps_tag_name] = str(gps_val)
                            except Exception:
                                gps_data["Raw GPS"] = str(value)
                        else:
                            # Bersihkan representasi value
                            if isinstance(value, bytes):
                                try:
                                    value = value.decode("utf-8", errors="ignore").strip("\x00")
                                except Exception:
                                    value = f"<{len(value)} bytes binary>"
                            exif_data[tag_name] = str(value)

                # Format GPS Latitude & Longitude jika lengkap
                if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
                    gps_data["Koordinat Lintang (Lat)"] = str(gps_data["GPSLatitude"])
                if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
                    gps_data["Koordinat Bujur (Long)"] = str(gps_data["GPSLongitude"])

                # 3. Ekstraksi PNG Text Chunks / Metadata Tambahan
                if hasattr(img, "info") and img.info:
                    for k, v in img.info.items():
                        if k in ["exif", "icc_profile"]:
                            continue
                        str_val = str(v)
                        if len(str_val) > 200:
                            str_val = str_val[:200] + "... (dipotong)"
                        png_info[str(k)] = str_val
                        # Deteksi prompt AI generator (seperti Midjourney / Stable Diffusion)
                        if any(term in str(k).lower() for term in ["parameters", "prompt", "workflow", "c2pa"]):
                            result["has_ai_watermark"] = True
                            result["watermarks_detected"].append(f"AI Generation Metadata chunk: {k}")

                # Cek apakah ada C2PA manifest pada bytes file
                try:
                    with open(file_path, "rb") as bf:
                        content_sample = bf.read(1024 * 512)
                        if b"c2pa" in content_sample or b"jumbf" in content_sample:
                            result["has_ai_watermark"] = True
                            result["watermarks_detected"].append("C2PA Content Provenance Manifest terdeteksi")
                except Exception:
                    pass

                if exif_data:
                    result["categories"]["EXIF Kamera & Perangkat"] = exif_data
                if gps_data:
                    result["categories"]["Lokasi GPS"] = gps_data
                if png_info:
                    result["categories"]["Metadata Dokumen/PNG Info"] = png_info

                total_tags = len(exif_data) + len(gps_data) + len(png_info)
                result["metadata_count"] = total_tags
                result["has_metadata"] = total_tags > 0

        except Exception as e:
            result["categories"]["Error"] = {"Pesan": f"Gagal membaca gambar: {str(e)}"}

        return result

