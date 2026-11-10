"""
Pengujian Unit untuk Privacy Risk Scorer (Tingkat Bahaya Privasi).
"""
import unittest
from src.inspectors.risk_scorer import calculate_privacy_risk

class TestPrivacyRiskScorer(unittest.TestCase):

    def test_clean_file_risk_score(self):
        """Memverifikasi berkas bersih tanpa metadata memiliki skor 0% dan berstatus AMAN."""
        clean_result = {
            "has_metadata": False,
            "has_ai_watermark": False,
            "metadata_count": 0,
            "categories": {}
        }
        assessment = calculate_privacy_risk(clean_result)
        self.assertEqual(assessment["score"], 0)
        self.assertEqual(assessment["level"], "AMAN")
        self.assertEqual(assessment["color"], "#43a047")

    def test_gps_file_risk_score(self):
        """Memverifikasi berkas dengan koordinat GPS menghasilkan skor signifikan (≥ 40%) status SEDANG/KRITIS."""
        gps_result = {
            "has_metadata": True,
            "has_ai_watermark": False,
            "metadata_count": 2,
            "categories": {
                "Lokasi GPS": {
                    "GPSLatitude": "0.95° S",
                    "GPSLongitude": "100.35° E"
                }
            }
        }
        assessment = calculate_privacy_risk(gps_result)
        self.assertGreaterEqual(assessment["score"], 40)
        self.assertIn("GPS", assessment["reasons"][0])

    def test_critical_combination_risk_score(self):
        """Memverifikasi berkas dengan GPS, Serial Number, dan Author mencapai status KRITIS (≥ 70%)."""
        critical_result = {
            "has_metadata": True,
            "has_ai_watermark": True,
            "metadata_count": 5,
            "categories": {
                "Lokasi GPS": {
                    "GPSLatitude": "0.95° S"
                },
                "EXIF Kamera & Perangkat": {
                    "SerialNumber": "CANON123456",
                    "Author": "Yogi Ario",
                    "Make": "Canon"
                }
            }
        }
        assessment = calculate_privacy_risk(critical_result)
        self.assertGreaterEqual(assessment["score"], 70)
        self.assertEqual(assessment["level"], "KRITIS")
        self.assertEqual(assessment["color"], "#e53935")

    def test_local_path_detection(self):
        """Memverifikasi deteksi path komputer lokal seperti C:\\Users\\yogi\\."""
        path_result = {
            "has_metadata": True,
            "has_ai_watermark": False,
            "metadata_count": 1,
            "categories": {
                "Dokumen": {
                    "SourcePath": "C:\\Users\\yogi\\Documents\\rahasia.docx"
                }
            }
        }
        assessment = calculate_privacy_risk(path_result)
        self.assertGreaterEqual(assessment["score"], 25)
        self.assertTrue(any("direktori" in r.lower() for r in assessment["reasons"]))

if __name__ == "__main__":
    unittest.main()
