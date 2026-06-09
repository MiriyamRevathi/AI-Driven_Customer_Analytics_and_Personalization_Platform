from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from config.settings import Config
from src.analytics import load_processed_dataset


SEGMENTATION_FEATURES = ["total_spending", "purchase_frequency", "age"]
SEGMENT_LABELS = ["Low Value", "Medium Value", "High Value"]


def load_latest_processed_dataset():
    """Load the newest cleaned dataset from the processed data folder."""
    processed_folder = Path(Config.PROCESSED_FOLDER)
    if not processed_folder.exists():
        return {
            "success": False,
            "data": None,
            "error": "Processed folder was not found.",
        }

    processed_files = [
        path
        for path in processed_folder.iterdir()
        if path.is_file() and path.suffix.lower() in {".xlsx", ".json"}
    ]
    if not processed_files:
        return {
            "success": False,
            "data": None,
            "error": "No processed dataset found. Upload and clean a dataset first.",
        }

    latest_file = max(processed_files, key=lambda path: path.stat().st_mtime)
    load_result = load_processed_dataset(latest_file)
    if not load_result["success"]:
        return load_result

    return {
        "success": True,
        "data": load_result["data"],
        "source_file": latest_file.name,
        "error": None,
    }


def prepare_segmentation_features(df):
    """Build a complete numeric feature matrix for KMeans."""
    missing_columns = [
        column for column in SEGMENTATION_FEATURES if column not in df.columns
    ]
    if missing_columns:
        return {
            "success": False,
            "features": None,
            "error": "Missing segmentation columns: " + ", ".join(missing_columns),
        }

    feature_df = df[SEGMENTATION_FEATURES].copy()
    for column in SEGMENTATION_FEATURES:
        feature_df[column] = pd.to_numeric(feature_df[column], errors="coerce")

    total_cells = int(feature_df.size)
    missing_cells = int(feature_df.isna().sum().sum())
    if total_cells == 0:
        return {
            "success": False,
            "features": None,
            "error": "No segmentation feature values are available.",
        }

    missing_ratio = missing_cells / total_cells
    if missing_ratio > 0.5:
        return {
            "success": False,
            "features": None,
            "error": "Too many missing numeric values for reliable segmentation.",
        }

    medians = feature_df.median(numeric_only=True)
    if medians.isna().any():
        return {
            "success": False,
            "features": None,
            "error": "Segmentation features do not contain enough numeric values.",
        }

    feature_df = feature_df.fillna(medians)

    return {
        "success": True,
        "features": feature_df,
        "error": None,
    }


def determine_cluster_count(df):
    """Use up to three clusters while rejecting tiny datasets."""
    row_count = int(len(df))
    if row_count < 3:
        return {
            "success": False,
            "cluster_count": None,
            "error": "At least 3 customers are required for segmentation.",
        }

    return {
        "success": True,
        "cluster_count": min(3, row_count),
        "error": None,
    }


def label_customer_segments(df):
    """Map KMeans cluster ids to business labels by average total spending."""
    cluster_spending = (
        df.groupby("cluster_id")["total_spending"]
        .mean()
        .sort_values()
    )
    label_map = {
        cluster_id: SEGMENT_LABELS[index]
        for index, cluster_id in enumerate(cluster_spending.index)
    }

    labeled_df = df.copy()
    labeled_df["segment"] = labeled_df["cluster_id"].map(label_map)
    return labeled_df


def generate_segmentation_summary(df):
    """Create dashboard-ready counts and average spending per segment."""
    summary = {}
    grouped = df.groupby("segment", sort=False)

    for segment_name, group in grouped:
        summary[str(segment_name)] = {
            "count": int(len(group)),
            "average_total_spending": round(float(group["total_spending"].mean()), 2),
            "average_purchase_frequency": round(
                float(group["purchase_frequency"].mean()),
                2,
            ),
        }

    return summary


def perform_customer_segmentation(df):
    """Run deterministic lightweight KMeans customer segmentation."""
    try:
        if df is None or df.empty:
            return {
                "success": False,
                "segments": [],
                "segment_summary": {},
                "error": "Cannot segment an empty dataset.",
            }

        cluster_result = determine_cluster_count(df)
        if not cluster_result["success"]:
            return {
                "success": False,
                "segments": [],
                "segment_summary": {},
                "error": cluster_result["error"],
            }

        feature_result = prepare_segmentation_features(df)
        if not feature_result["success"]:
            return {
                "success": False,
                "segments": [],
                "segment_summary": {},
                "error": feature_result["error"],
            }

        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_result["features"])

        kmeans = KMeans(
            n_clusters=cluster_result["cluster_count"],
            random_state=Config.RANDOM_STATE,
            n_init=10,
        )
        cluster_ids = kmeans.fit_predict(scaled_features)

        segmented_df = df.copy()
        for column in SEGMENTATION_FEATURES:
            segmented_df[column] = pd.to_numeric(
                segmented_df[column],
                errors="coerce",
            )
            segmented_df[column] = segmented_df[column].fillna(
                feature_result["features"][column]
            )

        segmented_df["cluster_id"] = cluster_ids
        segmented_df = label_customer_segments(segmented_df)

        output_columns = [
            "customer_id",
            "segment",
            "total_spending",
            "purchase_frequency",
            "age",
        ]
        segments = segmented_df[output_columns].to_dict(orient="records")
        for customer in segments:
            customer["total_spending"] = round(float(customer["total_spending"]), 2)
            customer["purchase_frequency"] = round(
                float(customer["purchase_frequency"]),
                2,
            )
            customer["age"] = round(float(customer["age"]), 2)

        return {
            "success": True,
            "segments": segments,
            "segment_summary": generate_segmentation_summary(segmented_df),
            "error": None,
        }

    except Exception as exc:
        return {
            "success": False,
            "segments": [],
            "segment_summary": {},
            "error": f"Customer segmentation failed: {exc}",
        }
