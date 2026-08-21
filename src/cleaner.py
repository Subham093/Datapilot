import re

import numpy as np
import pandas as pd

from src.config import (
    IDENTIFIER_UNIQUE_RATIO_THRESHOLD,
    IQR_MULTIPLIER,
    KNOWN_MEASUREMENT_COLUMN_NAMES,
    MAX_OUTLIER_RATIO_FOR_AUTO_CORRECTION,
    MIN_ROWS_FOR_IDENTIFIER_DETECTION,
    MIN_VALID_VALUES_FOR_OUTLIER_DETECTION,
    NUMERIC_PARSE_SUCCESS_RATIO,
)

# pandas' nullable Int64 dtype is a real 64-bit integer under
# the hood, so a value that's mathematically whole (passes a
# "% 1 == 0" check) can still be far too large to fit —
# something like 1e308 from a corrupted row. Anything outside
# this range gets kept as float instead of crashing the cast.
INT64_SAFE_MIN = -9_223_372_036_854_775_808
INT64_SAFE_MAX = 9_223_372_036_854_775_807


# SHARED SCHEMA

# Every audit-log entry uses exactly these five fields.
# This is the ONLY cleaning engine in the project — the
# dashboard no longer keeps a second, independent copy of
# this logic.
#
#   category : str   e.g. "Missing Values", "Outlier Correction"
#   column   : str   affected column name, or "All columns"
#   action   : str   short label, e.g. "Filled with median"
#   count    : int   how many values/rows were affected
#   reason   : str   plain-language explanation


def _log(audit_log, category, column, action, count, reason):
    audit_log.append(
        {
            "category": category,
            "column": str(column),
            "action": action,
            "count": int(count),
            "reason": reason,
        }
    )


# HELPER: DOES A COLUMN LOOK NUMERIC?

def _looks_numeric_series(series: pd.Series) -> bool:
    """
    A column is treated as numeric when pandas already
    thinks so, or when at least 80% of its non-null values
    can be parsed as numbers (handles numeric columns that
    were loaded as strings, e.g. "20", "21.5").
    """

    if pd.api.types.is_numeric_dtype(series):
        return True

    non_null = series.dropna()

    if len(non_null) == 0:
        return False

    converted = pd.to_numeric(non_null, errors="coerce")

    return converted.notna().mean() >= NUMERIC_PARSE_SUCCESS_RATIO


# HELPER: IDENTIFIER PROTECTION

def _is_likely_identifier_column(series: pd.Series, column) -> bool:
    """
    ID-like columns (customer_id, transaction_id, ...) must
    never have their values replaced by a median — doing so
    would corrupt a join key or primary key.

    Two-part check, in order:

    1. Column NAME strongly suggests an identifier
       (ends in "id", "identifier", "serial", "uuid").

    2. Otherwise, fall back to a uniqueness-ratio check —
       but ONLY on datasets with enough rows for that ratio
       to be statistically meaningful. On a small dataset
       (say, 11 rows), it's completely normal for a genuine
       measurement column like "age" to have every single
       value be different by pure chance (100% unique) —
       that is NOT evidence it's an identifier. Requiring a
       reasonably large row count before trusting the ratio
       avoids exactly this false positive.

       As a second safety net, known measurement-style column
       names are never classified as identifiers by ratio
       alone, even on larger datasets, since a wide numeric
       range (e.g. income, price) can also look "mostly
       unique" without being an ID.
    """

    column_name = str(column).strip().lower()

    identifier_suffixes = ("id", "_id", "identifier", "serial", "uuid")

    if column_name in identifier_suffixes or column_name.endswith(
        identifier_suffixes
    ):
        return True

    if column_name in KNOWN_MEASUREMENT_COLUMN_NAMES:
        return False

    non_null = series.dropna()

    if len(non_null) < MIN_ROWS_FOR_IDENTIFIER_DETECTION:
        return False

    return (non_null.nunique() / len(non_null)) >= IDENTIFIER_UNIQUE_RATIO_THRESHOLD


# HELPER: RESTORE A SENSIBLE NUMERIC DTYPE

def _restore_numeric_dtype(dataframe: pd.DataFrame, column) -> None:
    """
    If every non-null value is a whole number that actually
    fits in a 64-bit integer, store as the pandas nullable
    Int64 dtype. Otherwise keep float.

    This avoids two different crashes:
    - "invalid value 29.5 for dtype int64" (a genuinely
      fractional value slipping through — handled by the
      whole-number check).
    - "cannot safely cast non-equivalent float64 to int64"
      (a value that IS mathematically a whole number, but is
      astronomically large — e.g. 1e308 from a bad row — and
      overflows what Int64 can actually represent). A whole-
      number check alone isn't enough; the value also has to
      be finite and in-range.
    """

    numeric = pd.to_numeric(dataframe[column], errors="coerce")
    non_null = numeric.dropna()

    if non_null.empty:
        dataframe[column] = numeric
        return

    looks_whole = (
        np.isfinite(non_null).all()
        and np.isclose(non_null % 1, 0).all()
        and (non_null >= INT64_SAFE_MIN).all()
        and (non_null <= INT64_SAFE_MAX).all()
    )

    if looks_whole:
        dataframe[column] = numeric.round().astype("Int64")
    else:
        dataframe[column] = numeric.astype(float)


# STEP: NUMERIC ANOMALY + OUTLIER CORRECTION

def _correct_numeric_column(
    cleaned_df: pd.DataFrame,
    column,
    audit_log: list,
) -> None:
    """
    1. Convert numeric-looking values safely.
    2. Replace any value that fails to parse as a number
       with the column median.
    3. Skip identifier-like columns entirely below this
       point (never touch ID values).
    4. Detect outliers with the IQR rule and replace them
       with the median — UNLESS more than 20% of the column
       would be flagged, in which case nothing is changed
       automatically (that's a sign the "outliers" are real
       variation, not bad data).
    """

    original = cleaned_df[column].copy()

    if not _looks_numeric_series(original):
        return

    numeric = pd.to_numeric(original, errors="coerce").astype(float)
    cleaned_df[column] = numeric

    valid = numeric.dropna()

    if len(valid) == 0:
        return

    # Invalid (non-numeric) values -> median

    median_value = valid.median()

    invalid_mask = original.notna() & numeric.isna()
    invalid_count = int(invalid_mask.sum())

    if invalid_count > 0:

        cleaned_df.loc[invalid_mask, column] = median_value

        _log(
            audit_log,
            category="Invalid Values",
            column=column,
            action="Filled with median",
            count=invalid_count,
            reason=(
                "Non-numeric value(s) were found inside a "
                "predominantly numeric column and replaced "
                "with the column median."
            ),
        )

    # Recompute after invalid-value correction.
    numeric = pd.to_numeric(cleaned_df[column], errors="coerce").astype(float)
    cleaned_df[column] = numeric
    valid = numeric.dropna()

    if len(valid) == 0:
        return

    # Never touch identifier columns beyond this point

    if _is_likely_identifier_column(numeric, column):
        _restore_numeric_dtype(cleaned_df, column)
        return

    if len(valid) < MIN_VALID_VALUES_FOR_OUTLIER_DETECTION:
        _restore_numeric_dtype(cleaned_df, column)
        return

    # IQR outlier detection

    q1 = valid.quantile(0.25)
    q3 = valid.quantile(0.75)
    iqr = q3 - q1

    if pd.isna(iqr) or iqr <= 0:
        _restore_numeric_dtype(cleaned_df, column)
        return

    lower_bound = q1 - IQR_MULTIPLIER * iqr
    upper_bound = q3 + IQR_MULTIPLIER * iqr

    outlier_mask = ((numeric < lower_bound) | (numeric > upper_bound)).fillna(False)
    outlier_count = int(outlier_mask.sum())

    if outlier_count == 0:
        _restore_numeric_dtype(cleaned_df, column)
        return

    outlier_ratio = outlier_count / len(valid)

    if outlier_ratio > MAX_OUTLIER_RATIO_FOR_AUTO_CORRECTION:

        # Too many "outliers" to trust automatic correction —
        # flag it and leave the values untouched.
        _log(
            audit_log,
            category="Outlier Review Needed",
            column=column,
            action="No automatic replacement",
            count=outlier_count,
            reason=(
                f"The IQR rule flagged {outlier_count} value(s) "
                f"({outlier_ratio:.0%} of the column) as outliers "
                "outside the range "
                f"[{lower_bound:.2f}, {upper_bound:.2f}]. That's "
                "too large a share to correct automatically — "
                "review these manually."
            ),
        )

        _restore_numeric_dtype(cleaned_df, column)
        return

    median_value = valid.median()
    cleaned_df.loc[outlier_mask, column] = median_value

    _log(
        audit_log,
        category="Outlier Correction",
        column=column,
        action="Replaced with median",
        count=outlier_count,
        reason=(
            "Value(s) fell outside the IQR bounds "
            f"[{lower_bound:.2f}, {upper_bound:.2f}] and were "
            "replaced with the column median."
        ),
    )

    _restore_numeric_dtype(cleaned_df, column)


