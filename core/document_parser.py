import os
import json
from core.ocr_engine import extract_text_from_document
from core.llm_client import get_llm_response
from core.prompt_manager import get_prompt_template
from core.data_transformer import transform_llm_output_to_dataframe

def analyze_document_pipeline(
    file_path: str,
    llm_api_key: str,
    llm_provider: str = "openai"
) -> dict:
    """
    Executes the full document analysis pipeline: OCR -> LLM -> Transformation.

    Args:
        file_path (str): Path to the input document (PDF, JPG, PNG).
        llm_api_key (str): API key for the LLM service.
        llm_provider (str): The LLM provider to use ('openai' or 'gemini').

    Returns:
        dict: A dictionary containing the raw text, extracted data, and processed dataframes.
              Returns an empty dictionary if any step fails.
    """
    results = {
        "raw_text": "",
        "extracted_data": {},
        "main_fields_df": None,
        "item_df": None,
        "summary_text": ""
    }

    try:
        # 1. OCR to extract raw text
        print(f"Starting OCR for {file_path}...")
        raw_text = extract_text_from_document(file_path)
        results["raw_text"] = raw_text
        print("OCR complete.")

        if not raw_text.strip():
            print("No text extracted by OCR. Skipping LLM analysis.")
            return results

        # 2. Determine document type and get LLM prompt
        # Simple heuristic to guess document type for prompt selection
        doc_type = "general"
        raw_text_lower = raw_text.lower()
        if "invoice" in raw_text_lower or "bill" in raw_text_lower:
            doc_type = "invoice"
        elif "contract" in raw_text_lower or "agreement" in raw_text_lower or "terms and conditions" in raw_text_lower:
            doc_type = "contract"
        elif "form" in raw_text_lower or "application" in raw_text_lower:
            doc_type = "form"
        
        prompt = get_prompt_template(doc_type, raw_text)
        print(f"Sending document to LLM ({llm_provider}) for analysis with '{doc_type}' prompt...")

        # 3. Use LLM to extract and summarize key entities
        llm_output_json_str = get_llm_response(prompt, llm_api_key, llm_provider)
        
        extracted_data = json.loads(llm_output_json_str)
        results["extracted_data"] = extracted_data
        print("LLM analysis complete.")

        # 4. Transform LLM output for display
        _, main_fields, item_df, summary_content = transform_llm_output_to_dataframe(extracted_data)
        results["main_fields"] = main_fields
        results["item_df"] = item_df
        results["summary_text"] = summary_content
        print("Data transformation complete.")

    except json.JSONDecodeError as e:
        print(f"Error: LLM did not return valid JSON: {e}")
        print(f"LLM Raw Output:\n{llm_output_json_str}")
    except Exception as e:
        print(f"An error occurred during the document analysis pipeline: {e}")

    return results

if __name__ == '__main__':
    # Example usage (for testing the full pipeline independently)
    from dotenv import load_dotenv
    load_dotenv() # Load API keys from .env

    # Ensure data/raw directory exists and place a sample file there for testing
    os.makedirs("data/raw", exist_ok=True)
    sample_file_path = "data/raw/sample_invoice.pdf" # Or .png, .jpg

    # Create a dummy PDF for testing if it doesn't exist
    if not os.path.exists(sample_file_path):
        try:
            import fitz # PyMuPDF
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 50), "INVOICE #ABC-123\nDate: 2024-07-15\nVendor: My Company\nTotal Amount: $500.00 USD\nPayment Terms: Due upon receipt\nDescription: Consulting Services", fontsize=12)
            doc.save(sample_file_path)
            doc.close()
            print(f"Created dummy PDF for testing: {sample_file_path}")
        except Exception as e:
            print(f"Could not create dummy PDF for testing: {e}. Please place a sample PDF/image manually.")
            sample_file_path = None # Disable test if no sample file

    if sample_file_path and os.path.exists(sample_file_path):
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        provider = "openai" if os.getenv("OPENAI_API_KEY") else ("gemini" if os.getenv("GOOGLE_API_KEY") else None)

        if api_key and provider:
            print(f"\n--- Running Full Analysis Pipeline for {sample_file_path} ---")
            analysis_results = analyze_document_pipeline(sample_file_path, api_key, provider)

            print("\n--- Analysis Results ---")
            print(f"Raw Text (first 500 chars):\n{analysis_results['raw_text'][:500]}...")
            print("\nExtracted Data (JSON):")
            print(json.dumps(analysis_results['extracted_data'], indent=2))
            print("\nMain Fields:")
            print(analysis_results['main_fields'])
            if not analysis_results['item_df'].empty:
                print("\nItem DataFrame:")
                print(analysis_results['item_df'])
            print("\nSummary Text:")
            print(analysis_results['summary_text'])
        else:
            print("API key not found. Please set OPENAI_API_KEY or GOOGLE_API_KEY in your .env file to run pipeline test.")
    else:
        print("No sample file found for pipeline testing. Please ensure 'data/raw/sample_invoice.pdf' exists.")