from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from config.settings import Config
from src.analytics import load_processed_dataset


PREDICTION_FEATURES = ["age", "purchase_frequency", "total_spending"]
TARGET_COLUMN = "will_purchase_next_month"


def load_latest_processed_dataset():
    """Load the newest cleaned dataset from the processed data folder."""
    processed_folder = Path(Config.PROCESSED_FOLDER)
    if not processed_folder.exists():
        return {
            "success": False,
            "data": None,
            "source_file": None,
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
            "source_file": None,
            "error": "No processed dataset found. Upload and clean a dataset first.",
        }

    latest_file = max(processed_files, key=lambda path: path.stat().st_mtime)
    load_result = load_processed_dataset(latest_file)
    if not load_result["success"]:
        return {
            "success": False,
            "data": None,
            "source_file": latest_file.name,
            "error": load_result["error"],
        }

    return {
        "success": True,
        "data": load_result["data"],
        "source_file": latest_file.name,
        "error": None,
    }


def create_prediction_target(df):
    """
    Create or normalize the will_purchase_next_month target.

    If the dataset has no explicit target, this academic heuristic marks
    customers as likely buyers when they are frequent, valuable, and recent.
    """
    working_df = df.copy()

    if TARGET_COLUMN in working_df.columns:
        target = pd.to_numeric(working_df[TARGET_COLUMN], errors="coerce")
        working_df[TARGET_COLUMN] = target.fillna(0).astype(int).clip(0, 1)
        return {
            "success": True,
            "data": working_df,
            "error": None,
        }

    required_columns = ["purchase_frequency", "total_spending", "last_purchase_date"]
    missing_columns = [
        column for column in required_columns if column not in working_df.columns
    ]
    if missing_columns:
        return {
            "success": False,
            "data": None,
            "error": "Missing target creation columns: " + ", ".join(missing_columns),
        }

    frequency = pd.to_numeric(working_df["purchase_frequency"], errors="coerce")
    spending = pd.to_numeric(working_df["total_spending"], errors="coerce")
    purchase_dates = pd.to_datetime(
        working_df["last_purchase_date"],
        errors="coerce",
    )

    if frequency.dropna().empty or spending.dropna().empty or purchase_dates.dropna().empty:
        return {
            "success": False,
            "data": None,
            "error": "Not enough valid values to create prediction target.",
        }

    frequency_threshold = frequency.median()
    spending_threshold = spending.median()
    latest_purchase_date = purchase_dates.max()
    recency_days = (latest_purchase_date - purchase_dates).dt.days
    recency_threshold = recency_days.dropna().median()

    working_df[TARGET_COLUMN] = (
        (frequency >= frequency_threshold)
        & (spending >= spending_threshold)
        & (recency_days <= recency_threshold)
    ).astype(int)

    return {
        "success": True,
        "data": working_df,
        "error": None,
    }


def prepare_prediction_features(df):
    """Prepare safe numeric prediction features with median filling."""
    missing_columns = [
        column for column in PREDICTION_FEATURES if column not in df.columns
    ]
    if missing_columns:
        return {
            "success": False,
            "features": None,
            "error": "Missing prediction feature columns: " + ", ".join(missing_columns),
        }

    feature_df = df[PREDICTION_FEATURES].copy()
    for column in PREDICTION_FEATURES:
        feature_df[column] = pd.to_numeric(feature_df[column], errors="coerce")

    total_cells = int(feature_df.size)
    missing_cells = int(feature_df.isna().sum().sum())
    if total_cells == 0 or missing_cells / total_cells > 0.5:
        return {
            "success": False,
            "features": None,
            "error": "Too many missing feature values for prediction.",
        }

    medians = feature_df.median(numeric_only=True)
    if medians.isna().any():
        return {
            "success": False,
            "features": None,
            "error": "Prediction features do not contain enough numeric values.",
        }

    return {
        "success": True,
        "features": feature_df.fillna(medians),
        "error": None,
    }


def evaluate_prediction_model(model, X_test, y_test):
    """Return rounded classification metrics for the held-out test split."""
    predictions = model.predict(X_test)

    return {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 3),
        "precision": round(
            float(precision_score(y_test, predictions, zero_division=0)),
            3,
        ),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 3),
        "f1_score": round(float(f1_score(y_test, predictions, zero_division=0)), 3),
    }


def generate_customer_predictions(model, X):
    """Generate class labels and probabilities for every customer row."""
    labels = model.predict(X)

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X)[:, 1]
    else:
        probabilities = labels

    return [
        {
            "predicted_purchase": "Yes" if int(label) == 1 else "No",
            "prediction_probability": round(float(probability), 3),
        }
        for label, probability in zip(labels, probabilities)
    ]


def generate_prediction_summary(results):
    """Create simple aggregate counts for dashboard use."""
    yes_count = sum(1 for result in results if result["predicted_purchase"] == "Yes")
    no_count = len(results) - yes_count

    return {
        "total_predictions": int(len(results)),
        "likely_to_purchase": int(yes_count),
        "unlikely_to_purchase": int(no_count),
    }


def train_prediction_model(df):
    """Train a deterministic lightweight purchase prediction model."""
    try:
        if df is None or df.empty:
            return {
                "success": False,
                "metrics": {},
                "predictions": [],
                "summary": {},
                "error": "Cannot train prediction model on an empty dataset.",
            }

        if len(df) < 6:
            return {
                "success": False,
                "metrics": {},
                "predictions": [],
                "summary": {},
                "error": "At least 6 customers are required for purchase prediction.",
            }

        target_result = create_prediction_target(df)
        if not target_result["success"]:
            return {
                "success": False,
                "metrics": {},
                "predictions": [],
                "summary": {},
                "error": target_result["error"],
            }

        working_df = target_result["data"]
        feature_result = prepare_prediction_features(working_df)
        if not feature_result["success"]:
            return {
                "success": False,
                "metrics": {},
                "predictions": [],
                "summary": {},
                "error": feature_result["error"],
            }

        X = feature_result["features"]
        y = working_df[TARGET_COLUMN].astype(int)

        if y.nunique() < 2:
            return {
                "success": False,
                "metrics": {},
                "predictions": [],
                "summary": {},
                "error": "Prediction target has only one class; model training requires both purchase and non-purchase examples.",
            }

        class_counts = y.value_counts()
        stratify = y if class_counts.min() >= 2 else None

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.3,
            random_state=Config.RANDOM_STATE,
            stratify=stratify,
        )

        model = DecisionTreeClassifier(
            max_depth=3,
            random_state=Config.RANDOM_STATE,
        )
        model.fit(X_train, y_train)

        metrics = evaluate_prediction_model(model, X_test, y_test)
        prediction_rows = generate_customer_predictions(model, X)

        predictions = []
        for customer_id, row in zip(working_df["customer_id"], prediction_rows):
            predictions.append(
                {
                    "customer_id": str(customer_id),
                    "predicted_purchase": row["predicted_purchase"],
                    "prediction_probability": row["prediction_probability"],
                }
            )

        return {
            "success": True,
            "metrics": metrics,
            "predictions": predictions,
            "summary": generate_prediction_summary(predictions),
            "error": None,
        }

    except Exception as exc:
        return {
            "success": False,
            "metrics": {},
            "predictions": [],
            "summary": {},
            "error": f"Purchase prediction failed: {exc}",
        }
