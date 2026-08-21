import pandas as pd

from src.config import HIGH_MISSING_PERCENTAGE_THRESHOLD


def validate_dataset(df: pd.DataFrame) -> dict:
    """
    Validate a dataset before profiling, cleaning, or modeling.
    """

    errors = []
    warnings = []

    if not isinstance(df, pd.DataFrame):
        errors.append("Input is not a pandas DataFrame.")
        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
        }

    if df.empty:
        errors.append("Dataset is empty.")

    if len(df.columns) == 0:
        errors.append("Dataset contains no columns.")

    # Duplicate column names
    duplicated_columns = df.columns[
        df.columns.duplicated()
    ].tolist()

    if duplicated_columns:
        errors.append(
            f"Duplicate column names found: "
            f"{duplicated_columns}"
        )

    # Completely empty columns
    #
    # NOTE: when a column name is duplicated, df[column]
    # returns a DataFrame (not a Series), and .isna().all()
    # on a DataFrame returns a Series, which crashes the `if`
    # check with "truth value of a Series is ambiguous". Skip
    # duplicate-named columns here — they're already reported
    # above, and this check only makes sense for a name that
    # points at exactly one column.
    empty_columns = [
        column
        for column in df.columns
        if column not in duplicated_columns
        and df[column].isna().all()
    ]

    if empty_columns:
        warnings.append(
            f"Completely empty columns: {empty_columns}"
        )

    # Very high missing percentage
    # (same duplicate-column caveat as above — df[column]
    # returns multiple columns when the name repeats, so skip
    # names already reported as duplicates)
    high_missing_columns = []

    for column in df.columns:

        if column in duplicated_columns:
            continue

        missing_percentage = (
            df[column].isna().mean() * 100
        )

        if missing_percentage >= HIGH_MISSING_PERCENTAGE_THRESHOLD:
            high_missing_columns.append(column)

    if high_missing_columns:
        warnings.append(
            "Columns with 50% or more missing values: "
            f"{high_missing_columns}"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }