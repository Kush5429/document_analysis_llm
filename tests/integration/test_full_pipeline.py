import unittest
import os
import json
import shutil
from unittest.mock import patch, MagicMock

# Assuming core modules are correctly in PYTHONPATH
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from core.document_parser import analyze_document_pipeline
from core.ocr_engine import extract_text_from_document
from core.llm_client import get_llm_response
from core.pdf_generator import create_pdf_summary_weasyprint

class TestFullPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up dummy files and mock external calls for integration testing."""
        cls.test_dir = "integration_test_data"
        os.makedirs(os.path.join(cls.test_dir, "raw"), exist_ok=True)
        os.makedirs(os.path.join(cls.test_dir, "processed"), exist_ok=True)

        # Create a dummy image file for OCR
        cls.dummy_image_path = os.path.join(cls.test_dir, "raw", "integration_test_image.png")
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (400, 200), color = (255, 255, 255))
            d = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except IOError:
                font = ImageFont.load_default()
            d.text((50,50), "Integration Test Invoice #INT-001", fill=(0,0,0), font=font)
            img.save(cls.dummy_image_path)
        except ImportError:
            print("Pillow not installed, cannot create dummy image for integration test.")
            cls.dummy_image_path = None

        # Mock LLM response to avoid actual API calls during integration tests
        cls.mock_llm_response_content = json.dumps({
            "invoice_number": "INT-001",
            "date": "2024-07-16",
            "vendor_name": "Integration Test Vendor",
            "total_amount": "99.99",
            "currency": "USD",
            "items": [
                {"description": "Test Item", "quantity": 1, "unit_price": "99.99", "line_total": "99.99"}
            ],
            "summary": "This is a dummy invoice for integration testing."
        })

    @classmethod
    def tearDownClass(cls):
        """Clean up dummy files and directories."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    @patch('core.llm_client.get_llm_response')
    @patch('core.ocr_engine.extract_text_from_document')
    @patch('core.pdf_generator.create_pdf_summary_weasyprint')
    def test_full_pipeline_success(self, mock_create_pdf, mock_extract_text, mock_get_llm_response):
        """Test the entire pipeline from OCR to PDF generation."""
        if not self.dummy_image_path:
            self.skipTest("Dummy image not created, skipping full pipeline test.")

        # Configure mocks
        mock_extract_text.return_value = "Integration Test Invoice #INT-001\nDate: 2024-07-16\nTotal: $99.99 USD"
        mock_get_llm_response.return_value = self.mock_llm_response_content
        mock_create_pdf.return_value = b"dummy_pdf_bytes"

        api_key = "test_api_key"
        provider = "openai"

        # Run the pipeline
        results = analyze_document_pipeline(self.dummy_image_path, api_key, provider)

        # Assertions
        mock_extract_text.assert_called_once_with(self.dummy_image_path)
        mock_get_llm_response.assert_called_once()
        mock_create_pdf.assert_called_once() # This will be called by main.py, not directly here.
                                            # The `analyze_document_pipeline` returns data,
                                            # and `main.py` then calls PDF generation.
                                            # For this test, we are testing the `analyze_document_pipeline` output.

        self.assertIn("Integration Test Invoice #INT-001", results["raw_text"])
        self.assertIsNotNone(results["extracted_data"])
        self.assertEqual(results["extracted_data"]["invoice_number"], "INT-001")
        self.assertEqual(results["extracted_data"]["total_amount"], "99.99")
        self.assertIn("dummy invoice", results["summary_text"])
        self.assertFalse(results["item_df"].empty)
        self.assertEqual(results["item_df"].iloc[0]["description"], "Test Item")

    @patch('core.llm_client.get_llm_response')
    @patch('core.ocr_engine.extract_text_from_document')
    def test_pipeline_ocr_failure(self, mock_extract_text, mock_get_llm_response):
        """Test pipeline behavior when OCR fails."""
        mock_extract_text.side_effect = Exception("OCR failed")

        api_key = "test_api_key"
        provider = "openai"

        results = analyze_document_pipeline("non_existent_file.pdf", api_key, provider)

        mock_extract_text.assert_called_once()
        mock_get_llm_response.assert_not_called() # LLM should not be called if OCR fails

        self.assertEqual(results["raw_text"], "")
        self.assertEqual(results["extracted_data"], {})
        self.assertIsNone(results["main_fields"])
        self.assertIsNone(results["item_df"])
        self.assertEqual(results["summary_text"], "")

    @patch('core.llm_client.get_llm_response')
    @patch('core.ocr_engine.extract_text_from_document')
    def test_pipeline_llm_json_decode_failure(self, mock_extract_text, mock_get_llm_response):
        """Test pipeline behavior when LLM returns invalid JSON."""
        mock_extract_text.return_value = "Valid text from OCR."
        mock_get_llm_response.return_value = "This is not valid JSON." # Invalid JSON

        api_key = "test_api_key"
        provider = "openai"

        results = analyze_document_pipeline(self.dummy_image_path, api_key, provider)

        mock_extract_text.assert_called_once()
        mock_get_llm_response.assert_called_once()

        self.assertIn("Valid text", results["raw_text"])
        self.assertEqual(results["extracted_data"], {}) # Should be empty due to JSON error
        self.assertIsNone(results["main_fields"])
        self.assertIsNone(results["item_df"])
        self.assertEqual(results["summary_text"], "")


if __name__ == '__main__':
    unittest.main()