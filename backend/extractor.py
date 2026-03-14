"""
extractor.py — Text extraction from PDF, DOCX, and TXT resume files.

No bug fixes needed here directly, but path sanitization (B2) is enforced
at the call site in app.py. This module only accepts an already-validated path.
"""

import os
from docx import Document
import pdfplumber


def extract_text(file_path: str) -> str:
    """
    Extract plain text from a resume file.

    Supported formats: .pdf, .docx, .txt
    Returns an empty string for unsupported formats.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext == ".docx":
        return _extract_docx(file_path)
    elif ext == ".txt":
        return _extract_txt(file_path)
    return ""


def _extract_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _extract_pdf(path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        # Return whatever was extracted before the error rather than crashing
        print(f"[extractor] Warning: error reading {path}: {e}")
    return text


def _extract_docx(path: str) -> str:
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        print(f"[extractor] Warning: error reading {path}: {e}")
        return ""
