# file_processor.py
import PyPDF2
from docx import Document

def process_file(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    else:
        raise ValueError(f"Unsupported file type: {file.type}")