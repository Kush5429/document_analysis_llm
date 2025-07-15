def get_prompt_template(doc_type: str, document_text: str) -> str:
    """
    Returns an LLM prompt template tailored to the document type for information extraction.

    Args:
        doc_type (str): The type of document ('invoice', 'contract', 'form', 'general').
        document_text (str): The raw text extracted from the document.

    Returns:
        str: The formatted prompt string for the LLM.
    """

    if doc_type == "invoice":
        prompt_template = f"""
        You are an expert at extracting structured information from invoices.
        Your task is to extract the following entities from the provided invoice text and present them in a JSON format.
        Ensure the JSON is valid and complete. If a field is not found, set its value to `null`.

        Expected JSON Schema:
        ```json
        {{
            "invoice_number": "string | null",
            "date": "string (YYYY-MM-DD format) | null",
            "vendor_name": "string | null",
            "customer_name": "string | null",
            "total_amount": "string (e.g., '123.45') | null",
            "currency": "string (e.g., 'USD', 'EUR') | null",
            "items": [
                {{
                    "description": "string | null",
                    "quantity": "number | null",
                    "unit_price": "string (e.g., '10.00') | null",
                    "line_total": "string (e.g., '100.00') | null"
                }}
            ],
            "payment_terms": "string | null",
            "summary": "A concise, one-sentence summary of the invoice, including vendor, total, and purpose."
        }}
        ```

        Invoice Text:
        ---
        {document_text}
        ---

        Please provide only the JSON output.
        """
    elif doc_type == "contract":
        prompt_template = f"""
        You are an expert at extracting key information and summarizing legal contracts.
        Your task is to extract the following entities from the provided contract text and present them in a JSON format.
        Ensure the JSON is valid and complete. If a field is not found, set its value to `null`.

        Expected JSON Schema:
        ```json
        {{
            "contract_title": "string | null",
            "parties": "array of strings (names of parties involved) | null",
            "effective_date": "string (YYYY-MM-DD format) | null",
            "termination_date": "string (YYYY-MM-DD format) | null",
            "governing_law": "string | null",
            "key_clauses_summary": "A brief summary (2-3 sentences) of the most important clauses (e.g., scope of work, payment terms, liability, intellectual property).",
            "overall_summary": "A one-paragraph overall summary of the contract's purpose, main agreements, and duration."
        }}
        ```

        Contract Text:
        ---
        {document_text}
        ---

        Please provide only the JSON output.
        """
    elif doc_type == "form":
        prompt_template = f"""
        You are an expert at extracting information from various forms.
        Your task is to extract key fields from the provided form text and present them in a JSON format.
        Identify common form fields like Name, Address, Phone, Email, Date of Birth, etc., along with any specific fields
        that appear to be relevant to the form's purpose.
        Ensure the JSON is valid and complete. If a field is not found, set its value to `null`.

        Expected JSON Schema (adapt based on detected fields):
        ```json
        {{
            "form_type": "string (e.g., 'Application Form', 'Registration Form') | null",
            "applicant_name": "string | null",
            "address": "string | null",
            "phone_number": "string | null",
            "email": "string | null",
            "date_of_birth": "string (YYYY-MM-DD format) | null",
            "purpose_of_form": "string | null",
            "summary": "A concise summary of the form's content and purpose."
        }}
        ```
        Adapt the fields in the JSON schema based on the content of the form.

        Form Text:
        ---
        {document_text}
        ---

        Please provide only the JSON output.
        """
    else: # General document analysis
        prompt_template = f"""
        You are a highly intelligent assistant capable of understanding and summarizing any document.
        Your task is to extract the most important entities and provide a concise summary from the provided text.
        Present the extracted information and summary in a JSON format.
        Ensure the JSON is valid and complete. If a field is not found or not applicable, set its value to `null`.

        Expected JSON Schema:
        ```json
        {{
            "document_main_topic": "string | null",
            "key_entities": "array of strings (important names, places, dates, concepts) | null",
            "main_points": "array of strings (bullet points of key takeaways) | null",
            "overall_summary": "A one-paragraph comprehensive summary of the document's content and purpose."
        }}
        ```

        Document Text:
        ---
        {document_text}
        ---

        Please provide only the JSON output.
        """
    
    return prompt_template

if __name__ == '__main__':
    # Example usage
    sample_invoice_text = """
    INVOICE #2024-001
    Date: 2024-07-12
    From: Acme Solutions
    To: Global Innovations
    Description: Software Development
    Qty: 1
    Unit Price: 5000.00
    Total: $5000.00 USD
    Payment Terms: Net 30
    """
    invoice_prompt = get_prompt_template("invoice", sample_invoice_text)
    print("--- Invoice Prompt ---")
    print(invoice_prompt)

    sample_contract_text = """
    SERVICE AGREEMENT
    This Agreement is made on 15th May, 2023
    Between: Party A (John Doe) and Party B (Jane Smith)
    Governing Law: California
    Scope of Work: Design and development of a new website.
    """
    contract_prompt = get_prompt_template("contract", sample_contract_text)
    print("\n--- Contract Prompt ---")
    print(contract_prompt)

    sample_general_text = """
    The quick brown fox jumps over the lazy dog. This is a test document.
    It contains some random information for general analysis.
    """
    general_prompt = get_prompt_template("general", sample_general_text)
    print("\n--- General Document Prompt ---")
    print(general_prompt)