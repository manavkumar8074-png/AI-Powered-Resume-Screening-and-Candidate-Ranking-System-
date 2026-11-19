from pypdf import PdfReader

def extract_text_from_pdf(file_path):
    """
    Extracts text from a given PDF file path or file-like object.
    """
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.strip()