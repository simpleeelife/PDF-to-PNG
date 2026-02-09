import os
from pathlib import Path

# Constants
DPI = 200
MAX_PAGES = 30

def get_default_output_dir():
    """Returns the default output directory: User's Pictures/PDF_PNG"""
    user_pictures = Path(os.path.expanduser("~")) / "Pictures"
    output_dir = user_pictures / "PDF_PNG"
    
    # Ensure directory exists
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Fallback if permission issues (though unlikely in user home)
            return Path.cwd() / "Output"
            
    return output_dir
