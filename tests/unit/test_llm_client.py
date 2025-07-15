import unittest
import os
import json
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Assuming core.llm_client is in the parent directory or correctly in PYTHONPATH
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from core.llm_client import get_llm_response

class TestLLMClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv() # Load API keys from .env for actual API calls if needed

    @patch('openai.chat.completions.create')
    def test_openai_client_success(self, mock_create):
        """Test successful response from OpenAI client."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"key": "value"}'
        mock_create.return_value = mock_response

        prompt = "Extract data."
        api_key = "dummy_openai_key"
        response = get_llm_response(prompt, api_key, provider="openai")
        
        self.assertEqual(response, '{"key": "value"}')
        mock_create.assert_called_once_with(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )

    @patch('openai.chat.completions.create')
    def test_openai_client_api_error(self, mock_create):
        """Test API error handling for OpenAI client."""
        mock_create.side_effect = openai.APIError("Test OpenAI API error", request=MagicMock(), response=MagicMock())

        prompt = "Extract data."
        api_key = "dummy_openai_key"
        with self.assertRaises(openai.APIError):
            get_llm_response(prompt, api_key, provider="openai")

    # @patch('google.generativeai.GenerativeModel')
    # def test_gemini_client_success(self, mock_generative_model):
    #     """Test successful response from Gemini client (if implemented)."""
    #     # Mock the client and its generate_content method
    #     mock_instance = MagicMock()
    #     mock_generative_model.return_value = mock_instance
    #     mock_instance.generate_content.return_value.text = '{"gemini_key": "gemini_value"}'

    #     prompt = "Extract data for Gemini."
    #     api_key = "dummy_gemini_key"
    #     response = get_llm_response(prompt, api_key, provider="gemini")
        
    #     self.assertEqual(response, '{"gemini_key": "gemini_value"}')
    #     mock_generative_model.assert_called_once_with(model_name="gemini-1.5-flash")
    #     mock_instance.generate_content.assert_called_once_with(
    #         prompt,
    #         generation_config={
    #             "response_mime_type": "application/json",
    #             "temperature": 0.0
    #         }
    #     )

    def test_unsupported_provider(self):
        """Test handling of unsupported LLM providers."""
        prompt = "Some text."
        api_key = "some_key"
        with self.assertRaises(ValueError) as cm:
            get_llm_response(prompt, api_key, provider="unsupported")
        self.assertIn("Unsupported LLM provider", str(cm.exception))

    def test_missing_api_key(self):
        """Test handling of missing API key."""
        prompt = "Some text."
        api_key = None
        with self.assertRaises(ValueError) as cm:
            get_llm_response(prompt, api_key, provider="openai")
        self.assertIn("API key is missing", str(cm.exception))

if __name__ == '__main__':
    unittest.main()