import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import HIGH_CARDINALITY_THRESHOLD, MAX_ONE_HOT_CATEGORIES


def detect_high_cardinality_columns(
    df: pd.DataFrame,
    target_column: str,
) -> list[str]:
    """
    Report which categorical columns WOULD be excluded from
    training for being high-cardinality, without actually
    building the preprocessor.

    This mirrors the exact same check build_preprocessor()
    applies internally — kept as a separate, pure function
    (rather than having build_preprocessor return this info)
    so existing callers of build_preprocessor() are completely
    unaffected. The dashboard calls this before training to
    show the user what's about to be silently excluded and
    why, instead of leaving them to guess.
    """

    if target_column not in df.columns:
        raise ValueError(
            f"Target column '{target_column}' "
            "does not exist."
        )

    X = df.drop(columns=[target_column])

    categorical_columns = X.select_dtypes(
        include=["object", "string", "category", "bool"]
    ).columns.tolist()

    dropped_columns = []

    for column in categorical_columns:

        non_null = X[column].dropna()

        if len(non_null) == 0:
            continue

        unique_ratio = non_null.nunique() / len(non_null)

        if unique_ratio > HIGH_CARDINALITY_THRESHOLD:
            dropped_columns.append(column)

    return dropped_columns


def build_preprocessor(
    df: pd.DataFrame,
    target_column: str,
):
    """
    Build an automatic preprocessing pipeline.

    Numeric columns:
        Missing values → median
        Scaling → StandardScaler

    Categorical columns:
        Missing values → most frequent
        Encoding → OneHotEncoder

    High-cardinality categorical columns (e.g. a free-text
    "name" column, or a leaked ID column) are EXCLUDED rather
    than one-hot encoded. Encoding a column with thousands of
    unique values creates thousands of near-useless features,
    balloons memory, and silently degrades every downstream
    model — this is a common, easy-to-miss production bug.
    """

    if target_column not in df.columns:
        raise ValueError(
            f"Target column '{target_column}' "
            "does not exist."
        )

    X = df.drop(
        columns=[target_column]
    )

    numeric_columns = X.select_dtypes(
        include=["number"]
    ).columns.tolist()

    categorical_columns = X.select_dtypes(
        include=["object", "string", "category", "bool"]
    ).columns.tolist()

    # Drop high-cardinality categorical columns.
    
    # A column where most values are unique (free text,
    # names, leaked ID columns) would otherwise explode
    # into one OneHotEncoder feature per unique value.

    if categorical_columns:

        dropped_high_cardinality = []

        for column in list(categorical_columns):

            non_null = X[column].dropna()

            if len(non_null) == 0:
                continue

            unique_ratio = non_null.nunique() / len(non_null)

            if unique_ratio > HIGH_CARDINALITY_THRESHOLD:
                categorical_columns.remove(column)
                dropped_high_cardinality.append(column)

        if dropped_high_cardinality:
            X = X.drop(columns=dropped_high_cardinality)

    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                ),
            ),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    max_categories=MAX_ONE_HOT_CATEGORIES,
                ),
            ),
        ]
    )

    transformers = []

    if numeric_columns:
        transformers.append(
            (
                "numeric",
                numeric_pipeline,
                numeric_columns,
            )
        )

    if categorical_columns:
        transformers.append(
            (
                "categorical",
                categorical_pipeline,
                categorical_columns,
            )
        )

    if not transformers:
        raise ValueError(
            "No usable feature columns were found."
        )

    preprocessor = ColumnTransformer(
        transformers=transformers
    )

    return preprocessor


def split_features_target(
    df: pd.DataFrame,
    target_column: str,
):
    """
    Separate the dataset into X and y.
    """

    if target_column not in df.columns:
        raise ValueError(
            f"Target column '{target_column}' "
            "does not exist."
        )

    X = df.drop(
        columns=[target_column]
    )

    y = df[target_column]

    return X, y