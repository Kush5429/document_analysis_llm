Document Analysis Using LLMs: Intelligent Automation for Unstructured Data
This repository houses the full-stack AI project "Document Analysis Using LLMs," a powerful tool designed to revolutionize how organizations interact with unstructured document data. Leveraging advanced Optical Character Recognition (OCR) and Large Language Models (LLMs), this solution automates the extraction, understanding, and summarization of critical information from diverse document types, including contracts, invoices, and forms. Transform your manual document processing into an intelligent, efficient, and accurate pipeline, culminating in stylish, downloadable PDF summaries for immediate insights.

Features
Document Upload: Easily upload scanned images (JPG, PNG) or PDF documents.

OCR Integration: Extracts raw text from documents using Tesseract OCR.

LLM-Powered Extraction: Utilizes Large Language Models (e.g., OpenAI, Gemini) to intelligently parse and extract key entities and information.

Concise Summarization: Generates clear, actionable summaries of document content.

Styled PDF Export: Creates professional, well-formatted PDF summaries for easy sharing and archival.

Scalable Architecture: Designed with modular components for easy extension and deployment.

Project Structure
document_analysis_llm/
├── app/                    # Streamlit/Gradio UI application
│   ├── main.py             # Main Streamlit app entry point
│   ├── ui_components.py    # Reusable UI elements (optional)
│   └── static/             # Static assets (logo, CSS)
├── core/                   # Core AI pipeline logic
│   ├── document_parser.py  # Orchestrates the document analysis pipeline
│   ├── ocr_engine.py       # Tesseract OCR wrapper
│   ├── llm_client.py       # LLM API interaction
│   ├── prompt_manager.py   # Manages LLM prompt templates
│   ├── data_transformer.py # Processes/cleans LLM output
│   └── pdf_generator.py    # PDF generation logic
├── data/                   # Data storage (raw, processed, training)
├── models/                 # Fine-tuned models or artifacts (if applicable)
├── tests/                  # Unit and integration tests
├── notebooks/              # Jupyter notebooks for experimentation
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker containerization setup
├── README.md               # Project documentation
├── LICENSE                 # Project license
└── .gitignore              # Files/folders to ignore in Git

Setup and Installation
Clone the repository:

git clone https://github.com/your-username/document-analysis-llm.git
cd document-analysis-llm

Create a virtual environment (recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Python dependencies:

pip install -r requirements.txt

Install Tesseract OCR:

Linux (Debian/Ubuntu):

sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev

macOS (using Homebrew):

brew install tesseract

Windows: Download the installer from Tesseract-OCR GitHub and add it to your system's PATH.

Set up Environment Variables:

Rename .env.example to .env.

Open .env and add your API keys:

OPENAI_API_KEY="your_openai_api_key_here"
# Or for Gemini:
# GOOGLE_API_KEY="your_google_gemini_api_key_here"

Usage
Run the Streamlit application:

streamlit run app/main.py

Open your web browser and navigate to the local URL provided by Streamlit (usually http://localhost:8501).

Upload your document, click the analysis buttons, and download the generated PDF summary.

Deployment (using Docker)
For production deployment, Docker is recommended for consistent environments.

Build the Docker image:

docker build -t document-analysis-llm .

Run the Docker container locally (for testing):

docker run -p 8501:8501 --env-file .env document-analysis-llm

(Ensure your .env file is in the same directory where you run this command, or specify its full path.)

Deploy to a cloud platform:

Push your Docker image to a container registry (e.g., Docker Hub, AWS ECR, Google Container Registry).

Deploy the image to a managed container service like Google Cloud Run, AWS Fargate, Azure Container Apps, or Heroku. Remember to configure environment variables for API keys on your chosen platform.

Contributing
Contributions are welcome! Please feel free to open issues or submit pull requests.

License
This project is licensed under the MIT License - see the LICENSE file for details.