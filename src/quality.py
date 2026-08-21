import re

import numpy as np
import pandas as pd

from src.config import IQR_MULTIPLIER

# Reused from cleaner.py (not duplicated) so that "Invalid Values"
# detected here always matches exactly what clean_dataset_with_log()
# will later fix — one source of truth for "does this column look
# numeric", instead of two separate implementations that could
# silently drift apart over time.
from src.cleaner import _looks_numeric_series


def detect_quality_issues(df: pd.DataFrame) -> list:
    issues = []

    # 1. MISSING VALUES

    for column in df.columns:

        missing = int(df[column].isna().sum())

        if missing > 0:

            if pd.api.types.is_numeric_dtype(df[column]):
                recommendation = "Fill with median"
            else:
                recommendation = "Fill with most frequent value"

            issues.append({
                "type": "Missing Values",
                "column": column,
                "count": missing,
                "severity": "Medium",
                "description": (
                    f"{missing} missing value(s) found."
                ),
                "recommended_action": recommendation,
            })

    # 2. DUPLICATE ROWS

    duplicates = int(df.duplicated().sum())

    if duplicates > 0:

        issues.append({
            "type": "Duplicate Rows",
            "column": "All columns",
            "count": duplicates,
            "severity": "Medium",
            "description": (
                f"{duplicates} duplicate row(s) found."
            ),
            "recommended_action": "Remove duplicate rows",
        })

    # 3. CONSTANT COLUMNS

    for column in df.columns:

        if df[column].nunique(dropna=True) <= 1:

            issues.append({
                "type": "Constant Column",
                "column": column,
                "count": 1,
                "severity": "Low",
                "description": (
                    "Column contains only one unique value."
                ),
                "recommended_action": (
                    "Remove constant column"
                ),
            })

    # 4. CATEGORY INCONSISTENCIES

    categorical_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in categorical_columns:

        values = (
            df[column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        normalized_values = values.str.lower()

        groups = {}

        for original, normalized in zip(
            values,
            normalized_values
        ):

            groups.setdefault(
                normalized,
                set()
            ).add(original)

        for normalized, variants in groups.items():

            if len(variants) > 1:

                variants_text = ", ".join(
                    sorted(variants)
                )

                issues.append({
                    "type": "Category Inconsistency",
                    "column": column,
                    "count": len(variants),
                    "severity": "Low",
                    "description": (
                        "Possible inconsistent values: "
                        f"{variants_text}"
                    ),
                    "recommended_action": (
                        "Standardize category formatting"
                    ),
                })

    # 5. NUMERICAL OUTLIERS

    numerical_columns = df.select_dtypes(
        include=["number"]
    ).columns

    for column in numerical_columns:

        series = df[column].dropna()

        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - IQR_MULTIPLIER * iqr
        upper_bound = q3 + IQR_MULTIPLIER * iqr

        outlier_count = int(
            (
                (series < lower_bound)
                | (series > upper_bound)
            ).sum()
        )

        if outlier_count > 0:

            issues.append({
                "type": "Potential Outliers",
                "column": column,
                "count": outlier_count,
                "severity": "Medium",
                "description": (
                    f"{outlier_count} potential "
                    "outlier value(s) detected."
                ),
                "recommended_action": (
                    "Review outliers before removing "
                    "or transforming"
                ),
            })

    # 6. INVALID VALUES (NUMERIC-AS-TEXT COLUMNS)
    
    # A column can be mostly numeric but stored as text, with a
    # few genuinely non-numeric entries mixed in (e.g. "42k"
    # instead of 42000). clean_dataset_with_log() already fixes
    # these — this check surfaces the SAME issue here too, so
    # the Data Quality table and the cleaning audit log always
    # agree on what was actually wrong.

    for column in df.columns:

        if pd.api.types.is_numeric_dtype(df[column]):
            continue

        if not _looks_numeric_series(df[column]):
            continue

        non_null = df[column].dropna()

        if len(non_null) == 0:
            continue

        parsed = pd.to_numeric(non_null, errors="coerce")

        invalid_count = int(parsed.isna().sum())

        if invalid_count > 0:

            issues.append({
                "type": "Invalid Values",
                "column": column,
                "count": invalid_count,
                "severity": "Medium",
                "description": (
                    f"{invalid_count} non-numeric value(s) "
                    "found in a predominantly numeric column."
                ),
                "recommended_action": "Fill with median",
            })

    # 7. HEAVILY MISSING COLUMNS
    
    # A column that's mostly empty isn't really a "fill in the
    # gaps" situation — imputing 70%+ fake values makes a
    # column mostly fabricated. This is a distinct, more urgent
    # issue than ordinary missing values, so it's flagged
    # separately with its own recommendation: consider dropping
    # the column instead of imputing it.

    HEAVILY_MISSING_THRESHOLD = 0.5

    for column in df.columns:

        if len(df) == 0:
            continue

        missing_ratio = df[column].isna().sum() / len(df)

        if missing_ratio >= HEAVILY_MISSING_THRESHOLD:

            issues.append({
                "type": "Heavily Missing Column",
                "column": column,
                "count": int(df[column].isna().sum()),
                "severity": "High",
                "description": (
                    f"{missing_ratio:.0%} of this column's "
                    "values are missing — too sparse to "
                    "impute reliably."
                ),
                "recommended_action": (
                    "Consider dropping this column instead "
                    "of filling it in"
                ),
            })

    # 8. LIKELY PERSONAL/SENSITIVE INFORMATION (PII)    

    # Pattern-based, not column-name-based, so it works for any
    # dataset — not just ones with a column literally named
    # "email". Purely informational: DataPilot never modifies
    # or removes this data automatically, since that's a
    # decision the person uploading the data should make.

    EMAIL_PATTERN = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    PHONE_PATTERN = re.compile(
        r"^[+]?[\d][\d\s().-]{7,}\d$"
    )

    PII_MATCH_RATIO_THRESHOLD = 0.5

    for column in df.select_dtypes(
        include=["object", "string"]
    ).columns:

        values = df[column].dropna().astype(str).str.strip()

        if len(values) == 0:
            continue

        email_matches = values.str.match(EMAIL_PATTERN).mean()
        phone_matches = values.str.match(PHONE_PATTERN).mean()

        if email_matches >= PII_MATCH_RATIO_THRESHOLD:

            issues.append({
                "type": "Possible Personal Information",
                "column": column,
                "count": int(
                    values.str.match(EMAIL_PATTERN).sum()
                ),
                "severity": "Medium",
                "description": (
                    "This column looks like it contains "
                    "email addresses."
                ),
                "recommended_action": (
                    "Review before sharing or deploying — "
                    "consider removing or masking"
                ),
            })

        elif phone_matches >= PII_MATCH_RATIO_THRESHOLD:

            issues.append({
                "type": "Possible Personal Information",
                "column": column,
                "count": int(
                    values.str.match(PHONE_PATTERN).sum()
                ),
                "severity": "Medium",
                "description": (
                    "This column looks like it contains "
                    "phone numbers."
                ),
                "recommended_action": (
                    "Review before sharing or deploying — "
                    "consider removing or masking"
                ),
            })

    # 9. NON-FINITE VALUES (inf / -inf)
    
    # Infinity isn't a statistical outlier — it's a value that
    # silently breaks correlation, standardization, and most
    # model training downstream, often without an obvious error
    # (e.g. mean/std become NaN, not a clear crash). The generic
    # IQR outlier check technically catches these too (infinity
    # is always outside any finite range), but bucketing it with
    # ordinary "review this unusually high salary" outliers
    # understates how different and urgent this actually is —
    # so it gets called out explicitly, at higher severity.

    for column in df.select_dtypes(include="number").columns:

        non_finite_mask = ~df[column].isna() & ~np.isfinite(df[column])
        non_finite_count = int(non_finite_mask.sum())

        if non_finite_count > 0:

            issues.append({
                "type": "Non-Finite Values",
                "column": column,
                "count": non_finite_count,
                "severity": "High",
                "description": (
                    f"{non_finite_count} value(s) are "
                    "infinite (inf/-inf), not just unusually "
                    "large — this will break correlation, "
                    "scaling, and most model training if left "
                    "as-is."
                ),
                "recommended_action": (
                    "Review and replace or remove — these are "
                    "not valid numeric measurements"
                ),
            })

    return issues


def calculate_quality_score(
    df: pd.DataFrame,
    issues: list,
) -> int:

    """
    Calculate a balanced data-quality score
    from 0 to 100.

    The score considers the proportion of
    affected rows rather than simply subtracting
    a large penalty for every issue.
    """

    if df.empty:
        return 0

    rows = len(df)

    total_penalty = 0.0

    for issue in issues:

        issue_type = issue["type"]
        count = issue["count"]

        # Missing values
        if issue_type == "Missing Values":

            impact = min(
                count / rows,
                1.0
            )

            total_penalty += (
                impact * 15
            )

        # Invalid values (numeric-as-text) — same weight as
        # Missing Values since it's the same kind of problem:
        # a value that isn't actually usable as-is.
        elif issue_type == "Invalid Values":

            impact = min(
                count / rows,
                1.0
            )

            total_penalty += (
                impact * 15
            )

        # Duplicate rows
        elif issue_type == "Duplicate Rows":

            impact = min(
                count / rows,
                1.0
            )

            total_penalty += (
                impact * 10
            )

        # Constant columns
        elif issue_type == "Constant Column":

            total_penalty += 5

        # Category inconsistencies
        elif issue_type == "Category Inconsistency":

            total_penalty += 3

        # Outliers are warnings, not automatic errors
        elif issue_type == "Potential Outliers":

            total_penalty += 2

        # Heavily missing columns — bigger penalty than
        # ordinary missing values, since imputing 70%+ fake
        # data is a much bigger integrity concern than filling
        # a handful of gaps.
        elif issue_type == "Heavily Missing Column":

            total_penalty += 10

        # Possible PII — informational/compliance concern
        # rather than a correctness problem, so a light
        # penalty rather than a heavy one.
        elif issue_type == "Possible Personal Information":

            total_penalty += 3

        # Non-finite values — weighted well above a normal
        # outlier, since this isn't "review this value", it's
        # "this will silently break downstream math".
        elif issue_type == "Non-Finite Values":

            total_penalty += 12

    score = 100 - total_penalty

    return int(
        max(
            0,
            min(100, round(score))
        )
    )