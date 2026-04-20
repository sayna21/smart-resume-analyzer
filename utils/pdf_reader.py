"""
=============================================================
 SMART RESUME ANALYZER — PDF READER
=============================================================
 
"""

import pdfplumber
import io
from typing import Tuple


def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extract text from PDF bytes.
    
    Returns:
        tuple: (extracted_text, page_count)
    
    Raises:
        ValueError: if file is not a valid PDF or is scanned-only
    """
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            page_count = len(pdf.pages)
            
            if page_count == 0:
                raise ValueError("PDF has no pages.")
            
            # Cap at 10 pages — resumes should be 1-2 pages
            pages_to_read = min(page_count, 10)
            
            all_text = []
            empty_pages = 0
            
            for i in range(pages_to_read):
                page = pdf.pages[i]
                
                # extract_text() with layout=True respects column order
                text = page.extract_text(layout=True) or ""
                
                if not text.strip():
                    empty_pages += 1
                    # Try without layout as fallback
                    text = page.extract_text() or ""
                
                if text.strip():
                    all_text.append(text)
            
            full_text = "\n".join(all_text)
            
            # Detect scanned PDF (no extractable text)
            if not full_text.strip() or empty_pages == pages_to_read:
                raise ValueError(
                    "This PDF appears to be a scanned image. "
                    "Please upload a text-based PDF resume. "
                    "Tip: Export from Google Docs / MS Word as PDF."
                )
            
            # Minimum content check — real resume should have at least 100 chars
            if len(full_text.strip()) < 100:
                raise ValueError(
                    "Very little text extracted from PDF. "
                    "Please ensure the resume is text-based, not an image scan."
                )
            
            return full_text, page_count
    
    except pdfplumber.pdfminer.pdfparser.PDFSyntaxError:
        raise ValueError("Invalid or corrupted PDF file.")
    except PermissionError:
        raise ValueError("PDF is password-protected. Please remove the password first.")
    except ValueError:
        raise  # Re-raise our own ValueError messages
    except Exception as e:
        raise ValueError(f"Could not read PDF: {str(e)}")


def validate_file_size(file_bytes: bytes, max_mb: int = 5) -> None:
    """Ensure uploaded file is within size limits."""
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_mb:
        raise ValueError(
            f"File too large ({size_mb:.1f}MB). Maximum allowed: {max_mb}MB. "
            f"Please compress the PDF or remove embedded images."
        )


def validate_file_type(filename: str, content_type: str) -> None:
    """Ensure uploaded file is a PDF."""
    if not filename.lower().endswith(".pdf"):
        raise ValueError(f"Only PDF files are accepted. Got: {filename}")
    if "pdf" not in content_type.lower() and content_type != "application/octet-stream":
        raise ValueError(f"Invalid content type: {content_type}. Expected application/pdf")