# STEP: CATEGORICAL WHITESPACE + CASE NORMALIZATION

def _normalize_categorical_column(
    cleaned_df: pd.DataFrame,
    column,
    audit_log: list,
) -> None:
    """
    1. Strip leading/trailing whitespace and collapse
       repeated internal whitespace ("  Delhi " -> "Delhi").
    2. Standardize case-insensitive duplicates ("delhi",
       "Delhi", "DELHI") to whichever variant is most common.
    """

    series = cleaned_df[column]

    if not (
        pd.api.types.is_object_dtype(series)
        or pd.api.types.is_string_dtype(series)
        or isinstance(series.dtype, pd.CategoricalDtype)
    ):
        return

    # Whitespace normalization

    def _clean_text(value):
        if pd.isna(value) or not isinstance(value, str):
            return value
        stripped = value.strip()
        if not stripped:
            return np.nan
        return re.sub(r"\s+", " ", stripped)

    original_values = series.copy()
    new_values = series.apply(_clean_text)

    whitespace_changed = int(
        (
            (original_values != new_values)
            & original_values.notna()
            & new_values.notna()
        ).sum()
    )

    cleaned_df[column] = new_values

    if whitespace_changed > 0:
        _log(
            audit_log,
            category="Whitespace",
            column=column,
            action="Trimmed and normalized whitespace",
            count=whitespace_changed,
            reason=(
                "Leading/trailing or repeated internal "
                "whitespace was removed."
            ),
        )

    # Case-insensitive standardization

    series = cleaned_df[column]

    values = [v for v in series.dropna().unique() if isinstance(v, str)]

    if len(values) < 2:
        return

    groups: dict[str, list[str]] = {}

    for value in values:
        groups.setdefault(value.lower(), []).append(value)

    frequencies = series.value_counts()

    for normalized_key, variants in groups.items():

        if len(variants) <= 1:
            continue

        canonical = max(variants, key=lambda v: frequencies.get(v, 0))

        variant_mask = series.isin(variants) & (series != canonical)
        changed_count = int(variant_mask.sum())

        if changed_count == 0:
            continue

        cleaned_df.loc[variant_mask, column] = canonical

        _log(
            audit_log,
            category="Category Standardization",
            column=column,
            action="Standardized category values",
            count=changed_count,
            reason=(
                f"Equivalent category variants were standardized "
                f"to '{canonical}'."
            ),
        )

        series = cleaned_df[column]


# INTERNAL CLEANING ENGINE

