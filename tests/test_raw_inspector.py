"""
Pengujian Unit untuk Raw Camera Inspector & Cleaner.
"""
import os
import struct
import unittest
import tempfile
import shutil
from src.inspectors.raw_inspector import RawCameraInspector
from src.cleaners.raw_cleaner import RawCameraCleaner

class TestRawCamera(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.raw_file = os.path.join(self.test_dir, "sample.arw")
        self._create_mock_tiff_raw(self.raw_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_mock_tiff_raw(self, path: str):
        """Membuat mock berkas RAW berbasis TIFF dengan Make, Model, Serial, dan GPS."""
        with open(path, "wb") as f:
            # Header TIFF: Little Endian ('II'), magic 42 (0x002A), offset IFD0 = 8
            f.write(b"II\x2A\x00\x08\x00\x00\x00")
            
            # IFD0: 4 entri tag
            # Tag 0x010F: Make (ASCII)
            # Tag 0x0110: Model (ASCII)
            # Tag 0xA431: BodySerialNumber (ASCII)
            # Tag 0x8825: GPSInfo (Pointer)
            num_entries = 4
            f.write(struct.pack("<H", num_entries))

            # Entry 1: Make -> 'SONY'
            # tag, type(2=ASCII), count(5), val_or_offset
            # Karena count=5 > 4, simpan di offset 80
            f.write(struct.pack("<HHI I", 0x010F, 2, 5, 80))

            # Entry 2: Model -> 'ILCE-7M4' (Sony A7 IV), offset 88
            f.write(struct.pack("<HHI I", 0x0110, 2, 9, 88))

            # Entry 3: BodySerialNumber -> 'SN987654321', offset 100
            f.write(struct.pack("<HHI I", 0xA431, 2, 12, 100))

            # Entry 4: GPSInfo -> Pointer ke offset 120
            f.write(struct.pack("<HHI I", 0x8825, 4, 1, 120))

            # Next IFD offset = 0
            f.write(struct.pack("<I", 0))

            # Tulis data string di offset yang sesuai
            f.seek(80)
            f.write(b"SONY\x00")

            f.seek(88)
            f.write(b"ILCE-7M4\x00")

            f.seek(100)
            f.write(b"SN987654321\x00")

            # Tulis sub-IFD GPSInfo di offset 120 (1 entri: GPSVersionID)
            f.seek(120)
            f.write(struct.pack("<H", 1))
            f.write(struct.pack("<HHI I", 0x0000, 1, 4, 0x00020202))
            f.write(struct.pack("<I", 0))

    def test_raw_inspector_detection(self):
        """Memverifikasi bahwa RAW inspector mendeteksi kamera Sony, serial number, dan GPS."""
        inspector = RawCameraInspector()
        self.assertTrue(inspector.can_inspect(self.raw_file))

        info = inspector.inspect(self.raw_file)
        self.assertTrue(info["has_metadata"])
        self.assertIn("Perangkat & Nomor Seri", info["categories"])

        device_info = info["categories"]["Perangkat & Nomor Seri"]
        self.assertEqual(device_info.get("Make"), "SONY")
        self.assertEqual(device_info.get("Model"), "ILCE-7M4")
        self.assertEqual(device_info.get("BodySerialNumber"), "SN987654321")

        # Cek Risk Score (Kamera Serial + GPS menghasilkan status tinggi)
        self.assertGreaterEqual(info.get("risk_score", 0), 30)

    def test_raw_cleaner(self):
        """Memverifikasi bahwa RAW cleaner membersihkan serial number dan GPS."""
        cleaner = RawCameraCleaner()
        self.assertTrue(cleaner.can_clean(self.raw_file))

        res = cleaner.clean(self.raw_file, inplace=True)
        self.assertTrue(res["success"])

        # Re-inspect
        info_cleaned = RawCameraInspector().inspect(self.raw_file)
        device_info = info_cleaned.get("categories", {}).get("Perangkat & Nomor Seri", {})
        self.assertNotEqual(device_info.get("BodySerialNumber"), "SN987654321")
        self.assertNotIn("Lokasi GPS", info_cleaned.get("categories", {}))

if __name__ == "__main__":
    unittest.main()
