from weasyprint import HTML, CSS
from datetime import datetime
import os
import json
import pandas as pd

def create_pdf_summary_weasyprint(extracted_data: dict, doc_type: str = "Document", logo_path: str = None) -> bytes:
    """
    Generates a styled PDF summary from extracted document data using WeasyPrint.

    Args:
        extracted_data (dict): A dictionary containing the extracted information from the LLM.
                               Expected to have keys like 'invoice_number', 'summary', 'items', etc.
        doc_type (str): The type of document (e.g., 'Invoice', 'Contract', 'Document'). Used for title.
        logo_path (str): Path to a company logo image. If provided, it will be included.

    Returns:
        bytes: The PDF content as bytes.
    """
    
    # Prepare data for display in PDF
    main_fields = {}
    item_data_html = ""
    summary_content = ""
    
    for key, value in extracted_data.items():
        if key == 'items' and isinstance(value, list):
            if value: # Only process if items list is not empty
                item_df = pd.DataFrame(value)
                # Convert DataFrame to HTML table
                item_data_html = item_df.to_html(index=False, classes="item-table")
        elif key in ['summary', 'key_clauses_summary', 'overall_summary']:
            if key == 'overall_summary' and value:
                summary_content = value
            elif key == 'key_clauses_summary' and value and not summary_content:
                summary_content = value
            elif key == 'summary' and value and not summary_content:
                summary_content = value
        else:
            main_fields[key] = value

    # Generate HTML content for the PDF
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{doc_type.capitalize()} Analysis Summary</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Lato:wght@400;700&display=swap" rel="stylesheet">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Lato:wght@400;700&display=swap');
            body {{
                font-family: 'Roboto', sans-serif;
                margin: 40px;
                color: #333;
                line-height: 1.6;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 10px;
                border-bottom: 2px solid #eee;
            }}
            .header img {{
                max-width: 150px;
                height: auto;
                margin-bottom: 10px;
                border-radius: 8px; /* Rounded corners for logo */
            }}
            .header h1 {{
                color: #2c3e50;
                font-family: 'Lato', sans-serif;
                font-size: 28px;
                margin: 0;
            }}
            h2 {{
                color: #34495e;
                font-family: 'Lato', sans-serif;
                font-size: 22px;
                border-bottom: 1px solid #ddd;
                padding-bottom: 5px;
                margin-top: 30px;
                margin-bottom: 15px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                border-radius: 8px; /* Rounded corners for table */
                overflow: hidden; /* Ensures corners apply */
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                color: #555;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .summary-section p {{
                background-color: #f9f9f9;
                border-left: 5px solid #3498db; /* Accent color border */
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 8px; /* Rounded corners for summary box */
            }}
            .footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 10px;
                border-top: 1px solid #eee;
                font-size: 12px;
                color: #777;
            }}
        </style>
    </head>
    <body>
    """
    
    # Header with optional logo
    if logo_path and os.path.exists(logo_path):
        html_content += f"""
        <div class="header">
            <img src="file:///{os.path.abspath(logo_path)}" alt="Company Logo">
            <h1>{doc_type.capitalize()} Analysis Report</h1>
        </div>
        """
    else:
        html_content += f"""
        <div class="header">
            <h1>{doc_type.capitalize()} Analysis Report</h1>
        </div>
        """

    # Extracted Key Data Table
    if main_fields:
        html_content += "<h2>Extracted Key Data</h2>"
        html_content += "<table>"
        for key, value in main_fields.items():
            # Format key for display
            display_key = key.replace('_', ' ').title()
            if isinstance(value, list):
                display_value = ", ".join(map(str, value))
            elif value is None:
                display_value = "N/A"
            else:
                display_value = str(value)
            html_content += f"<tr><th>{display_key}</th><td>{display_value}</td></tr>"
        html_content += "</table>"

    # Handle line items for invoices/forms
    if item_data_html:
        html_content += "<h2>Line Items / Details</h2>"
        html_content += item_data_html

    # Summary Paragraph
    if summary_content:
        html_content += "<div class='summary-section'>"
        html_content += f"<h2>Summary</h2><p>{summary_content}</p>"
        html_content += "</div>"

    # Timestamp & footer
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_content += f"""
        <div class="footer">
            Generated on: {timestamp}<br>
            Document Analysis Using LLMs - &copy; 2025
        </div>
    </body>
    </html>
    """

    # Generate PDF
    try:
        # WeasyPrint can directly take HTML string and generate PDF bytes
        pdf_file_bytes = HTML(string=html_content).write_pdf()
        return pdf_file_bytes
    except Exception as e:
        print(f"Error during PDF generation with WeasyPrint: {e}")
        raise

if __name__ == '__main__':
    # Example usage (for testing this module independently)
    sample_data_invoice = {
        "invoice_number": "INV-TEST-007",
        "date": "2025-07-12",
        "vendor_name": "Test Solutions Inc.",
        "customer_name": "Client Corp.",
        "total_amount": "999.99",
        "currency": "USD",
        "items": [
            {"description": "Consulting Service", "quantity": 5, "unit_price": "150.00", "line_total": "750.00"},
            {"description": "Software License", "quantity": 1, "unit_price": "249.99", "line_total": "249.99"}
        ],
        "payment_terms": "Net 30",
        "summary": "This invoice from Test Solutions Inc. to Client Corp. is for consulting and software, totaling $999.99 USD."
    }

    sample_data_contract = {
        "contract_title": "Software Development Agreement",
        "parties": ["Developer Ltd.", "Startup Innovations"],
        "effective_date": "2025-01-01",
        "termination_date": "2025-12-31",
        "governing_law": "New York",
        "key_clauses_summary": "Agreement covers custom software development, intellectual property assignment, and a fixed project fee.",
        "overall_summary": "This is a one-year agreement between Developer Ltd. and Startup Innovations for custom software development, detailing project scope, payment, and IP rights."
    }

    # Ensure data/processed directory exists for output
    os.makedirs("data/processed", exist_ok=True)

    print("--- Generating Sample Invoice PDF ---")
    try:
        # Create a dummy logo file for testing if it doesn't exist
        logo_test_path = "app/static/logo.png"
        os.makedirs(os.path.dirname(logo_test_path), exist_ok=True)
        if not os.path.exists(logo_test_path):
            try:
                from PIL import Image
                img = Image.new('RGB', (150, 50), color = (70, 130, 180)) # SteelBlue
                img.save(logo_test_path)
                print(f"Created dummy logo at {logo_test_path}")
            except ImportError:
                print("Pillow not installed, cannot create dummy logo. PDF will be generated without logo.")
                logo_test_path = None # Set to None if logo cannot be created

        pdf_bytes_invoice = create_pdf_summary_weasyprint(
            sample_data_invoice,
            doc_type="Invoice",
            logo_path=logo_test_path
        )
        with open("data/processed/invoice_summary_test.pdf", "wb") as f:
            f.write(pdf_bytes_invoice)
        print("Sample invoice PDF generated successfully at data/processed/invoice_summary_test.pdf")
    except Exception as e:
        print(f"Failed to generate sample invoice PDF: {e}")

    print("\n--- Generating Sample Contract PDF ---")
    try:
        pdf_bytes_contract = create_pdf_summary_weasyprint(
            sample_data_contract,
            doc_type="Contract",
            logo_path=logo_test_path
        )
        with open("data/processed/contract_summary_test.pdf", "wb") as f:
            f.write(pdf_bytes_contract)
        print("Sample contract PDF generated successfully at data/processed/contract_summary_test.pdf")
    except Exception as e:
        print(f"Failed to generate sample contract PDF: {e}")