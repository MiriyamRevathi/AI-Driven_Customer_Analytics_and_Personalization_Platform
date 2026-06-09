REQUIRED_COLUMNS = [
    "customer_id",
    "age",
    "gender",
    "location",
    "purchase_frequency",
    "total_spending",
    "preferred_category",
    "last_purchase_date",
]


def validate_empty_dataset(df):
    """Return validation errors when the loaded DataFrame has no usable rows."""
    if df is None:
        return ["Dataset could not be loaded."]

    if df.empty:
        return ["Dataset is empty."]

    return []


def validate_required_columns(df):
    """Check the fixed academic customer schema without changing the DataFrame."""
    existing_columns = set(df.columns)
    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in existing_columns
    ]

    if missing_columns:
        return [
            "Missing required columns: " + ", ".join(missing_columns)
        ]

    return []


def validate_duplicate_customers(df):
    """Warn when customer_id repeats, but do not fail validation."""
    if "customer_id" not in df.columns:
        return []

    duplicate_count = int(df["customer_id"].duplicated().sum())
    if duplicate_count == 0:
        return []

    return [
        f"Found {duplicate_count} duplicate customer_id value(s). They will need cleaning before analysis."
    ]


def validate_dataset(df):
    """
    Run lightweight structural validation only.

    Validation deliberately does not clean, rename, type-cast, or mutate data.
    """
    errors = []
    warnings = []

    if df is None:
        return {
            "success": False,
            "errors": ["Dataset could not be loaded."],
            "warnings": [],
            "dataset_info": {
                "rows": 0,
                "columns": 0,
            },
        }

    dataset_info = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
    }

    errors.extend(validate_empty_dataset(df))
    if not errors:
        errors.extend(validate_required_columns(df))
        warnings.extend(validate_duplicate_customers(df))

    return {
        "success": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "dataset_info": dataset_info,
    }
