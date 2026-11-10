"""
Pengujian Unit untuk Drone Video Telemetry Inspector & Cleaner.
"""
import os
import struct
import unittest
import tempfile
import shutil
from src.inspectors.drone_inspector import DroneTelemetryInspector
from src.cleaners.drone_cleaner import DroneTelemetryCleaner

class TestDroneTelemetry(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.video_file = os.path.join(self.test_dir, "drone_clip.mp4")
        self._create_mock_drone_mp4(self.video_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_mock_drone_mp4(self, path: str):
        """Membuat mock MP4 dengan atom ftyp dan moov.udta yang memuat telemetri DJI."""
        with open(path, "wb") as f:
            # 1. ftyp atom (16 bytes)
            # size=16, type=ftyp, major_brand=mp42, minor_version=0
            f.write(struct.pack(">I4s4sI", 16, b"ftyp", b"mp42", 0))

            # 2. moov atom yang memuat sub-atom udta
            # payload udta memuat model DJI Mini 4 Pro dan koordinat GPS
            udta_payload = b"DJI Mini 4 Pro Drone Flight Log [latitude: -0.925400] [longitude: 100.362100] [altitude: 85.5m]"
            udta_size = 8 + len(udta_payload)
            udta_atom = struct.pack(">I4s", udta_size, b"udta") + udta_payload

            moov_size = 8 + len(udta_atom)
            moov_atom = struct.pack(">I4s", moov_size, b"moov") + udta_atom

            f.write(moov_atom)

    def test_drone_inspector_detection(self):
        """Memverifikasi deteksi model drone DJI dan koordinat GPS penerbangan."""
        inspector = DroneTelemetryInspector()
        self.assertTrue(inspector.can_inspect(self.video_file))

        info = inspector.inspect(self.video_file)
        self.assertTrue(info["has_metadata"])
        self.assertIn("Telemetri Drone & Kamera Aksi", info["categories"])
        self.assertIn("Lokasi GPS", info["categories"])

        telemetry = info["categories"]["Telemetri Drone & Kamera Aksi"]
        self.assertIn("DJI Mini 4", telemetry.get("Model Drone / Kamera", ""))

        gps = info["categories"]["Lokasi GPS"]
        self.assertEqual(gps.get("Latitude"), "-0.925400")
        self.assertEqual(gps.get("Longitude"), "100.362100")

    def test_drone_cleaner(self):
        """Memverifikasi bahwa telemetri drone di atom udta dinetralkan menjadi atom free."""
        cleaner = DroneTelemetryCleaner()
        self.assertTrue(cleaner.can_clean(self.video_file))

        res = cleaner.clean(self.video_file, inplace=True)
        self.assertTrue(res["success"])

        # Re-inspect
        info_cleaned = DroneTelemetryInspector().inspect(self.video_file)
        self.assertNotIn("Telemetri Drone & Kamera Aksi", info_cleaned.get("categories", {}))
        self.assertNotIn("Lokasi GPS", info_cleaned.get("categories", {}))

if __name__ == "__main__":
    unittest.main()
