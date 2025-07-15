import unittest
import os
from PIL import Image, ImageDraw, ImageFont
import fitz # PyMuPDF

# Assuming core.ocr_engine is in the parent directory or correctly in PYTHONPATH
# For local testing, you might need to adjust sys.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from core.ocr_engine import extract_text_from_document

class TestOCREngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up dummy files for testing."""
        cls.test_dir = "test_data"
        os.makedirs(cls.test_dir, exist_ok=True)

        # Create a dummy image file
        cls.image_path = os.path.join(cls.test_dir, "test_image.png")
        img = Image.new('RGB', (400, 200), color = (255, 255, 255))
        d = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except IOError:
            font = ImageFont.load_default()
        d.text((50,50), "Test OCR Image", fill=(0,0,0), font=font)
        img.save(cls.image_path)

        # Create a dummy PDF file (selectable text)
        cls.pdf_selectable_path = os.path.join(cls.test_dir, "test_selectable_pdf.pdf")
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "This is selectable text in PDF.", fontsize=12)
        doc.save(cls.pdf_selectable_path)
        doc.close()

        # Create a dummy scanned PDF (image-based PDF, requires OCR fallback)
        cls.pdf_scanned_path = os.path.join(cls.test_dir, "test_scanned_pdf.pdf")
        # For a true "scanned" PDF, we'd embed an image.
        # For simplicity, we'll create a PDF where direct text extraction is empty
        # and rely on the OCR fallback.
        # (Note: PyMuPDF's get_text() usually returns something even from image-only if OCR is run by it.
        # This test relies on the `extract_text_from_document`'s logic to try direct then OCR).
        
        # A more realistic "scanned" PDF simulation:
        img_for_pdf = Image.new('RGB', (600, 400), color = (255, 255, 255))
        d_img = ImageDraw.Draw(img_for_pdf)
        try:
            font_img = ImageFont.truetype("arial.ttf", 30)
        except IOError:
            font_img = ImageFont.load_default()
        d_img.text((100,100), "Scanned PDF Text", fill=(0,0,0), font=font_img)
        img_for_pdf.save(os.path.join(cls.test_dir, "temp_scanned_img.png"))
        
        doc_scanned = fitz.open()
        img_page = doc_scanned.new_page(width=img_for_pdf.width, height=img_for_pdf.height)
        img_page.insert_image(img_page.rect, filename=os.path.join(cls.test_dir, "temp_scanned_img.png"))
        doc_scanned.save(cls.pdf_scanned_path)
        doc_scanned.close()


    @classmethod
    def tearDownClass(cls):
        """Clean up dummy files after testing."""
        if os.path.exists(cls.image_path):
            os.remove(cls.image_path)
        if os.path.exists(cls.pdf_selectable_path):
            os.remove(cls.pdf_selectable_path)
        if os.path.exists(cls.pdf_scanned_path):
            os.remove(cls.pdf_scanned_path)
        if os.path.exists(os.path.join(cls.test_dir, "temp_scanned_img.png")):
            os.remove(os.path.join(cls.test_dir, "temp_scanned_img.png"))
        if os.path.exists(cls.test_dir):
            os.rmdir(cls.test_dir)

    def test_extract_text_from_image(self):
        """Test text extraction from an image."""
        extracted_text = extract_text_from_document(self.image_path)
        self.assertIn("Test OCR Image", extracted_text)

    def test_extract_text_from_selectable_pdf(self):
        """Test text extraction from a PDF with selectable text."""
        extracted_text = extract_text_from_document(self.pdf_selectable_path)
        self.assertIn("This is selectable text in PDF.", extracted_text)

    def test_extract_text_from_scanned_pdf(self):
        """Test text extraction from a scanned (image-based) PDF."""
        # This test relies on Tesseract's ability to OCR the embedded image in the PDF.
        extracted_text = extract_text_from_document(self.pdf_scanned_path)
        self.assertIn("Scanned PDF Text", extracted_text)

    def test_unsupported_file_type(self):
        """Test handling of unsupported file types."""
        unsupported_file = os.path.join(self.test_dir, "test.txt")
        with open(unsupported_file, "w") as f:
            f.write("This is a text file.")
        
        with self.assertRaises(ValueError) as cm:
            extract_text_from_document(unsupported_file)
        self.assertIn("Unsupported file type", str(cm.exception))
        os.remove(unsupported_file)

if __name__ == '__main__':
    unittest.main()