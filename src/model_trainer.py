import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.preprocessing import (
    build_preprocessor,
    split_features_target,
)

from src.model_selector import (
    get_models,
)


def train_models(
    df: pd.DataFrame,
    target_column: str,
    task_type: str,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict:
    """
    Train all candidate models and return
    trained pipelines plus train/test data.
    """

    X, y = split_features_target(
        df,
        target_column,
    )

    if len(df) < 10:
        raise ValueError(
            "Dataset is too small for reliable "
            "machine learning. At least 10 rows "
            "are recommended."
        )

    stratify = None

    if task_type == "Classification":

        class_counts = y.value_counts()

        if (
            len(class_counts) >= 2
            and class_counts.min() >= 2
        ):
            stratify = y

    try:

        X_train, X_test, y_train, y_test = (
            train_test_split(
                X,
                y,
                test_size=test_size,
                random_state=random_state,
                stratify=stratify,
            )
        )

    except ValueError:

        X_train, X_test, y_train, y_test = (
            train_test_split(
                X,
                y,
                test_size=test_size,
                random_state=random_state,
            )
        )

    models = get_models(
        task_type
    )

    trained_models = {}

    for model_name, model in models.items():

        preprocessor = build_preprocessor(
            df,
            target_column,
        )

        pipeline = Pipeline(
            steps=[
                (
                    "preprocessor",
                    preprocessor,
                ),
                (
                    "model",
                    model,
                ),
            ]
        )

        pipeline.fit(
            X_train,
            y_train,
        )

        trained_models[
            model_name
        ] = pipeline

    return {
        "models": trained_models,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "target_column": target_column,
        "task_type": task_type,
    }