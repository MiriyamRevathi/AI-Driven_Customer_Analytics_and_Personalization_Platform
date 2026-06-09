from pathlib import Path

from flask import Blueprint, jsonify, render_template

from config.settings import Config
from src.analytics import generate_analytics_summary, load_processed_dataset
from src.prediction import (
    load_latest_processed_dataset as load_latest_prediction_dataset,
)
from src.prediction import train_prediction_model
from src.recommendation import (
    generate_customer_recommendations,
    load_latest_processed_dataset as load_latest_recommendation_dataset,
)
from src.segmentation import load_latest_processed_dataset, perform_customer_segmentation


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard", methods=["GET"])
def dashboard_page():
    return render_template("dashboard.html")


def _get_latest_processed_file():
    """Find the newest cleaned dataset produced by the upload pipeline."""
    processed_folder = Path(Config.PROCESSED_FOLDER)
    if not processed_folder.exists():
        return None

    processed_files = [
        path
        for path in processed_folder.iterdir()
        if path.is_file() and path.suffix.lower() in {".xlsx", ".json"}
    ]
    if not processed_files:
        return None

    return max(processed_files, key=lambda path: path.stat().st_mtime)


@dashboard_bp.route("/analyze", methods=["GET"])
def analyze_dataset():
    try:
        latest_file = _get_latest_processed_file()
        if latest_file is None:
            return jsonify(
                {
                    "success": False,
                    "error": "No processed dataset found. Upload and clean a dataset first.",
                }
            ), 404

        load_result = load_processed_dataset(latest_file)
        if not load_result["success"]:
            return jsonify(
                {
                    "success": False,
                    "error": load_result["error"],
                }
            ), 422

        analytics_result = generate_analytics_summary(load_result["data"])
        if not analytics_result["success"]:
            return jsonify(
                {
                    "success": False,
                    "error": analytics_result["error"],
                }
            ), 422

        return jsonify(
            {
                "success": True,
                "source_file": latest_file.name,
                "analytics": analytics_result["analytics"],
            }
        ), 200

    except Exception as exc:
        return jsonify(
            {
                "success": False,
                "error": f"Analytics request failed: {exc}",
            }
        ), 500


@dashboard_bp.route("/segment", methods=["GET"])
def segment_customers():
    try:
        load_result = load_latest_processed_dataset()
        if not load_result["success"]:
            return jsonify(
                {
                    "success": False,
                    "error": load_result["error"],
                }
            ), 404

        segmentation_result = perform_customer_segmentation(load_result["data"])
        if not segmentation_result["success"]:
            return jsonify(
                {
                    "success": False,
                    "error": segmentation_result["error"],
                }
            ), 422

        return jsonify(
            {
                "success": True,
                "source_file": load_result.get("source_file"),
                "segmentation": {
                    "segments": segmentation_result["segments"],
                    "summary": segmentation_result["segment_summary"],
                },
            }
        ), 200

    except Exception as exc:
        return jsonify(
            {
                "success": False,
                "error": f"Segmentation request failed: {exc}",
            }
        ), 500


@dashboard_bp.route("/predict", methods=["GET"])
def predict_purchase():
    try:
        load_result = load_latest_prediction_dataset()
        if not load_result["success"]:
            return jsonify(
                {
                    "success": False,
                    "error": load_result["error"],
                }
            ), 404

        prediction_result = train_prediction_model(load_result["data"])
        if not prediction_result["success"]:
            return jsonify(
                {
                    "success": False,
                    "error": prediction_result["error"],
                }
            ), 422

        return jsonify(
            {
                "success": True,
                "source_file": load_result.get("source_file"),
                "prediction": {
                    "metrics": prediction_result["metrics"],
                    "summary": prediction_result["summary"],
                    "predictions": prediction_result["predictions"],
                },
            }
        ), 200

    except Exception as exc:
        return jsonify(
            {
                "success": False,
                "error": f"Prediction request failed: {exc}",
            }
        ), 500


@dashboard_bp.route("/recommend", methods=["GET"])
def recommend_customers():
    try:
        load_result = load_latest_recommendation_dataset()
        if not load_result["success"]:
            return jsonify(
                {
                    "success": False,
                    "error": load_result["error"],
                }
            ), 404

        recommendation_result = generate_customer_recommendations(load_result["data"])
        if not recommendation_result["success"]:
            return jsonify(
                {
                    "success": False,
                    "error": recommendation_result["error"],
                }
            ), 422

        return jsonify(
            {
                "success": True,
                "source_file": load_result.get("source_file"),
                "recommendations": {
                    "summary": recommendation_result["summary"],
                    "customers": recommendation_result["customers"],
                },
            }
        ), 200

    except Exception as exc:
        return jsonify(
            {
                "success": False,
                "error": f"Recommendation request failed: {exc}",
            }
        ), 500
