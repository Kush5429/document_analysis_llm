import unittest
import os
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

# Assuming core.pdf_generator is in the parent directory or correctly in PYTHONPATH
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from core.pdf_generator import create_pdf_summary_weasyprint

class TestPDFGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up dummy data and a dummy logo for testing."""
        cls.test_output_dir = "test_pdf_output"
        os.makedirs(cls.test_output_dir, exist_ok=True)

        # Dummy logo file
        cls.dummy_logo_path = os.path.join(cls.test_output_dir, "dummy_logo.png")
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 50), color = (200, 200, 255)) # Light blue
            img.save(cls.dummy_logo_path)
        except ImportError:
            cls.dummy_logo_path = None # Cannot create dummy logo without Pillow

        cls.sample_invoice_data = {
            "invoice_number": "INV-12345",
            "date": "2024-07-15",
            "vendor_name": "TestCorp",
            "customer_name": "ClientCo",
            "total_amount": "150.75",
            "currency": "USD",
            "items": [
                {"description": "Item A", "quantity": 2, "unit_price": "25.00", "line_total": "50.00"},
                {"description": "Item B", "quantity": 1, "unit_price": "100.75", "line_total": "100.75"}
            ],
            "payment_terms": "Net 30",
            "summary": "This invoice from TestCorp to ClientCo is for items A and B, totaling $150.75 USD."
        }

        cls.sample_contract_data = {
            "contract_title": "Consulting Agreement",
            "parties": ["Consultant X", "Company Y"],
            "effective_date": "2024-01-01",
            "termination_date": "2024-12-31",
            "governing_law": "California",
            "key_clauses_summary": "Defines scope of consulting, payment schedule, and confidentiality.",
            "overall_summary": "A one-year consulting agreement between Consultant X and Company Y for advisory services."
        }
        
        cls.sample_general_data = {
            "document_main_topic": "Project Overview",
            "key_entities": ["Phase 1", "Budget", "Timeline"],
            "main_points": ["Phase 1 completed on time.", "Budget allocated.", "Next steps defined."],
            "overall_summary": "This document provides an overview of the project, detailing the completion of Phase 1, budget allocation, and future plans."
        }


    @classmethod
    def tearDownClass(cls):
        """Clean up dummy files after testing."""
        if os.path.exists(cls.dummy_logo_path):
            os.remove(cls.dummy_logo_path)
        if os.path.exists(cls.test_output_dir):
            # Remove any generated PDFs during tests
            for f in os.listdir(cls.test_output_dir):
                os.remove(os.path.join(cls.test_output_dir, f))
            os.rmdir(cls.test_output_dir)

    @patch('weasyprint.HTML.write_pdf')
    def test_pdf_generation_invoice(self, mock_write_pdf):
        """Test PDF generation for invoice data."""
        mock_write_pdf.return_value = b"dummy_pdf_content_invoice"

        pdf_bytes = create_pdf_summary_weasyprint(
            self.sample_invoice_data,
            doc_type="Invoice",
            logo_path=self.dummy_logo_path
        )
        self.assertEqual(pdf_bytes, b"dummy_pdf_content_invoice")
        mock_write_pdf.assert_called_once()
        # You could further inspect the HTML string passed to HTML() if needed
        # For this test, we verify the function call and return value.

    @patch('weasyprint.HTML.write_pdf')
    def test_pdf_generation_contract(self, mock_write_pdf):
        """Test PDF generation for contract data."""
        mock_write_pdf.return_value = b"dummy_pdf_content_contract"

        pdf_bytes = create_pdf_summary_weasyprint(
            self.sample_contract_data,
            doc_type="Contract",
            logo_path=self.dummy_logo_path
        )
        self.assertEqual(pdf_bytes, b"dummy_pdf_content_contract")
        mock_write_pdf.assert_called_once()

    @patch('weasyprint.HTML.write_pdf')
    def test_pdf_generation_general_doc(self, mock_write_pdf):
        """Test PDF generation for general document data."""
        mock_write_pdf.return_value = b"dummy_pdf_content_general"

        pdf_bytes = create_pdf_summary_weasyprint(
            self.sample_general_data,
            doc_type="Document",
            logo_path=self.dummy_logo_path
        )
        self.assertEqual(pdf_bytes, b"dummy_pdf_content_general")
        mock_write_pdf.assert_called_once()

    @patch('weasyprint.HTML.write_pdf')
    def test_pdf_generation_no_logo(self, mock_write_pdf):
        """Test PDF generation when no logo path is provided."""
        mock_write_pdf.return_value = b"dummy_pdf_content_no_logo"

        pdf_bytes = create_pdf_summary_weasyprint(
            self.sample_invoice_data,
            doc_type="Invoice",
            logo_path=None
        )
        self.assertEqual(pdf_bytes, b"dummy_pdf_content_no_logo")
        mock_write_pdf.assert_called_once()

    @patch('weasyprint.HTML.write_pdf')
    def test_pdf_generation_invalid_logo_path(self, mock_write_pdf):
        """Test PDF generation with an invalid logo path (should proceed without logo)."""
        mock_write_pdf.return_value = b"dummy_pdf_content_invalid_logo"

        pdf_bytes = create_pdf_summary_weasyprint(
            self.sample_invoice_data,
            doc_type="Invoice",
            logo_path="/path/to/nonexistent/logo.png"
        )
        self.assertEqual(pdf_bytes, b"dummy_pdf_content_invalid_logo")
        mock_write_pdf.assert_called_once()


if __name__ == '__main__':
    unittest.main()