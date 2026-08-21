import re

import pandas as pd


NO_CONFIDENT_TARGET_LABEL = "— Select a target column —"
"""
Sentinel option shown in the dashboard's target selectbox
when auto-detection has no confident guess. Never a real
column name, so it can't collide with an actual dataset.
"""


# Below this minority-class share, the split is considered
# imbalanced enough to warn about. 10% is a common,
# well-documented rule-of-thumb threshold for "severe" class
# imbalance in classification literature.
IMBALANCE_MINORITY_RATIO_THRESHOLD = 0.10

# A class with fewer than this many examples can't be reliably
# split into both a train and a test set — that's a distinct,
# more urgent problem than "imbalanced but workable".
MIN_SAMPLES_PER_CLASS_FOR_RELIABLE_SPLIT = 2


def check_class_imbalance(target: pd.Series) -> dict | None:
    """
    Inspect a classification target column for severe class
    imbalance.

    Returns None if the column doesn't look like a usable
    classification target (fewer than 2 classes present), so
    callers can safely skip regression targets or broken data
    without a special case.
    """

    counts = target.dropna().value_counts()

    if len(counts) < 2:
        return None

    total = int(counts.sum())
    minority_class = counts.idxmin()
    minority_count = int(counts.min())
    minority_ratio = minority_count / total

    return {
        "class_counts": {
            str(label): int(count)
            for label, count in counts.items()
        },
        "minority_class": str(minority_class),
        "minority_count": minority_count,
        "minority_ratio": minority_ratio,
        "is_imbalanced": (
            minority_ratio < IMBALANCE_MINORITY_RATIO_THRESHOLD
        ),
        "too_few_to_split": (
            minority_count < MIN_SAMPLES_PER_CLASS_FOR_RELIABLE_SPLIT
        ),
    }


def resolve_target_selectbox_options(
    auto_detected_target: str | None,
    available_columns: list[str],
) -> tuple[list[str], int]:
    """
    Decide what the dashboard's target-column selectbox
    should show, given whatever detect_target_column()
    returned.

    BUG THIS FIXES: previously, when auto-detection had no
    confident guess (returns None), the dashboard's own
    fallback logic did `default_index = 0`, which silently
    pre-selected the FIRST column in the dataset as the
    target — turning "I couldn't confidently detect a
    target" into "let's use column 1" without the user ever
    choosing that. This function makes "no confident guess"
    an explicit, visible state instead: a placeholder option
    the user must actively replace with a real choice.

    Returns (options_list, default_index) — pure and
    Streamlit-free on purpose, so this decision logic is
    unit-testable without simulating a browser.
    """

    if (
        auto_detected_target is not None
        and auto_detected_target in available_columns
    ):
        return available_columns, available_columns.index(
            auto_detected_target
        )

    return (
        [NO_CONFIDENT_TARGET_LABEL] + available_columns,
        0,
    )


# TARGET COLUMN DETECTION

