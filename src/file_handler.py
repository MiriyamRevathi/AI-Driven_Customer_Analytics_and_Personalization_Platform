from datetime import datetime
from pathlib import Path

from werkzeug.utils import secure_filename

from config.settings import Config


def allowed_file(filename):
    """Return True only when the filename has an approved upload extension."""
    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in Config.ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    """Create a sanitized timestamped filename to avoid collisions."""
    safe_name = secure_filename(filename)
    if not safe_name:
        raise ValueError("Invalid filename.")

    # Keep the extension decision tied to the original validated filename,
    # while using Werkzeug's sanitized stem for the saved local file.
    original_extension = filename.rsplit(".", 1)[1].lower()
    safe_stem = Path(safe_name).stem
    if not safe_stem or original_extension not in Config.ALLOWED_EXTENSIONS:
        raise ValueError("Invalid filename or file extension.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{safe_stem}_{timestamp}.{original_extension}"


def save_uploaded_file(file):
    """
    Validate and save an uploaded Flask FileStorage object.

    The function returns a small structured dictionary so routes can keep
    response formatting consistent without duplicating file safety logic.
    """
    if file is None:
        return {
            "success": False,
            "error": "No file part found in the request.",
        }

    if not file.filename:
        return {
            "success": False,
            "error": "No file selected for upload.",
        }

    if not allowed_file(file.filename):
        allowed = ", ".join(f".{ext}" for ext in sorted(Config.ALLOWED_EXTENSIONS))
        return {
            "success": False,
            "error": f"Invalid file type. Allowed formats: {allowed}.",
        }

    upload_folder = Path(Config.UPLOAD_FOLDER)
    upload_folder.mkdir(parents=True, exist_ok=True)

    try:
        unique_filename = generate_unique_filename(file.filename)
    except ValueError as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    destination = upload_folder / unique_filename

    # Defense in depth: ensure the final path stays inside the upload folder.
    resolved_upload_folder = upload_folder.resolve()
    resolved_destination = destination.resolve()
    if resolved_upload_folder not in resolved_destination.parents:
        return {
            "success": False,
            "error": "Unsafe file path detected.",
        }

    file.save(resolved_destination)

    return {
        "success": True,
        "filename": unique_filename,
        "path": str(resolved_destination),
    }
