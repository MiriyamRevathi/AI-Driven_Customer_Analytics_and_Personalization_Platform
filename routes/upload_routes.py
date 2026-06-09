from flask import Blueprint, jsonify, render_template, request

from src.data_cleaner import clean_dataset
from src.data_loader import load_dataset
from src.data_validator import validate_dataset
from src.file_handler import save_uploaded_file


upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["GET"])
def upload_page():
    return render_template("upload.html")


@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    try:
        # Flask stores uploaded files in request.files when the form uses
        # enctype="multipart/form-data". The field name must stay "file".
        if "file" not in request.files:
            return jsonify(
                {
                    "success": False,
                    "error": "No file field found. Use form field name 'file'.",
                }
            ), 400

        # All filename, extension, path, and save checks live in file_handler
        # so later data-loading code can reuse the same upload safety contract.
        result = save_uploaded_file(request.files.get("file"))
        if not result["success"]:
            return jsonify(result), 400

        load_result = load_dataset(result["path"])
        if not load_result["success"]:
            return jsonify(
                {
                    "success": False,
                    "errors": [load_result["error"]],
                }
            ), 422

        validation_result = validate_dataset(load_result["data"])
        if not validation_result["success"]:
            return jsonify(
                {
                    "success": False,
                    "errors": validation_result["errors"],
                    "warnings": validation_result["warnings"],
                    "dataset_info": validation_result["dataset_info"],
                }
            ), 422

        clean_result = clean_dataset(load_result["data"], result["filename"])
        if not clean_result["success"]:
            return jsonify(
                {
                    "success": False,
                    "errors": clean_result["errors"],
                    "warnings": validation_result["warnings"] + clean_result["warnings"],
                    "dataset_info": validation_result["dataset_info"],
                }
            ), 422

        cleaned_dataset_info = {
            "rows": int(len(clean_result["data"])),
            "columns": int(len(clean_result["data"].columns)),
        }

        return jsonify(
            {
                "success": True,
                "message": "Dataset uploaded, validated, and cleaned successfully",
                "filename": result["filename"],
                "processed_file": clean_result["processed_file"],
                "dataset_info": cleaned_dataset_info,
                "warnings": validation_result["warnings"] + clean_result["warnings"],
            }
        ), 201

    except Exception as exc:
        return jsonify(
            {
                "success": False,
                "error": f"Upload failed: {exc}",
            }
        ), 500
