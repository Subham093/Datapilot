import numpy as np
import pandas as pd

from src.config import LEAKAGE_CORRELATION_THRESHOLD

# Correlation math effectively squares each value internally.
# Anything whose magnitude approaches sqrt(float64 max) (~1.34e154)
# would overflow float64 range once squared, producing NaN/inf and
# a meaningless correlation — regardless of whether the original
# value was literal infinity or just an absurdly large finite
# number. This threshold is set well below that boundary. Values
# at or above it are excluded from this correlation check only —
# in the extremely unlikely case a real dataset legitimately uses
# numbers at this scale, this wouldn't affect anything else DataPilot
# does with that column, only this one leakage-correlation check.
CORRELATION_SAFE_MAGNITUDE = 1e100


def detect_target_leakage(
    df: pd.DataFrame,
    target_column: str,
) -> list:
    """
    Detect simple and explainable forms of
    potential target leakage.

    This is a warning system, not proof of leakage.
    """

    if target_column not in df.columns:
        raise ValueError(
            f"Target column '{target_column}' "
            "does not exist."
        )

    warnings = []

    target = df[target_column]

    # ---------------------------------------------------------
    # 1. Suspicious column names
    # ---------------------------------------------------------

    leakage_keywords = [
        "target",
        "label",
        "outcome",
        "result",
        "prediction",
        "predicted",
        "actual",
        "future",
        "post",
        "after",
    ]

    for column in df.columns:

        if column == target_column:
            continue

        column_name = str(column).strip().lower()

        matched_keywords = [
            keyword
            for keyword in leakage_keywords
            if keyword in column_name
        ]

        if matched_keywords:

            warnings.append({
                "type": "Suspicious Feature Name",
                "column": column,
                "severity": "Medium",
                "description": (
                    "Feature name may contain information "
                    "related to the target or future outcome."
                ),
                "recommended_action": (
                    "Review whether this feature would "
                    "actually be available at prediction time."
                ),
            })

    # ---------------------------------------------------------
    # 2. Exact copy of target
    # ---------------------------------------------------------

    for column in df.columns:

        if column == target_column:
            continue

        try:
            if df[column].equals(target):

                warnings.append({
                    "type": "Target Copy",
                    "column": column,
                    "severity": "High",
                    "description": (
                        "Feature appears to be an exact copy "
                        "of the target column."
                    ),
                    "recommended_action": (
                        "Remove this feature before training."
                    ),
                })

        except Exception:
            continue

    # ---------------------------------------------------------
    # 3. Extremely high correlation
    # ---------------------------------------------------------

    if pd.api.types.is_numeric_dtype(target):

        numeric_columns = df.select_dtypes(
            include=["number"]
        ).columns

        for column in numeric_columns:

            if column == target_column:
                continue

            pair = df[[column, target_column]].dropna()

            # dropna() removes missing values but not inf/-inf or
            # astronomically large-but-technically-finite values
            # (e.g. 1e308) — both are "present" as far as pandas is
            # concerned, but both corrupt the correlation math
            # (numpy warns about overflow/invalid-value during the
            # internal computation) and produce a meaningless
            # result. A value doesn't need to be literal infinity
            # to behave like it once it's squared during Pearson
            # correlation — anything whose magnitude approaches
            # float64's own limit is just as unsafe.
            pair = pair[
                (np.abs(pair[column]) < CORRELATION_SAFE_MAGNITUDE)
                & (np.abs(pair[target_column]) < CORRELATION_SAFE_MAGNITUDE)
            ]

            if len(pair) < 3:
                continue

            # Correlation is undefined when either side has only
            # one distinct value (e.g. a constant feature or a
            # single-class target) — the standard deviation would
            # be zero, making the underlying division 0/0. Checking
            # distinct-value count directly says exactly what's
            # being tested, without relying on floating-point
            # equality against 0.
            if (
                pair[column].nunique(dropna=True) <= 1
                or pair[target_column].nunique(dropna=True) <= 1
            ):
                continue

            correlation = pair[column].corr(
                pair[target_column]
            )

            if pd.notna(correlation) and abs(correlation) >= LEAKAGE_CORRELATION_THRESHOLD:

                warnings.append({
                    "type": "Very High Target Correlation",
                    "column": column,
                    "severity": "High",
                    "description": (
                        f"Feature has correlation of "
                        f"{correlation:.3f} with the target."
                    ),
                    "recommended_action": (
                        "Investigate whether this feature "
                        "contains target-derived information."
                    ),
                })

    return warnings