"""
Unit Tests untuk Modul Metadata Editors (ImageEditor, PdfEditor, DocxEditor, MediaEditor)
Memverifikasi kemampuan penyuntingan selektif / preservative (misal: hanya mengganti Author).
"""

import os
import unittest
import tempfile
import shutil
from PIL import Image
import piexif
from pypdf import PdfWriter, PdfReader
from docx import Document

from src.editors import get_editor_for_file, is_editable_file
from src.editors.image_editor import ImageEditor
from src.editors.pdf_editor import PdfEditor
from src.editors.docx_editor import DocxEditor

class TestMetadataEditors(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_image_editor_selective_author_change(self):
        """Memverifikasi bahwa hanya tag Artist/Author yang berubah sementara tag lain utuh."""
        img_path = os.path.join(self.test_dir, "test_img.jpg")
        img = Image.new("RGB", (100, 100), color="blue")
        
        # Buat EXIF awal dengan Artist='Original Artist' dan ImageDescription='Keep This Title'
        zeroth_ifd = {
            piexif.ImageIFD.Artist: b"Original Artist",
            piexif.ImageIFD.ImageDescription: b"Keep This Title",
            piexif.ImageIFD.Software: b"TestSoftware v1"
        }
        exif_dict = {"0th": zeroth_ifd, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        exif_bytes = piexif.dump(exif_dict)
        img.save(img_path, exif=exif_bytes)

        editor = ImageEditor()
        fields_before = editor.get_editable_fields(img_path)
        self.assertEqual(fields_before["Artist"], "Original Artist")
        self.assertEqual(fields_before["ImageDescription"], "Keep This Title")

        # Ganti HANYA Artist menjadi 'Yogi Ario'
        res = editor.save_fields(img_path, {"Artist": "Yogi Ario"}, inplace=True)
        self.assertTrue(res["success"])

        # Verifikasi setelah disimpan
        fields_after = editor.get_editable_fields(img_path)
        self.assertEqual(fields_after["Artist"], "Yogi Ario")
        # Field ImageDescription HARUS tetap utuh 'Keep This Title'
        self.assertEqual(fields_after["ImageDescription"], "Keep This Title")
        self.assertEqual(fields_after["Software"], "TestSoftware v1")

    def test_pdf_editor_selective_author_change(self):
        """Memverifikasi pengubahan Author pada dokumen PDF tanpa mengubah Title."""
        pdf_path = os.path.join(self.test_dir, "test_doc.pdf")
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        writer.add_metadata({
            "/Author": "Old Author",
            "/Title": "Universal Standard Document",
            "/Subject": "Testing Suite"
        })
        with open(pdf_path, "wb") as f:
            writer.write(f)

        editor = PdfEditor()
        fields_before = editor.get_editable_fields(pdf_path)
        self.assertEqual(fields_before["Author"], "Old Author")
        self.assertEqual(fields_before["Title"], "Universal Standard Document")

        # Ganti HANYA Author menjadi 'Yogi Ario'
        res = editor.save_fields(pdf_path, {"Author": "Yogi Ario"}, inplace=True)
        self.assertTrue(res["success"])

        # Verifikasi pembacaan ulang via pypdf
        reader = PdfReader(pdf_path)
        self.assertEqual(reader.metadata.author, "Yogi Ario")
        self.assertEqual(reader.metadata.title, "Universal Standard Document")
        self.assertEqual(reader.metadata.subject, "Testing Suite")

    def test_docx_editor_selective_author_change(self):
        """Memverifikasi pengubahan Author pada dokumen DOCX."""
        docx_path = os.path.join(self.test_dir, "test_doc.docx")
        doc = Document()
        doc.add_paragraph("Konten dokumen pengujian.")
        doc.core_properties.author = "Initial Author"
        doc.core_properties.title = "Important Paper"
        doc.save(docx_path)

        editor = DocxEditor()
        fields_before = editor.get_editable_fields(docx_path)
        self.assertEqual(fields_before["Author"], "Initial Author")
        self.assertEqual(fields_before["Title"], "Important Paper")

        # Ganti HANYA Author
        res = editor.save_fields(docx_path, {"Author": "Yogi Ario"}, inplace=True)
        self.assertTrue(res["success"])

        # Verifikasi via Document
        doc_after = Document(docx_path)
        self.assertEqual(doc_after.core_properties.author, "Yogi Ario")
        self.assertEqual(doc_after.core_properties.title, "Important Paper")

    def test_editor_dispatcher(self):
        """Memverifikasi bahwa dispatcher mengenali berkas dengan tepat."""
        self.assertTrue(is_editable_file("sample.jpg"))
        self.assertTrue(is_editable_file("sample.pdf"))
        self.assertTrue(is_editable_file("sample.docx"))
        self.assertTrue(is_editable_file("sample.mp3"))
        self.assertFalse(is_editable_file("sample.unknown"))

if __name__ == "__main__":
    unittest.main()

