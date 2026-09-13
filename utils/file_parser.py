from pathlib import Path
import io

import fitz
from docx import Document


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []

    pdf = fitz.open(stream=file_bytes, filetype="pdf")

    for page in pdf:
        text_parts.append(page.get_text())

    pdf.close()

    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)


def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text(file_name: str, file_bytes: bytes) -> str:
    extension = Path(file_name).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_bytes)

    if extension == ".docx":
        return extract_text_from_docx(file_bytes)

    if extension == ".txt":
        return extract_text_from_txt(file_bytes)

    raise ValueError(
        "Unsupported file type. Please upload PDF, DOCX, or TXT."
    )