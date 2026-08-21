# -*- coding: utf-8 -*-

import pandas as pd

from src.config import DEFAULT_DRIFT_THRESHOLD_PERCENT


def compare_datasets(
    reference_df: pd.DataFrame,
    current_df: pd.DataFrame,
) -> dict:
    """
    Compare a reference dataset with a current dataset.

    Detects:
    - row-count changes
    - column-count changes
    - added columns
    - removed columns
    - numeric mean changes
    """

    reference_columns = set(reference_df.columns)
    current_columns = set(current_df.columns)

    added_columns = sorted(
        current_columns - reference_columns
    )

    removed_columns = sorted(
        reference_columns - current_columns
    )

    common_columns = sorted(
        reference_columns & current_columns
    )

    numeric_drift = []

    for column in common_columns:

        reference_series = reference_df[column]
        current_series = current_df[column]

        if (
            pd.api.types.is_numeric_dtype(
                reference_series
            )
            and pd.api.types.is_numeric_dtype(
                current_series
            )
        ):

            reference_mean = reference_series.mean()
            current_mean = current_series.mean()

            if (
                pd.notna(reference_mean)
                and pd.notna(current_mean)
            ):

                if reference_mean == 0:

                    if current_mean == 0:
                        change_percentage = 0.0
                    else:
                        change_percentage = 100.0

                else:

                    change_percentage = (
                        abs(
                            current_mean
                            - reference_mean
                        )
                        / abs(reference_mean)
                    ) * 100

                numeric_drift.append(
                    {
                        "column": column,
                        "reference_mean": round(
                            float(reference_mean),
                            4,
                        ),
                        "current_mean": round(
                            float(current_mean),
                            4,
                        ),
                        "change_percentage": round(
                            float(change_percentage),
                            2,
                        ),
                    }
                )

    return {
        "reference_rows": len(reference_df),
        "current_rows": len(current_df),
        "reference_columns": len(
            reference_columns
        ),
        "current_columns": len(
            current_columns
        ),
        "added_columns": added_columns,
        "removed_columns": removed_columns,
        "numeric_drift": numeric_drift,
    }


def detect_data_drift(
    comparison: dict,
    threshold: float = DEFAULT_DRIFT_THRESHOLD_PERCENT,
) -> list:
    """
    Convert dataset comparison results
    into actionable drift warnings.
    """

    warnings = []

    # Numeric drift
    for item in comparison.get(
        "numeric_drift",
        [],
    ):

        if (
            item["change_percentage"]
            >= threshold
        ):

            warnings.append(
                {
                    "type": "Numeric Drift",
                    "column": item["column"],
                    "severity": "Medium",
                    "description": (
                        f"Mean changed by "
                        f"{item['change_percentage']}%."
                    ),
                    "recommended_action": (
                        "Investigate the source of "
                        "the distribution change."
                    ),
                }
            )

    # New columns
    for column in comparison.get(
        "added_columns",
        [],
    ):

        warnings.append(
            {
                "type": "New Column",
                "column": column,
                "severity": "Low",
                "description": (
                    "Column was not present in "
                    "the reference dataset."
                ),
                "recommended_action": (
                    "Verify whether the new column "
                    "is expected."
                ),
            }
        )

    # Removed columns
    for column in comparison.get(
        "removed_columns",
        [],
    ):

        warnings.append(
            {
                "type": "Removed Column",
                "column": column,
                "severity": "Medium",
                "description": (
                    "Column from the reference "
                    "dataset is missing."
                ),
                "recommended_action": (
                    "Verify the data pipeline "
                    "before production use."
                ),
            }
        )

    return warnings


# Compatibility alias.
# Some older dashboard code may use detect_drift.
def detect_drift(
    comparison: dict,
    threshold: float = DEFAULT_DRIFT_THRESHOLD_PERCENT,
) -> list:

    return detect_data_drift(
        comparison,
        threshold,
    )