from pathlib import Path

import pandas as pd


def load_processed_dataset(file_path):
    """Load a cleaned dataset saved by the preprocessing subsystem."""
    try:
        path = Path(file_path)
        if not path.exists():
            return {
                "success": False,
                "data": None,
                "error": "Processed dataset file was not found.",
            }

        if path.suffix.lower() == ".xlsx":
            dataframe = pd.read_excel(path)
        elif path.suffix.lower() == ".json":
            dataframe = pd.read_json(path)
        else:
            return {
                "success": False,
                "data": None,
                "error": "Unsupported processed file format.",
            }

        if dataframe.empty:
            return {
                "success": False,
                "data": None,
                "error": "Processed dataset is empty.",
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
            "error": f"Processed dataset is unreadable or corrupted: {exc}",
        }
    except Exception as exc:
        return {
            "success": False,
            "data": None,
            "error": f"Unable to load processed dataset: {exc}",
        }


def generate_basic_statistics(df):
    """Generate high-level dashboard metrics with safe numeric handling."""
    total_customers = int(df["customer_id"].nunique()) if "customer_id" in df.columns else int(len(df))

    spending = (
        pd.to_numeric(df["total_spending"], errors="coerce")
        if "total_spending" in df.columns
        else pd.Series(dtype="float64")
    )
    frequency = (
        pd.to_numeric(df["purchase_frequency"], errors="coerce")
        if "purchase_frequency" in df.columns
        else pd.Series(dtype="float64")
    )

    return {
        "total_customers": total_customers,
        "total_spending": round(float(spending.sum(skipna=True)), 2),
        "average_spending": round(float(spending.mean(skipna=True)), 2) if not spending.dropna().empty else 0.0,
        "average_purchase_frequency": round(float(frequency.mean(skipna=True)), 2)
        if not frequency.dropna().empty
        else 0.0,
    }


def generate_category_distribution(df):
    """Return count of customers by preferred product category."""
    if "preferred_category" not in df.columns:
        return {}

    return {
        str(category): int(count)
        for category, count in df["preferred_category"].fillna("Unknown").value_counts().items()
    }


def generate_location_distribution(df):
    """Return count of customers by location."""
    if "location" not in df.columns:
        return {}

    return {
        str(location): int(count)
        for location, count in df["location"].fillna("Unknown").value_counts().items()
    }


def generate_top_customers(df):
    """Return the top five customers ranked by total spending."""
    required_columns = {"customer_id", "total_spending"}
    if not required_columns.issubset(df.columns):
        return []

    working_df = df.copy()
    working_df["total_spending"] = pd.to_numeric(
        working_df["total_spending"],
        errors="coerce",
    ).fillna(0)

    display_columns = [
        column
        for column in [
            "customer_id",
            "total_spending",
            "purchase_frequency",
            "preferred_category",
            "location",
        ]
        if column in working_df.columns
    ]

    top_customers = working_df.sort_values(
        by="total_spending",
        ascending=False,
    ).head(5)

    records = top_customers[display_columns].to_dict(orient="records")
    for record in records:
        if "total_spending" in record:
            record["total_spending"] = round(float(record["total_spending"]), 2)
        if "purchase_frequency" in record:
            if pd.isna(record["purchase_frequency"]):
                record["purchase_frequency"] = None
            else:
                record["purchase_frequency"] = int(record["purchase_frequency"])

    return records


def generate_missing_value_summary(df):
    """Return missing value counts for each processed dataset column."""
    return {
        str(column): int(missing_count)
        for column, missing_count in df.isna().sum().items()
    }


def generate_analytics_summary(df):
    """Build one dashboard-ready analytics payload."""
    try:
        if df is None or df.empty:
            return {
                "success": False,
                "analytics": None,
                "error": "Cannot generate analytics for an empty dataset.",
            }

        return {
            "success": True,
            "analytics": {
                "basic_statistics": generate_basic_statistics(df),
                "category_distribution": generate_category_distribution(df),
                "location_distribution": generate_location_distribution(df),
                "top_customers": generate_top_customers(df),
                "missing_values": generate_missing_value_summary(df),
            },
            "error": None,
        }

    except Exception as exc:
        return {
            "success": False,
            "analytics": None,
            "error": f"Analytics generation failed: {exc}",
        }
