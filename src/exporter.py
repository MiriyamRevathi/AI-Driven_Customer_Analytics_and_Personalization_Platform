from datetime import datetime
import json
from pathlib import Path

import pandas as pd

from config.settings import Config
from src.analytics import generate_analytics_summary
from src.prediction import (
    load_latest_processed_dataset as load_latest_prediction_dataset,
)
from src.prediction import train_prediction_model
from src.recommendation import generate_customer_recommendations
from src.segmentation import perform_customer_segmentation


def load_latest_processed_dataset():
    """Load the newest cleaned dataset for report generation."""
    return load_latest_prediction_dataset()


def generate_full_export_payload():
    """Generate analytics, segmentation, prediction, and recommendation output."""
    load_result = load_latest_processed_dataset()
    if not load_result["success"]:
        return {
            "success": False,
            "payload": None,
            "error": load_result["error"],
        }

    df = load_result["data"]

    analytics_result = generate_analytics_summary(df)
    if not analytics_result["success"]:
        return {
            "success": False,
            "payload": None,
            "error": analytics_result["error"],
        }

    segmentation_result = perform_customer_segmentation(df)
    if not segmentation_result["success"]:
        return {
            "success": False,
            "payload": None,
            "error": segmentation_result["error"],
        }

    prediction_result = train_prediction_model(df)
    if not prediction_result["success"]:
        return {
            "success": False,
            "payload": None,
            "error": prediction_result["error"],
        }

    recommendation_result = generate_customer_recommendations(df)
    if not recommendation_result["success"]:
        return {
            "success": False,
            "payload": None,
            "error": recommendation_result["error"],
        }

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "generated_at": generated_at,
        "source_file": load_result.get("source_file"),
        "analytics": analytics_result["analytics"],
        "segments": [
            {
                "customer_id": row["customer_id"],
                "segment": row["segment"],
            }
            for row in segmentation_result["segments"]
        ],
        "predictions": [
            {
                "customer_id": row["customer_id"],
                "predicted_purchase": row["predicted_purchase"],
                "prediction_probability": row["prediction_probability"],
            }
            for row in prediction_result["predictions"]
        ],
        "recommendations": [
            {
                "customer_id": row["customer_id"],
                "recommendation": row["recommendation"],
                "recommended_category": row["recommended_category"],
                "priority": row["priority"],
            }
            for row in recommendation_result["customers"]
        ],
    }

    return {
        "success": True,
        "payload": payload,
        "error": None,
    }


def _ensure_export_folder():
    export_folder = Path(Config.EXPORT_FOLDER)
    export_folder.mkdir(parents=True, exist_ok=True)
    return export_folder


def export_to_json(payload):
    """Save the complete report payload as JSON."""
    export_folder = _ensure_export_folder()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = export_folder / f"customer_report_{timestamp}.json"

    with export_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    return str(export_path)


def _analytics_rows(analytics):
    """Flatten analytics sections into rows for the Excel Analytics sheet."""
    rows = []

    for metric, value in analytics.get("basic_statistics", {}).items():
        rows.append({"section": "basic_statistics", "name": metric, "value": value})

    for category, count in analytics.get("category_distribution", {}).items():
        rows.append({"section": "category_distribution", "name": category, "value": count})

    for location, count in analytics.get("location_distribution", {}).items():
        rows.append({"section": "location_distribution", "name": location, "value": count})

    for column, count in analytics.get("missing_values", {}).items():
        rows.append({"section": "missing_values", "name": column, "value": count})

    for customer in analytics.get("top_customers", []):
        rows.append(
            {
                "section": "top_customers",
                "name": customer.get("customer_id"),
                "value": customer.get("total_spending"),
            }
        )

    return rows


def export_to_excel(payload):
    """Save the complete report payload as an Excel workbook."""
    export_folder = _ensure_export_folder()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = export_folder / f"customer_report_{timestamp}.xlsx"

    analytics_df = pd.DataFrame(_analytics_rows(payload.get("analytics", {})))
    segments_df = pd.DataFrame(payload.get("segments", []))
    predictions_df = pd.DataFrame(payload.get("predictions", []))
    recommendations_df = pd.DataFrame(payload.get("recommendations", []))

    with pd.ExcelWriter(export_path, engine="openpyxl") as writer:
        analytics_df.to_excel(writer, sheet_name="Analytics", index=False)
        segments_df.to_excel(writer, sheet_name="Segments", index=False)
        predictions_df.to_excel(writer, sheet_name="Predictions", index=False)
        recommendations_df.to_excel(writer, sheet_name="Recommendations", index=False)

    return str(export_path)


def generate_export_summary(export_path):
    """Return route-friendly metadata for a generated export file."""
    path = Path(export_path)
    export_type = "excel" if path.suffix.lower() == ".xlsx" else "json"

    return {
        "type": export_type,
        "path": str(path),
        "filename": path.name,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
