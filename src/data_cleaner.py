from datetime import datetime
from pathlib import Path

import pandas as pd

from config.settings import Config


CATEGORICAL_COLUMNS = ["gender", "location", "preferred_category"]
NUMERIC_COLUMNS = ["age", "purchase_frequency", "total_spending"]


def standardize_column_names(df):
    """Normalize column names into the approved snake_case project format."""
    cleaned_df = df.copy()
    cleaned_df.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in cleaned_df.columns
    ]
    return cleaned_df


def clean_string_columns(df):
    """Trim and title-case customer text fields without changing schema."""
    cleaned_df = df.copy()

    for column in CATEGORICAL_COLUMNS:
        if column not in cleaned_df.columns:
            continue

        cleaned_df[column] = (
            cleaned_df[column]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
            .str.title()
        )

    if "customer_id" in cleaned_df.columns:
        cleaned_df["customer_id"] = (
            cleaned_df["customer_id"]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    return cleaned_df


def remove_duplicate_customers(df):
    """Remove duplicate customer_id rows and keep the first occurrence."""
    cleaned_df = df.copy()
    warnings = []

    if "customer_id" not in cleaned_df.columns:
        return cleaned_df, ["customer_id column is missing; duplicates could not be checked."]

    duplicate_count = int(cleaned_df["customer_id"].duplicated().sum())
    if duplicate_count > 0:
        cleaned_df = cleaned_df.drop_duplicates(subset="customer_id", keep="first")
        warnings.append(f"Removed {duplicate_count} duplicate customer row(s).")

    return cleaned_df, warnings


def handle_missing_values(df):
    """Apply conservative missing-value rules only."""
    cleaned_df = df.copy()
    warnings = []

    if "customer_id" in cleaned_df.columns:
        before_count = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(subset=["customer_id"])
        dropped_count = before_count - len(cleaned_df)
        if dropped_count > 0:
            warnings.append(f"Dropped {dropped_count} row(s) with missing customer_id.")

    for column in CATEGORICAL_COLUMNS:
        if column not in cleaned_df.columns:
            continue

        missing_count = int(cleaned_df[column].isna().sum())
        if missing_count > 0:
            cleaned_df[column] = cleaned_df[column].fillna("Unknown")
            warnings.append(f"Filled {missing_count} missing {column} value(s) with Unknown.")

    return cleaned_df, warnings


def validate_numeric_ranges(df):
    """Convert numeric columns safely and blank out values outside accepted ranges."""
    cleaned_df = df.copy()
    warnings = []

    for column in NUMERIC_COLUMNS:
        if column not in cleaned_df.columns:
            continue

        original_non_missing = cleaned_df[column].notna()
        cleaned_df[column] = pd.to_numeric(cleaned_df[column], errors="coerce")

        conversion_failures = int((original_non_missing & cleaned_df[column].isna()).sum())
        if conversion_failures > 0:
            warnings.append(
                f"Converted {conversion_failures} invalid {column} value(s) to missing."
            )

    if "age" in cleaned_df.columns:
        invalid_age = cleaned_df["age"].notna() & (
            (cleaned_df["age"] < 0) | (cleaned_df["age"] > 120)
        )
        invalid_count = int(invalid_age.sum())
        if invalid_count > 0:
            cleaned_df.loc[invalid_age, "age"] = pd.NA
            warnings.append(f"Converted {invalid_count} out-of-range age value(s) to missing.")

    if "purchase_frequency" in cleaned_df.columns:
        invalid_frequency = (
            cleaned_df["purchase_frequency"].notna()
            & (cleaned_df["purchase_frequency"] < 0)
        )
        invalid_count = int(invalid_frequency.sum())
        if invalid_count > 0:
            cleaned_df.loc[invalid_frequency, "purchase_frequency"] = pd.NA
            warnings.append(
                f"Converted {invalid_count} invalid purchase_frequency value(s) to missing."
            )

    if "total_spending" in cleaned_df.columns:
        invalid_spending = (
            cleaned_df["total_spending"].notna()
            & (cleaned_df["total_spending"] < 0)
        )
        invalid_count = int(invalid_spending.sum())
        if invalid_count > 0:
            cleaned_df.loc[invalid_spending, "total_spending"] = pd.NA
            warnings.append(
                f"Converted {invalid_count} invalid total_spending value(s) to missing."
            )

    return cleaned_df, warnings


def parse_purchase_dates(df):
    """Parse purchase dates safely; invalid dates become pandas NaT."""
    cleaned_df = df.copy()
    warnings = []

    if "last_purchase_date" not in cleaned_df.columns:
        return cleaned_df, warnings

    original_non_missing = cleaned_df["last_purchase_date"].notna()
    cleaned_df["last_purchase_date"] = pd.to_datetime(
        cleaned_df["last_purchase_date"],
        errors="coerce",
    )

    failed_count = int((original_non_missing & cleaned_df["last_purchase_date"].isna()).sum())
    if failed_count > 0:
        warnings.append(f"Converted {failed_count} invalid last_purchase_date value(s) to missing.")

    return cleaned_df, warnings


def save_cleaned_dataset(df, original_filename):
    """Save cleaned data into data/processed using a timestamped filename."""
    processed_folder = Path(Config.PROCESSED_FOLDER)
    processed_folder.mkdir(parents=True, exist_ok=True)

    original_path = Path(original_filename)
    extension = original_path.suffix.lower()
    if extension not in {".xlsx", ".json"}:
        extension = ".json"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    processed_filename = f"{original_path.stem}_cleaned_{timestamp}{extension}"
    processed_path = processed_folder / processed_filename

    if extension == ".xlsx":
        df.to_excel(processed_path, index=False)
    else:
        df.to_json(processed_path, orient="records", indent=2, date_format="iso")

    return str(processed_path)


def clean_dataset(df, original_filename):
    """
    Clean validated customer data and persist the processed result.

    This function returns structured output for the upload route. It does not
    calculate analytics or ML features.
    """
    try:
        if df is None:
            return {
                "success": False,
                "data": None,
                "processed_file": None,
                "warnings": [],
                "errors": ["Cannot clean an unloaded dataset."],
            }

        cleaned_df = standardize_column_names(df)
        cleaned_df = clean_string_columns(cleaned_df)

        duplicate_warnings = []
        cleaned_df, duplicate_warnings = remove_duplicate_customers(cleaned_df)

        missing_warnings = []
        cleaned_df, missing_warnings = handle_missing_values(cleaned_df)

        numeric_warnings = []
        cleaned_df, numeric_warnings = validate_numeric_ranges(cleaned_df)

        date_warnings = []
        cleaned_df, date_warnings = parse_purchase_dates(cleaned_df)

        warnings = (
            duplicate_warnings
            + missing_warnings
            + numeric_warnings
            + date_warnings
        )

        if cleaned_df.empty:
            return {
                "success": False,
                "data": None,
                "processed_file": None,
                "warnings": warnings,
                "errors": ["No rows remain after cleaning."],
            }

        processed_file = save_cleaned_dataset(cleaned_df, original_filename)

        return {
            "success": True,
            "data": cleaned_df,
            "processed_file": processed_file,
            "warnings": warnings,
            "errors": [],
        }

    except Exception as exc:
        return {
            "success": False,
            "data": None,
            "processed_file": None,
            "warnings": [],
            "errors": [f"Data cleaning failed: {exc}"],
        }
