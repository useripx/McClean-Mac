"""
Pengujian Unit untuk Audio Steganography & Ultrasonic Watermark Inspector.
"""
import os
import struct
import unittest
import tempfile
import shutil
from src.watermarks.audio_stego import AudioStegoInspector

class TestAudioStego(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.wav_clean = os.path.join(self.test_dir, "clean.wav")
        self.wav_stego = os.path.join(self.test_dir, "stego.wav")

        self._create_mock_wav(self.wav_clean, with_junk=False)
        self._create_mock_wav(self.wav_stego, with_junk=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_mock_wav(self, path: str, with_junk: bool):
        """Membuat mock file WAV dengan atau tanpa chunk tersembunyi."""
        with open(path, "wb") as f:
            # RIFF Header
            f.write(b"RIFF\x00\x00\x00\x00WAVE")

            # fmt chunk (16 bytes)
            f.write(b"fmt \x10\x00\x00\x00")
            f.write(struct.pack("<HHIIHH", 1, 1, 44100, 88200, 2, 16))

            if with_junk:
                # JUNK chunk dengan payload watermark rahasia
                payload = b"WATERMARK_SECRET_PAYLOAD_AI_INSPECTOR"
                f.write(b"JUNK")
                f.write(struct.pack("<I", len(payload)))
                f.write(payload)

            # data chunk kosong (4 bytes audio data)
            f.write(b"data\x04\x00\x00\x00\x00\x00\x00\x00")

            # Update ukuran RIFF total
            size = f.tell() - 8
            f.seek(4)
            f.write(struct.pack("<I", size))

    def test_clean_wav_no_stego(self):
        """Memverifikasi bahwa file WAV bersih tidak terdeteksi stego."""
        res = AudioStegoInspector.inspect_audio(self.wav_clean)
        self.assertFalse(res["has_stego"])
        self.assertEqual(res["stego_count"], 0)

    def test_stego_wav_detected(self):
        """Memverifikasi deteksi chunk JUNK tersembunyi pada file WAV."""
        res = AudioStegoInspector.inspect_audio(self.wav_stego)
        self.assertTrue(res["has_stego"])
        self.assertGreater(res["stego_count"], 0)
        self.assertTrue(any("JUNK" in d for d in res["details"]))

if __name__ == "__main__":
    unittest.main()