def _clean_dataset_internal(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """
    The single cleaning pipeline used everywhere in the app
    (dashboard, tests, CLI). Order matters:

        1. Remove duplicate rows
        2. Fill missing values (numeric -> median, categorical -> mode)
        3. Normalize categorical text (whitespace + case)
        4. Correct numeric anomalies and outliers
        5. Remove constant columns (run LAST — step 4 can
           turn a near-constant column fully constant)
    """

    cleaned_df = df.copy()
    audit_log: list[dict] = []

    # 1. REMOVE DUPLICATES

    duplicate_count = int(cleaned_df.duplicated().sum())

    if duplicate_count > 0:

        cleaned_df = cleaned_df.drop_duplicates()

        _log(
            audit_log,
            category="Duplicate Rows",
            column="All columns",
            action="Removed duplicates",
            count=duplicate_count,
            reason=(
                "Exact duplicate rows were removed to prevent "
                "repeated observations."
            ),
        )

    # 2. HANDLE MISSING VALUES

    for column in cleaned_df.columns:

        missing_count = int(cleaned_df[column].isna().sum())

        if missing_count == 0:
            continue

        if pd.api.types.is_numeric_dtype(cleaned_df[column]):

            median_value = cleaned_df[column].median()

            if pd.isna(median_value):
                # Every value in this column is missing, so there
                # is no median to compute — fillna(NaN) would be a
                # silent no-op. Leave the column as-is; if it's
                # still constant/empty, step 5 below drops it and
                # logs that honestly instead of us falsely
                # claiming a median fill happened.
                continue

            cleaned_df[column] = cleaned_df[column].fillna(median_value)

            _log(
                audit_log,
                category="Missing Values",
                column=column,
                action="Filled with median",
                count=missing_count,
                reason=(
                    "Numeric columns are imputed using the median "
                    "to reduce the effect of extreme values."
                ),
            )

        else:

            mode_values = cleaned_df[column].mode()

            if not mode_values.empty:

                mode_value = mode_values.iloc[0]
                cleaned_df[column] = cleaned_df[column].fillna(mode_value)

                _log(
                    audit_log,
                    category="Missing Values",
                    column=column,
                    action="Filled with most frequent value",
                    count=missing_count,
                    reason=(
                        "Categorical columns are imputed using the "
                        "most frequent observed category."
                    ),
                )

    # 3. NORMALIZE CATEGORICAL TEXT

    categorical_columns = cleaned_df.select_dtypes(
        include=["object", "string", "category"]
    ).columns

    for column in categorical_columns:
        cleaned_df[column] = cleaned_df[column].astype("string")
        _normalize_categorical_column(cleaned_df, column, audit_log)

    # 4. NUMERIC ANOMALY + OUTLIER CORRECTION

    for column in cleaned_df.columns:

        if _looks_numeric_series(cleaned_df[column]):
            _correct_numeric_column(cleaned_df, column, audit_log)

    # 5. REMOVE CONSTANT COLUMNS (run last, see docstring)

    constant_columns = [
        column
        for column in cleaned_df.columns
        if cleaned_df[column].nunique(dropna=True) <= 1
    ]

    for column in constant_columns:

        _log(
            audit_log,
            category="Constant Column",
            column=column,
            action="Removed column",
            count=1,
            reason=(
                "The column contains no useful variation because "
                "it has only one unique value."
            ),
        )

    if constant_columns:
        cleaned_df = cleaned_df.drop(columns=constant_columns)

    return cleaned_df, audit_log


# PUBLIC API

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a dataset automatically. Returns the cleaned DataFrame only."""

    cleaned_df, _ = _clean_dataset_internal(df)
    return cleaned_df


def clean_dataset_with_log(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """
    Clean a dataset and return an audit trail.

    Every audit-log entry has exactly the same five keys:
    category, column, action, count, reason.
    """

    return _clean_dataset_internal(df)


def get_cleaning_summary(
    original_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    audit_log: list[dict],
) -> dict:
    """Generate a high-level summary of cleaning operations."""

    original_rows = len(original_df)
    cleaned_rows = len(cleaned_df)

    original_columns = len(original_df.columns)
    cleaned_columns = len(cleaned_df.columns)

    original_missing = int(original_df.isna().sum().sum())
    cleaned_missing = int(cleaned_df.isna().sum().sum())

    return {
        "original_rows": original_rows,
        "cleaned_rows": cleaned_rows,
        "rows_removed": original_rows - cleaned_rows,
        "original_columns": original_columns,
        "cleaned_columns": cleaned_columns,
        "columns_removed": original_columns - cleaned_columns,
        "original_missing_values": original_missing,
        "remaining_missing_values": cleaned_missing,
        "missing_values_handled": original_missing - cleaned_missing,
        "total_changes": len(audit_log),
    }