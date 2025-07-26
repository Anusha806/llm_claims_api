import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text.replace("\n", " ").replace("  ", " ").strip()
    except Exception as e:
        print(f"PDF Extraction Error: {e}")
        return ""
