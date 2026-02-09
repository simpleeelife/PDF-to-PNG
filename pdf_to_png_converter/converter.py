import os
import fitz  # PyMuPDF
from pathlib import Path
from . import config

class ConversionError(Exception):
    pass

class ValidationError(Exception):
    pass

def validate_pdf(file_path):
    """
    Validates the PDF file based on requirements.
    Raises ValidationError if invalid.
    """
    if not os.path.exists(file_path):
        raise ValidationError(f"File not found: {file_path}")
    
    if not file_path.lower().endswith('.pdf'):
        raise ValidationError("Not a PDF file.")

    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise ValidationError(f"Could not open file. It may be corrupted or not a valid PDF.\nDetails: {str(e)}")

    if doc.needs_pass:
        doc.close()
        raise ValidationError("Password protected PDFs are not supported.")

    if doc.page_count > config.MAX_PAGES:
        count = doc.page_count
        doc.close()
        raise ValidationError(f"Page count limit exceeded. Max: {config.MAX_PAGES}, Actual: {count}")
    
    return doc

def convert_pdf(file_path, output_dir, progress_callback=None):
    """
    Converts a PDF file to PNGs.
    
    Args:
        file_path: Path to input PDF
        output_dir: Path object for output directory
        progress_callback: Function accepting (current_page, total_pages, filename)
    """
    try:
        doc = validate_pdf(file_path)
    except ValidationError:
        raise
    except Exception as e:
        raise ConversionError(f"Unexpected error during validation: {str(e)}")

    total_pages = doc.page_count
    base_name = Path(file_path).stem
    # Sanitize filename (replace invalid chars)
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        base_name = base_name.replace(char, '_')

    output_files = []

    try:
        for i in range(total_pages):
            page = doc.load_page(i)
            # Zoom = DPI / 72
            zoom = config.DPI / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Format: Basename_001.png
            out_filename = f"{base_name}_{i+1:03d}.png"
            out_path = output_dir / out_filename
            
            pix.save(str(out_path))
            output_files.append(str(out_path))

            if progress_callback:
                progress_callback(i + 1, total_pages, out_filename)
                
    except Exception as e:
        raise ConversionError(f"Error converting page {i+1}: {str(e)}")
    finally:
        doc.close()

    return output_files
