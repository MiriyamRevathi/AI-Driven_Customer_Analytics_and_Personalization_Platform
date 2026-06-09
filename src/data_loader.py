from pathlib import Path

import pandas as pd


def load_excel_file(file_path):
    """Load an Excel workbook into a DataFrame without transforming content."""
    try:
        path = Path(file_path)
        if not path.exists():
            return {
                "success": False,
                "data": None,
                "error": "Uploaded Excel file was not found.",
            }

        dataframe = pd.read_excel(path)
        if dataframe.empty:
            return {
                "success": False,
                "data": None,
                "error": "Excel file is readable but contains no rows.",
            }

        return {
            "success": True,
            "data": dataframe,
            "error": None,
        }

    except ValueError as exc:
        return {
            "success": False,
            "data": None,
            "error": f"Invalid Excel file structure: {exc}",
        }
    except Exception as exc:
        return {
            "success": False,
            "data": None,
            "error": f"Unable to read Excel file: {exc}",
        }


def load_json_file(file_path):
    """Load a JSON file into a DataFrame without transforming content."""
    try:
        path = Path(file_path)
        if not path.exists():
            return {
                "success": False,
                "data": None,
                "error": "Uploaded JSON file was not found.",
            }

        dataframe = pd.read_json(path)
        if dataframe.empty:
            return {
                "success": False,
                "data": None,
                "error": "JSON file is readable but contains no rows.",
            }

        return {
            "success": True,
            "data": dataframe,
            "error": None,
        }

    except ValueError as exc:
        return {
            "success": False,
            "data": None,
            "error": f"Invalid JSON file structure: {exc}",
        }
    except UnicodeDecodeError as exc:
        return {
            "success": False,
            "data": None,
            "error": f"JSON encoding issue: {exc}",
        }
    except Exception as exc:
        return {
            "success": False,
            "data": None,
            "error": f"Unable to read JSON file: {exc}",
        }


def load_dataset(file_path):
    """Dispatch loading by file extension for supported assignment formats."""
    path = Path(file_path)

    if not path.exists():
        return {
            "success": False,
            "data": None,
            "error": "Uploaded file was not found.",
        }

    extension = path.suffix.lower()
    if extension == ".xlsx":
        return load_excel_file(path)

    if extension == ".json":
        return load_json_file(path)

    return {
        "success": False,
        "data": None,
        "error": "Unsupported file extension. Only .xlsx and .json are allowed.",
    }
