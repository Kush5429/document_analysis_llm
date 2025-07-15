import pandas as pd
import json

def transform_llm_output_to_dataframe(extracted_data: dict) -> tuple[pd.DataFrame, dict, pd.DataFrame, str]:
    """
    Transforms the raw dictionary output from the LLM into a more structured format
    suitable for display in Streamlit, including main fields, itemized data, and summary.

    Args:
        extracted_data (dict): The dictionary parsed from the LLM's JSON output.

    Returns:
        tuple[pd.DataFrame, dict, pd.DataFrame, str]:
            - A DataFrame containing all extracted key-value pairs.
            - A dictionary of main fields (excluding 'items' and summaries).
            - A DataFrame of itemized data (e.g., invoice line items), empty if not present.
            - A string containing the overall summary.
    """
    
    # Initialize variables
    main_fields = {}
    item_df = pd.DataFrame()
    summary_content = ""
    
    # Separate main fields from 'items' and summary fields
    for key, value in extracted_data.items():
        if key == 'items' and isinstance(value, list):
            if value: # Only process if items list is not empty
                try:
                    item_df = pd.DataFrame(value)
                except ValueError:
                    print(f"Warning: 'items' field could not be converted to DataFrame: {value}")
                    item_df = pd.DataFrame() # Ensure it's an empty DataFrame on error
        elif key in ['summary', 'key_clauses_summary', 'overall_summary']:
            # Prioritize overall_summary, then key_clauses_summary, then general summary
            if key == 'overall_summary' and value:
                summary_content = value
            elif key == 'key_clauses_summary' and value and not summary_content:
                summary_content = value
            elif key == 'summary' and value and not summary_content:
                summary_content = value
        else:
            main_fields[key] = value

    # Create a DataFrame for all key-value pairs (excluding items for simplicity in this DF)
    # This DataFrame is mostly for internal consistency or if you want to display everything flat
    all_data_for_df = {k: v for k, v in extracted_data.items() if k != 'items'}
    # Flatten nested lists/dicts within all_data_for_df if they are not items
    for key, value in all_data_for_df.items():
        if isinstance(value, list):
            all_data_for_df[key] = ", ".join(map(str, value))
        elif isinstance(value, dict):
            all_data_for_df[key] = json.dumps(value)

    # Create a single DataFrame from all extracted data (excluding items, as they get their own DF)
    # This DataFrame is more for a conceptual "all data" view.
    # For display, `main_fields` and `item_df` are more practical.
    full_df = pd.DataFrame([all_data_for_df])

    return full_df, main_fields, item_df, summary_content

if __name__ == '__main__':
    # Example usage
    sample_invoice_data = {
        "invoice_number": "INV-2024-001",
        "date": "2024-07-12",
        "vendor_name": "Acme Corp.",
        "total_amount": "123.45",
        "currency": "USD",
        "items": [
            {"description": "Product A", "quantity": 2, "unit_price": "10.00", "line_total": "20.00"},
            {"description": "Service B", "quantity": 1, "unit_price": "100.00", "line_total": "100.00"}
        ],
        "payment_terms": "Net 30",
        "summary": "Invoice from Acme Corp. for products and services totaling $123.45."
    }

    sample_contract_data = {
        "contract_title": "Consulting Agreement",
        "parties": ["Client A", "Consultant B"],
        "effective_date": "2024-01-01",
        "termination_date": "2024-12-31",
        "governing_law": "Delaware",
        "key_clauses_summary": "This agreement outlines consulting services, payment terms, and confidentiality.",
        "overall_summary": "This is a one-year consulting agreement between Client A and Consultant B for advisory services."
    }

    print("--- Transforming Invoice Data ---")
    full_df_invoice, main_fields_invoice, item_df_invoice, summary_invoice = transform_llm_output_to_dataframe(sample_invoice_data)
    print("\nMain Fields (Invoice):")
    print(main_fields_invoice)
    print("\nItem DataFrame (Invoice):")
    print(item_df_invoice)
    print("\nSummary (Invoice):")
    print(summary_invoice)
    print("\nFull DataFrame (Invoice - conceptual):")
    print(full_df_invoice)

    print("\n--- Transforming Contract Data ---")
    full_df_contract, main_fields_contract, item_df_contract, summary_contract = transform_llm_output_to_dataframe(sample_contract_data)
    print("\nMain Fields (Contract):")
    print(main_fields_contract)
    print("\nItem DataFrame (Contract - should be empty):")
    print(item_df_contract)
    print("\nSummary (Contract):")
    print(summary_contract)
    print("\nFull DataFrame (Contract - conceptual):")
    print(full_df_contract)

    sample_general_data = {
        "document_main_topic": "AI Development",
        "key_entities": ["LLMs", "Machine Learning", "Neural Networks"],
        "main_points": ["AI is evolving rapidly.", "LLMs are powerful tools.", "Ethical AI is important."],
        "overall_summary": "This document discusses the rapid advancements in AI, focusing on the capabilities of Large Language Models and the importance of ethical considerations in their development and deployment."
    }
    print("\n--- Transforming General Document Data ---")
    full_df_general, main_fields_general, item_df_general, summary_general = transform_llm_output_to_dataframe(sample_general_data)
    print("\nMain Fields (General):")
    print(main_fields_general)
    print("\nItem DataFrame (General - should be empty):")
    print(item_df_general)
    print("\nSummary (General):")
    print(summary_general)
    print("\nFull DataFrame (General - conceptual):")
    print(full_df_general)