def detect_target_column(
    df: pd.DataFrame,
) -> str | None:
    """
    Automatically detect the most likely target column.

    The detector scores columns using multiple signals
    instead of relying on a fixed dataset schema.
    """

    if df.empty or len(df.columns) == 0:
        return None

    scores = {}

    strong_target_names = {
        "target",
        "label",
        "class",
        "output",
        "result",
        "outcome",
        "response",
        "prediction",
        "y",
    }

    target_keywords = {
        "target",
        "label",
        "class",
        "outcome",
        "result",
        "response",
        "status",
        "churn",
        "fraud",
        "default",
        "survive",
        "survived",
        "purchase",
        "purchased",
        "promote",
        "promoted",
        "approve",
        "approved",
        "pass",
        "passed",
        "fail",
        "failed",
        "price",
        "cost",
        "revenue",
        "sales",
        "amount",
        "value",
    }

    id_keywords = {
        "id",
        "identifier",
        "index",
        "uuid",
    }

    feature_keywords = {
        "age",
        "area",
        "bedroom",
        "bedrooms",
        "salary",
        "income",
        "experience",
        "height",
        "weight",
        "distance",
        "year",
        "years",
        "count",
        "number",
    }

    for position, column in enumerate(df.columns):

        column_name = str(column).strip()
        normalized_name = column_name.lower()

        score = 0

        series = df[column]

        # -------------------------------------------------
        # 1. Exact target name
        # -------------------------------------------------

        if normalized_name in strong_target_names:
            score += 100

        # -------------------------------------------------
        # 2. Target-like words
        # -------------------------------------------------

        words = set(
            re.findall(
                r"[a-zA-Z0-9]+",
                normalized_name,
            )
        )

        keyword_matches = words.intersection(
            target_keywords
        )

        score += len(keyword_matches) * 35

        # 3. ID penalty

        id_matches = words.intersection(
            id_keywords
        )

        if id_matches:
            score -= 100

        non_missing = series.dropna()

        if len(non_missing) > 0:

            unique_ratio = (
                non_missing.nunique()
                / len(non_missing)
            )

            if unique_ratio >= 0.95:
                score -= 40

            elif unique_ratio >= 0.80:
                score -= 20

        # 4. Feature-name penalty

        feature_matches = words.intersection(
            feature_keywords
        )

        score -= len(feature_matches) * 20

        # 5. Cardinality

        unique_count = series.nunique(
            dropna=True
        )

        if unique_count == 2:
            score += 20

        elif 3 <= unique_count <= 10:
            score += 5

        # 6. Numeric target analysis

        if pd.api.types.is_numeric_dtype(series):

            if len(non_missing) > 0:

                unique_ratio = (
                    non_missing.nunique()
                    / len(non_missing)
                )

                if unique_ratio >= 0.70:
                    score += 25

                elif unique_ratio >= 0.40:
                    score += 15

                elif unique_ratio <= 0.30:
                    score -= 10

        # 7. Missing-value penalty

        missing_ratio = series.isna().mean()

        if missing_ratio > 0.50:
            score -= 50

        elif missing_ratio > 0.20:
            score -= 20

        # 8. Slight preference for later columns

        if position == len(df.columns) - 1:
            score += 5

        scores[column] = score

    if not scores:
        return None

    best_column = max(
        scores,
        key=scores.get,
    )

    if scores[best_column] < 0:
        return None

    return best_column


# ML TASK DETECTION

def detect_task_type(
    df: pd.DataFrame,
    target_column: str,
) -> str:
    """
    Detect whether the ML problem is Classification
    or Regression.
    """

    if target_column not in df.columns:

        raise ValueError(
            f"Target column '{target_column}' "
            "does not exist."
        )

    target = df[target_column].dropna()

    if target.empty:

        raise ValueError(
            "Target column contains no usable values."
        )

    # Boolean → Classification

    if pd.api.types.is_bool_dtype(target):

        return "Classification"

    # Text / categorical → Classification

    if (
        pd.api.types.is_object_dtype(target)
        or pd.api.types.is_string_dtype(target)
        or isinstance(
            target.dtype,
            pd.CategoricalDtype,
        )
    ):

        return "Classification"

    # Numeric target

    if pd.api.types.is_numeric_dtype(target):

        unique_values = target.nunique()

        # Binary numeric target
        # Example: 0 / 1
        if unique_values == 2:

            return "Classification"

        # Integer targets require additional analysis.
        #
        # Example:
        # bedrooms = 1, 2, 3, 4
        # → Classification
        #
        # Example:
        # price = 4500000, 5200000, 6500000
        # → Regression

        if pd.api.types.is_integer_dtype(target):

            min_value = target.min()
            max_value = target.max()

            value_range = max_value - min_value

            # Small integer labels
            if (
                unique_values <= 10
                and min_value >= 0
                and max_value <= 20
                and value_range <= 20
            ):

                return "Classification"

            # Larger numeric integer values
            # are treated as continuous quantities.
            return "Regression"

        # Floating-point numeric values are normally
        # continuous quantities.
        return "Regression"

    # Safe fallback
    return "Classification"


# COMPLETE ML ANALYSIS

def analyze_ml_task(
    df: pd.DataFrame,
    target_column: str | None = None,
) -> dict:
    """
    Detect the target column and determine the ML task.
    """

    if target_column is None:

        target_column = detect_target_column(df)

    if target_column is None:

        raise ValueError(
            "DataPilot could not confidently detect "
            "a target column. Please select the target "
            "column manually."
        )

    task_type = detect_task_type(
        df,
        target_column,
    )

    target = df[target_column]

    class_balance = (
        check_class_imbalance(target)
        if task_type == "Classification"
        else None
    )

    return {
        "target_column": target_column,
        "task_type": task_type,
        "target_unique_values": int(
            target.nunique(dropna=True)
        ),
        "target_missing_values": int(
            target.isna().sum()
        ),
        "rows": len(df),
        "features": len(df.columns) - 1,
        "class_balance": class_balance,
    }