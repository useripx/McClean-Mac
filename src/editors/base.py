"""
Interface Dasar Metadata Editor untuk Mrclean
Menyediakan kontrak kerja untuk membaca dan memperbarui metadata secara selektif (preservative).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseMetadataEditor(ABC):
    """Kelas dasar untuk editor metadata per jenis berkas."""

    @abstractmethod
    def get_editable_fields(self, file_path: str) -> Dict[str, str]:
        """
        Membaca metadata yang ada dan mengembalikan kamus pasangan field yang dapat disunting:
        Contoh: {"Author": "John Doe", "Title": "Laporan", ...}
        """
        pass

    @abstractmethod
    def save_fields(self, file_path: str, updated_fields: Dict[str, str], inplace: bool = True) -> Dict[str, Any]:
        """
        Menyimpan pembaruan nilai field ke berkas tanpa menghapus field lain yang tidak diubah.
        Mengembalikan dict: {"success": bool, "output_path": str, "error": str}
        """
        pass

