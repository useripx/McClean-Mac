"""
Pengujian Unit untuk Offline Map Dialog & DMS Converter.
"""
import unittest
from unittest.mock import MagicMock
from src.gui.dialogs.map_dialog import OfflineMapDialog

class TestOfflineMap(unittest.TestCase):

    def test_dms_conversion_north_east(self):
        """Memverifikasi konversi desimal ke DMS untuk lintang utara dan bujur timur."""
        # Padang: 0.9471° S, 100.4172° E
        # Mock parent
        dummy_parent = MagicMock()
        dialog = OfflineMapDialog.__new__(OfflineMapDialog)
        
        # Test DMS Utarah / Timur
        dms_lat = dialog._to_dms(3.5952, is_lat=True)
        self.assertIn("U", dms_lat)
        self.assertIn("3°", dms_lat)

        dms_lon = dialog._to_dms(98.6722, is_lat=False)
        self.assertIn("T", dms_lon)
        self.assertIn("98°", dms_lon)

    def test_dms_conversion_south_west(self):
        """Memverifikasi konversi desimal ke DMS untuk lintang selatan dan bujur barat."""
        dummy_parent = MagicMock()
        dialog = OfflineMapDialog.__new__(OfflineMapDialog)

        dms_lat = dialog._to_dms(-6.2088, is_lat=True)
        self.assertIn("S", dms_lat)
        self.assertIn("6°", dms_lat)

        dms_lon = dialog._to_dms(-74.0060, is_lat=False)
        self.assertIn("B", dms_lon)
        self.assertIn("74°", dms_lon)

if __name__ == "__main__":
    unittest.main()
