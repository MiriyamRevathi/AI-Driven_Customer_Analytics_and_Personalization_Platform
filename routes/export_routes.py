from flask import Blueprint, jsonify

from src.exporter import (
    export_to_excel,
    export_to_json,
    generate_export_summary,
    generate_full_export_payload,
)


export_bp = Blueprint("export", __name__)


@export_bp.route("/export/json", methods=["GET"])
def export_json_report():
    try:
        payload_result = generate_full_export_payload()
        if not payload_result["success"]:
            return jsonify(
                {
                    "success": False,
                    "error": payload_result["error"],
                }
            ), 422

        export_path = export_to_json(payload_result["payload"])
        return jsonify(
            {
                "success": True,
                "export": generate_export_summary(export_path),
            }
        ), 200

    except Exception as exc:
        return jsonify(
            {
                "success": False,
                "error": f"JSON export failed: {exc}",
            }
        ), 500


@export_bp.route("/export/excel", methods=["GET"])
def export_excel_report():
    try:
        payload_result = generate_full_export_payload()
        if not payload_result["success"]:
            return jsonify(
                {
                    "success": False,
                    "error": payload_result["error"],
                }
            ), 422

        export_path = export_to_excel(payload_result["payload"])
        return jsonify(
            {
                "success": True,
                "export": generate_export_summary(export_path),
            }
        ), 200

    except Exception as exc:
        return jsonify(
            {
                "success": False,
                "error": f"Excel export failed: {exc}",
            }
        ), 500
