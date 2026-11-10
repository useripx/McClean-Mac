"""
Pengujian Unit untuk Release Tool & SemVer Validator.
"""
import unittest
from tools.create_release import validate_tag

class TestReleaseTool(unittest.TestCase):

    def test_valid_semver_tags(self):
        """Memverifikasi bahwa format tag yang valid dikenali dengan benar."""
        valid_tags = ["v1.0.0", "v1.1.0", "v2.0.0", "v1.0.0-macos", "v1.1.0-beta.1"]
        for tag in valid_tags:
            self.assertTrue(validate_tag(tag), f"Tag {tag} seharusnya valid!")

    def test_invalid_semver_tags(self):
        """Memverifikasi bahwa format tag yang salah ditolak."""
        invalid_tags = ["1.0.0", "v1", "v1.0", "release-1.0", "v1.0.0.0", "v_1_0_0"]
        for tag in invalid_tags:
            self.assertFalse(validate_tag(tag), f"Tag {tag} seharusnya tidak valid!")

if __name__ == "__main__":
    unittest.main()
