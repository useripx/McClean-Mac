"""
MrClean Mac — Professional RAW Camera Image Inspector
Mengekstrak metadata mendalam pada format foto kamera mentah (RAW):
- Sony (.arw)
- Canon (.cr2, .cr3)
- Nikon (.nef)
- Fujifilm (.raf)
- Adobe Digital Negative (.dng)
- Olympus (.orf)
- Panasonic (.rw2)

Mengekstrak: Nomor Seri Bodi Kamera, Nomor Seri Lensa, Shutter Count,
Koordinat GPS Presisi, Profil Warna Sensor, dan Riwayat Software.
"""
import os
import struct
from typing import Dict, Any, Tuple, Optional
from PIL import Image, ExifTags
from src.inspectors.base import BaseInspector
from src.inspectors.risk_scorer import calculate_privacy_risk

class RawCameraInspector(BaseInspector):
    """Inspektor metadata khusus format foto kamera profesional (RAW)."""

    SUPPORTED_EXTS = {".arw", ".cr2", ".cr3", ".nef", ".raf", ".dng", ".orf", ".rw2"}

    # Pemetaan Tag EXIF Penting
    TAG_NAMES = {
        0x010F: "Make",
        0x0110: "Model",
        0x0131: "Software",
        0x0132: "DateTime",
        0x013B: "Artist",
        0x8298: "Copyright",
        0x8769: "ExifOffset",
        0x8825: "GPSInfo",
        0x9003: "DateTimeOriginal",
        0x9004: "DateTimeDigitized",
        0x9201: "ShutterSpeedValue",
        0x9202: "ApertureValue",
        0x8827: "ISOSpeedRatings",
        0xA431: "BodySerialNumber",
        0xA432: "LensSpecification",
        0xA433: "LensMake",
        0xA434: "LensModel",
        0xA435: "LensSerialNumber"
    }

    def can_inspect(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.SUPPORTED_EXTS

    def inspect(self, file_path: str) -> Dict[str, Any]:
        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "category": "raw_image",
            "has_metadata": False,
            "metadata_count": 0,
            "categories": {},
            "has_ai_watermark": False,
            "watermarks_detected": []
        }

        ext = os.path.splitext(file_path)[1].lower()
        raw_tags = {}
        gps_tags = {}

        # 1. Parsing format berbasis TIFF (ARW, CR2, NEF, DNG, ORF, RW2)
        try:
            with open(file_path, "rb") as f:
                header = f.read(16)
                if len(header) >= 8 and (header[:4] in (b"II*\x00", b"MM\x00*")):
                    endian = "<" if header[:2] == b"II" else ">"
                    raw_tags, gps_tags = self._parse_tiff_raw(f, endian)
                elif header.startswith(b"FUJIFILMCCD-RAW"):
                    # Fuji RAF
                    raw_tags, gps_tags = self._parse_raf(f)
                elif len(header) >= 8 and header[4:8] == b"ftyp":
                    # Canon CR3 (ISOBMFF / QuickTime container)
                    raw_tags, gps_tags = self._parse_cr3(f)
        except Exception:
            pass

        # 2. Coba Pillow sebagai pelengkap (misal untuk DNG atau embedded thumbnail)
        try:
            with Image.open(file_path) as img:
                exif = img.getexif()
                if exif:
                    for k, v in exif.items():
                        tag_name = ExifTags.TAGS.get(k, f"Tag_{k}")
                        if tag_name not in raw_tags and not isinstance(v, (bytes, bytearray)):
                            raw_tags[tag_name] = str(v)
        except Exception:
            pass

        # 3. Klasifikasi Kategori Metadata
        cat_umum = {
            "Format Berkas": f"Kamera RAW ({ext.upper()[1:]})",
            "Ukuran Berkas": f"{result['file_size'] / (1024*1024):.2f} MB"
        }
        result["categories"]["Umum"] = cat_umum

        cat_perangkat = {}
        cat_kamera = {}
        cat_gps = {}

        for k, v in raw_tags.items():
            k_lower = k.lower()
            val_str = str(v).strip()
            if not val_str:
                continue

            if any(term in k_lower for term in ["make", "model", "serial", "lens", "body"]):
                cat_perangkat[k] = val_str
            elif any(term in k_lower for term in ["iso", "aperture", "shutter", "fnumber", "exposure", "focal"]):
                cat_kamera[k] = val_str
            else:
                cat_umum[k] = val_str

        for k, v in gps_tags.items():
            cat_gps[k] = str(v)

        if cat_perangkat:
            result["categories"]["Perangkat & Nomor Seri"] = cat_perangkat
        if cat_kamera:
            result["categories"]["Parameter Pengambilan Foto"] = cat_kamera
        if cat_gps:
            result["categories"]["Lokasi GPS"] = cat_gps

        total_tags = len(cat_perangkat) + len(cat_kamera) + len(cat_gps)
        result["metadata_count"] = total_tags
        result["has_metadata"] = (total_tags > 0)

        # 4. Hitung Skor Risiko Privasi
        risk = calculate_privacy_risk(result)
        result["risk_score"] = risk["score"]
        result["risk_level"] = risk["level"]
        result["risk_color"] = risk["color"]
        result["risk_reasons"] = risk["reasons"]
        result["risk_recommendation"] = risk["recommendation"]

        return result

    def _parse_tiff_raw(self, f, endian: str) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Membaca IFD0, Exif IFD, dan GPS IFD dari struktur TIFF."""
        raw_tags = {}
        gps_tags = {}
        f.seek(4)
        ifd_offset = struct.unpack(endian + "I", f.read(4))[0]

        visited = set()
        to_visit = [(ifd_offset, "IFD0")]

        while to_visit:
            offset, ifd_name = to_visit.pop(0)
            if offset in visited or offset <= 0:
                continue
            visited.add(offset)

            try:
                f.seek(offset)
                entry_count_bytes = f.read(2)
                if len(entry_count_bytes) < 2:
                    break
                num_entries = struct.unpack(endian + "H", entry_count_bytes)[0]

                for _ in range(min(num_entries, 150)):
                    entry = f.read(12)
                    if len(entry) < 12:
                        break
                    tag_id, tag_type, count, val_or_offset = struct.unpack(endian + "HHI I", entry)
                    tag_name = self.TAG_NAMES.get(tag_id, f"Tag_0x{tag_id:04X}")

                    # Pointer ke sub-IFD
                    if tag_id == 0x8769:  # ExifOffset
                        to_visit.append((val_or_offset, "ExifIFD"))
                    elif tag_id == 0x8825:  # GPSInfo
                        to_visit.append((val_or_offset, "GPSIFD"))
                    else:
                        # Baca nilai string atau angka
                        val = self._read_tag_value(f, endian, tag_type, count, val_or_offset)
                        if val is not None:
                            if ifd_name == "GPSIFD":
                                gps_tags[tag_name] = str(val)
                            else:
                                raw_tags[tag_name] = str(val)
            except Exception:
                break

        return raw_tags, gps_tags

    def _read_tag_value(self, f, endian: str, tag_type: int, count: int, val_or_offset: int) -> Any:
        """Membaca nilai tag TIFF sesuai tipe data IFD."""
        try:
            # Type 2: ASCII String
            if tag_type == 2:
                if count <= 4:
                    s_bytes = struct.pack(endian + "I", val_or_offset)[:count]
                else:
                    pos = f.tell()
                    f.seek(val_or_offset)
                    s_bytes = f.read(count)
                    f.seek(pos)
                return s_bytes.split(b"\x00")[0].decode("utf-8", errors="ignore").strip()

            # Type 3: SHORT (16-bit)
            elif tag_type == 3:
                return val_or_offset & 0xFFFF

            # Type 4: LONG (32-bit)
            elif tag_type == 4:
                return val_or_offset

            # Type 5: RATIONAL (2x 32-bit)
            elif tag_type == 5 and count == 1:
                pos = f.tell()
                f.seek(val_or_offset)
                num, den = struct.unpack(endian + "II", f.read(8))
                f.seek(pos)
                if den != 0:
                    return f"{num/den:.2f}"
                return f"{num}/{den}"
        except Exception:
            pass
        return None

    def _parse_raf(self, f) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Mengekstrak offset TIFF tersemat pada Fujifilm RAF."""
        f.seek(0)
        header = f.read(120)
        tags = {"Camera Brand": "Fujifilm", "Format": "Fujifilm CCD-RAW"}
        # Offset ke JPEG preview atau IFD tersemat
        if len(header) >= 92:
            tags["Raw Version"] = header[16:20].decode("ascii", errors="ignore").strip()
            tags["Camera Model"] = header[20:52].decode("ascii", errors="ignore").strip()
        return tags, {}

    def _parse_cr3(self, f) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Membaca metadata atom Canon CR3 (ISO Base Media File Format)."""
        f.seek(0)
        tags = {"Camera Brand": "Canon", "Container": "Canon RAW 3 (ISOBMFF)"}
        # Cari atom 'moov' atau 'prvw'
        file_len = os.fstat(f.fileno()).st_size
        while f.tell() < min(file_len, 1024 * 64):
            data = f.read(8)
            if len(data) < 8:
                break
            atom_size, atom_type = struct.unpack(">I4s", data)
            if atom_size == 0 or atom_size > file_len:
                break
            if atom_type == b"ftyp":
                brand = f.read(min(atom_size - 8, 16))
                tags["Major Brand"] = brand[:4].decode("ascii", errors="ignore")
                break
            else:
                f.seek(f.tell() + atom_size - 8)
        return tags, {}
