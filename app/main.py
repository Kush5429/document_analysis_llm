import streamlit as st
import os
import json
import pandas as pd
from dotenv import load_dotenv

# Import core functionalities
from app.core.ocr_engine import extract_text_from_document
from core.llm_client import get_llm_response
from core.prompt_manager import get_prompt_template
from core.data_transformer import transform_llm_output_to_dataframe
from core.pdf_generator import create_pdf_summary_weasyprint

# Load environment variables from .env file
load_dotenv()

# --- Streamlit UI Configuration ---
st.set_page_config(
    page_title="Document Analysis with LLMs",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS from static folder
# Note: Streamlit doesn't directly support linking local CSS files in the same way
# as a traditional web server. We can inject it.
# To make this work, create app/static/custom.css and add your styles.
# Example:
# with open("app/static/custom.css") as f:
#     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'file_path' not in st.session_state:
    st.session_state['file_path'] = None
if 'raw_text' not in st.session_state:
    st.session_state['raw_text'] = ""
if 'extracted_data' not in st.session_state:
    st.session_state['extracted_data'] = {}

# --- Sidebar for API Key Input ---
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")
    st.subheader("API Keys")

    # Check if API keys are set in environment variables
    openai_api_key_env = os.getenv("OPENAI_API_KEY")
    google_api_key_env = os.getenv("GOOGLE_API_KEY")

    if google_api_key_env: # Prioritize Google Gemini if available
        st.success("Google Gemini API Key loaded from environment variables!", icon="✅")
        st.session_state['llm_api_key'] = google_api_key_env
        st.session_state['llm_provider'] = "gemini"
    elif openai_api_key_env:
        st.success("OpenAI API Key loaded from environment variables!", icon="✅")
        st.session_state['llm_api_key'] = openai_api_key_env
        st.session_state['llm_provider'] = "openai"
    else:
        st.warning("No API key found in environment variables. Please set GOOGLE_API_KEY or OPENAI_API_KEY in your `.env` file.", icon="⚠️")
        st.session_state['llm_api_key'] = None
        st.session_state['llm_provider'] = None

    st.markdown("---")
    st.info("Upload your document, then click 'Extract Text' and 'Analyze with LLM' to see the magic!")

# --- Main Content Area ---
st.title("📄 Document Analysis Using LLMs")
st.markdown("Upload a document (PDF, JPG, PNG) and let AI extract key information and generate a summary.")

uploaded_file = st.file_uploader("Upload your document", type=["pdf", "png", "jpg", "jpeg"], key="file_uploader")

if uploaded_file is not None:
    # Save the file temporarily
    temp_file_path = os.path.join("data", "raw", uploaded_file.name)
    os.makedirs(os.path.dirname(temp_file_path), exist_ok=True) # Ensure directory exists
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state['file_path'] = temp_file_path
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    # Display document preview if possible (for images)
    if uploaded_file.type in ["image/png", "image/jpeg"]:
        st.image(uploaded_file, caption="Uploaded Document Preview", use_column_width=True)
    elif uploaded_file.type == "application/pdf":
        st.info("PDF preview is not directly supported in Streamlit for local files. Text will be extracted.")

    st.markdown("---")
    st.subheader("1. Extract Raw Text (OCR)")
    if st.button("Extract Text", key="extract_text_button"):
        if st.session_state['file_path']:
            with st.spinner("Extracting text using OCR... This may take a moment for large documents."):
                try:
                    st.session_state['raw_text'] = extract_text_from_document(st.session_state['file_path'])
                    st.success("Text extraction complete!")
                except Exception as e:
                    st.error(f"Error during text extraction: {e}")
                    st.session_state['raw_text'] = ""
            
            if st.session_state['raw_text']:
                st.expander("View Raw Extracted Text").code(st.session_state['raw_text'][:2000] + "...", language="text")
            else:
                st.warning("No text could be extracted from the document.")
        else:
            st.warning("Please upload a document first.")

    st.markdown("---")
    st.subheader("2. Analyze Document with LLM")
    if st.button("Analyze with LLM", key="analyze_llm_button"):
        if st.session_state['raw_text'] and st.session_state['llm_api_key']:
            with st.spinner("Sending document to LLM for analysis..."):
                try:
                    # Simple heuristic to guess document type for prompt selection
                    doc_type = "general"
                    raw_text_lower = st.session_state['raw_text'].lower()
                    if "invoice" in raw_text_lower or "bill" in raw_text_lower:
                        doc_type = "invoice"
                    elif "contract" in raw_text_lower or "agreement" in raw_text_lower or "terms and conditions" in raw_text_lower:
                        doc_type = "contract"
                    elif "form" in raw_text_lower or "application" in raw_text_lower:
                        doc_type = "form"

                    prompt = get_prompt_template(doc_type, st.session_state['raw_text'])
                    
                    llm_output_json_str = get_llm_response(
                        prompt,
                        api_key=st.session_state['llm_api_key'],
                        provider=st.session_state['llm_provider']
                    )
                    
                    st.session_state['extracted_data'] = json.loads(llm_output_json_str)
                    st.success("LLM analysis complete!")
                except json.JSONDecodeError:
                    st.error("LLM did not return valid JSON. Please check the prompt or raw text.")
                    st.code(llm_output_json_str) # Show raw LLM output for debugging
                    st.session_state['extracted_data'] = {}
                except Exception as e:
                    st.error(f"Error during LLM analysis: {e}")
                    st.session_state['extracted_data'] = {}
            
            if st.session_state['extracted_data']:
                st.subheader("Extracted Information:")
                # Display extracted data in a user-friendly way
                transformed_df, main_fields, item_df, summary_content = transform_llm_output_to_dataframe(st.session_state['extracted_data'])
                
                if main_fields:
                    st.write("### Key Data")
                    st.table(pd.DataFrame([main_fields]).T.rename(columns={0: 'Value'}))
                
                if not item_df.empty:
                    st.write("### Line Items")
                    st.dataframe(item_df)
                
                if summary_content:
                    st.write("### Summary")
                    st.markdown(summary_content)
            else:
                st.warning("No structured data could be extracted by the LLM.")
        elif not st.session_state['raw_text']:
            st.warning("Please extract text from a document first.")
        elif not st.session_state['llm_api_key']:
            st.error("API key is not configured. Please set it in the sidebar or environment variables.")

    st.markdown("---")
    st.subheader("3. Generate Styled PDF Summary")
    if st.button("Generate PDF", key="generate_pdf_button"):
        if st.session_state['extracted_data']:
            with st.spinner("Generating styled PDF..."):
                try:
                    # Re-derive doc_type for PDF title
                    doc_type = "Document"
                    if st.session_state['extracted_data'].get("invoice_number"):
                        doc_type = "Invoice"
                    elif st.session_state['extracted_data'].get("contract_title"):
                        doc_type = "Contract"

                    pdf_bytes = create_pdf_summary_weasyprint(
                        st.session_state['extracted_data'],
                        doc_type=doc_type,
                        logo_path="app/static/logo.png" # Provide path to your logo
                    )
                    st.success("PDF generated successfully!")
                    
                    st.download_button(
                        label="Download PDF Summary",
                        data=pdf_bytes,
                        file_name=f"{doc_type.lower()}_analysis_summary.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error generating PDF: {e}")
        else:
            st.warning("Please analyze a document with the LLM first to generate data for the PDF.")

# --- Cleanup (Optional, for temporary files) ---
# You might want a cleanup mechanism, e.g., a button to clear session state and delete temp files.
# For simplicity, we'll omit an explicit cleanup button here,
# but in a production app, manage temporary file lifecycle carefully.
