import pandas as pd

from src.prediction import (
    load_latest_processed_dataset as load_latest_prediction_dataset,
)
from src.prediction import train_prediction_model
from src.segmentation import perform_customer_segmentation


def load_latest_processed_dataset():
    """Load the newest cleaned dataset for recommendation generation."""
    return load_latest_prediction_dataset()


def load_segmentation_results(df=None):
    """Generate current segmentation results from the cleaned dataset."""
    if df is None:
        load_result = load_latest_processed_dataset()
        if not load_result["success"]:
            return load_result
        df = load_result["data"]

    segmentation_result = perform_customer_segmentation(df)
    if not segmentation_result["success"]:
        return {
            "success": False,
            "segments": [],
            "error": segmentation_result["error"],
        }

    return {
        "success": True,
        "segments": segmentation_result["segments"],
        "error": None,
    }


def load_prediction_results(df=None):
    """Generate current purchase prediction results from the cleaned dataset."""
    if df is None:
        load_result = load_latest_processed_dataset()
        if not load_result["success"]:
            return load_result
        df = load_result["data"]

    prediction_result = train_prediction_model(df)
    if not prediction_result["success"]:
        return {
            "success": False,
            "predictions": [],
            "error": prediction_result["error"],
        }

    return {
        "success": True,
        "predictions": prediction_result["predictions"],
        "error": None,
    }


def _select_recommendation(customer):
    """Apply deterministic business rules in priority order."""
    segment = customer.get("segment", "Unknown")
    predicted_purchase = int(customer.get("predicted_purchase", 0))
    probability = float(customer.get("prediction_probability", 0.0))
    purchase_frequency = float(customer.get("purchase_frequency", 0.0))
    preferred_category = customer.get("preferred_category") or "General"

    if segment == "High Value" and predicted_purchase == 1:
        return {
            "recommendation": "Premium loyalty campaign",
            "recommended_category": preferred_category,
            "priority": "High",
        }

    if purchase_frequency <= 1:
        return {
            "recommendation": "Customer retention outreach",
            "recommended_category": preferred_category,
            "priority": "High",
        }

    if segment == "Low Value" and predicted_purchase == 0:
        return {
            "recommendation": "Discount re-engagement campaign",
            "recommended_category": preferred_category,
            "priority": "Medium",
        }

    if segment == "Medium Value" and preferred_category == "Electronics":
        return {
            "recommendation": "Electronics upsell campaign",
            "recommended_category": "Electronics",
            "priority": "Medium",
        }

    if probability >= 0.7:
        return {
            "recommendation": "Personalized targeted marketing",
            "recommended_category": preferred_category,
            "priority": "Medium",
        }

    return {
        "recommendation": "General engagement campaign",
        "recommended_category": preferred_category,
        "priority": "Low",
    }


def generate_customer_recommendations(df):
    """Combine processed data, segmentation, and prediction into recommendations."""
    try:
        if df is None or df.empty:
            return {
                "success": False,
                "customers": [],
                "summary": {},
                "error": "Cannot generate recommendations for an empty dataset.",
            }

        segmentation_result = load_segmentation_results(df)
        if not segmentation_result["success"]:
            return {
                "success": False,
                "customers": [],
                "summary": {},
                "error": segmentation_result["error"],
            }

        prediction_result = load_prediction_results(df)
        if not prediction_result["success"]:
            return {
                "success": False,
                "customers": [],
                "summary": {},
                "error": prediction_result["error"],
            }

        base_columns = [
            "customer_id",
            "preferred_category",
            "purchase_frequency",
            "total_spending",
        ]
        customer_df = df[[column for column in base_columns if column in df.columns]].copy()
        customer_df["customer_id"] = customer_df["customer_id"].astype(str)

        segment_df = pd.DataFrame(segmentation_result["segments"])
        prediction_df = pd.DataFrame(prediction_result["predictions"])

        segment_df["customer_id"] = segment_df["customer_id"].astype(str)
        prediction_df["customer_id"] = prediction_df["customer_id"].astype(str)

        merged_df = (
            customer_df
            .merge(segment_df[["customer_id", "segment"]], on="customer_id", how="left")
            .merge(prediction_df, on="customer_id", how="left")
        )

        recommendations = []
        for record in merged_df.to_dict(orient="records"):
            predicted_label = record.get("predicted_purchase", "No")
            predicted_purchase = 1 if predicted_label == "Yes" else 0

            customer = {
                "segment": record.get("segment", "Unknown"),
                "predicted_purchase": predicted_purchase,
                "prediction_probability": record.get("prediction_probability", 0.0),
                "purchase_frequency": record.get("purchase_frequency", 0.0),
                "preferred_category": record.get("preferred_category", "General"),
            }
            selected = _select_recommendation(customer)

            recommendations.append(
                {
                    "customer_id": str(record.get("customer_id")),
                    "segment": customer["segment"],
                    "predicted_purchase": predicted_purchase,
                    "prediction_probability": round(
                        float(customer["prediction_probability"] or 0.0),
                        3,
                    ),
                    "recommendation": selected["recommendation"],
                    "recommended_category": selected["recommended_category"],
                    "priority": selected["priority"],
                }
            )

        return {
            "success": True,
            "customers": recommendations,
            "summary": generate_recommendation_summary(recommendations),
            "error": None,
        }

    except Exception as exc:
        return {
            "success": False,
            "customers": [],
            "summary": {},
            "error": f"Recommendation generation failed: {exc}",
        }


def generate_recommendation_summary(results):
    """Summarize recommendation priority and campaign distribution."""
    priority_counts = {"High": 0, "Medium": 0, "Low": 0}
    campaign_distribution = {}
    category_distribution = {}

    for result in results:
        priority = result.get("priority", "Low")
        recommendation = result.get("recommendation", "Unknown")
        category = result.get("recommended_category", "General")

        priority_counts[priority] = priority_counts.get(priority, 0) + 1
        campaign_distribution[recommendation] = (
            campaign_distribution.get(recommendation, 0) + 1
        )
        category_distribution[category] = category_distribution.get(category, 0) + 1

    return {
        "total_recommendations": int(len(results)),
        "high_priority_customers": int(priority_counts.get("High", 0)),
        "medium_priority_customers": int(priority_counts.get("Medium", 0)),
        "low_priority_customers": int(priority_counts.get("Low", 0)),
        "campaign_distribution": campaign_distribution,
        "category_recommendation_distribution": category_distribution,
    }
