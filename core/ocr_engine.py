import pytesseract
from PIL import Image
import fitz # PyMuPDF for PDF handling
import os

def extract_text_from_document(file_path: str) -> str:
    """
    Extracts text from an image or PDF document using Tesseract OCR and PyMuPDF.

    Args:
        file_path (str): The path to the document file (JPG, PNG, PDF).

    Returns:
        str: The extracted text from the document.
    """
    text = ""
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension in ['.png', '.jpg', '.jpeg']:
        try:
            # Use Pillow to open the image and pytesseract to extract text
            text = pytesseract.image_to_string(Image.open(file_path))
        except Exception as e:
            print(f"Error extracting text from image {file_path}: {e}")
            raise
    elif file_extension == '.pdf':
        try:
            doc = fitz.open(file_path)
            for page_num in range(doc.page_count):
                page = doc[page_num]
                # Attempt direct text extraction first (for selectable PDFs)
                page_text = page.get_text()
                if page_text.strip(): # If direct text extraction yields content
                    text += page_text
                else:
                    # Fallback to OCR for scanned PDFs (render page to image)
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    text += pytesseract.image_to_string(img)
            doc.close()
        except Exception as e:
            print(f"Error extracting text from PDF {file_path}: {e}")
            raise
    else:
        raise ValueError(f"Unsupported file type: {file_extension}. Only .png, .jpg, .jpeg, .pdf are supported.")

    return text

if __name__ == '__main__':
    # Example usage (for testing this module independently)
    # Make sure you have a sample.png or sample.pdf in your data/raw folder
    # and Tesseract OCR installed and configured in your PATH.

    # Create dummy files for demonstration if they don't exist
    os.makedirs("data/raw", exist_ok=True)
    if not os.path.exists("data/raw/sample_image.png"):
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (400, 200), color = (255, 255, 255))
            d = ImageDraw.Draw(img)
            # Try to load a default font or use a generic one
            try:
                # This path might vary based on OS, using a common one
                font = ImageFont.truetype("arial.ttf", 24)
            except IOError:
                font = ImageFont.load_default() # Fallback to default PIL font
            d.text((50,50), "Hello, OCR World!", fill=(0,0,0), font=font)
            img.save("data/raw/sample_image.png")
            print("Created dummy image: data/raw/sample_image.png")
        except ImportError:
            print("Pillow not fully installed for font rendering. Skipping dummy image creation.")
        except Exception as e:
            print(f"Could not create dummy image: {e}")

    if os.path.exists("data/raw/sample_image.png"):
        print("\n--- Testing Image OCR ---")
        try:
            image_text = extract_text_from_document("data/raw/sample_image.png")
            print("Extracted Text from Image:")
            print(image_text)
        except Exception as e:
            print(f"Failed to extract text from image: {e}")

    # For PDF testing, you'd need a sample PDF.
    # You can create a simple PDF with PyMuPDF or use an existing one.
    if not os.path.exists("data/raw/sample_pdf.pdf"):
        try:
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 50), "This is a sample PDF document.\nIt contains some text for testing OCR.", fontsize=12)
            doc.save("data/raw/sample_pdf.pdf")
            doc.close()
            print("Created dummy PDF: data/raw/sample_pdf.pdf")
        except Exception as e:
            print(f"Could not create dummy PDF: {e}")

    if os.path.exists("data/raw/sample_pdf.pdf"):
        print("\n--- Testing PDF OCR ---")
        try:
            pdf_text = extract_text_from_document("data/raw/sample_pdf.pdf")
            print("Extracted Text from PDF:")
            print(pdf_text)
        except Exception as e:
            print(f"Failed to extract text from PDF: {e}")