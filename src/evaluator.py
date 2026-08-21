import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import cross_val_score


def evaluate_models(
    training_result: dict,
) -> pd.DataFrame:
    """
    Evaluate all trained models on the held-out test set.

    Also calculates cross-validation performance when
    the dataset is large enough for reliable CV.
    """

    models = training_result["models"]
    X_test = training_result["X_test"]
    y_test = training_result["y_test"]
    task_type = training_result["task_type"]

    results = []

    for model_name, model in models.items():

        predictions = model.predict(X_test)

        # CLASSIFICATION

        if task_type == "Classification":

            accuracy = accuracy_score(
                y_test,
                predictions,
            )

            precision = precision_score(
                y_test,
                predictions,
                average="weighted",
                zero_division=0,
            )

            recall = recall_score(
                y_test,
                predictions,
                average="weighted",
                zero_division=0,
            )

            f1 = f1_score(
                y_test,
                predictions,
                average="weighted",
                zero_division=0,
            )

            results.append(
                {
                    "model": model_name,
                    "accuracy": round(
                        accuracy,
                        4,
                    ),
                    "precision": round(
                        precision,
                        4,
                    ),
                    "recall": round(
                        recall,
                        4,
                    ),
                    "f1_score": round(
                        f1,
                        4,
                    ),
                }
            )

        # REGRESSION

        elif task_type == "Regression":

            mae = mean_absolute_error(
                y_test,
                predictions,
            )

            mse = mean_squared_error(
                y_test,
                predictions,
            )

            rmse = mse ** 0.5

            r2 = r2_score(
                y_test,
                predictions,
            )

            results.append(
                {
                    "model": model_name,
                    "mae": round(
                        mae,
                        4,
                    ),
                    "rmse": round(
                        rmse,
                        4,
                    ),
                    "r2_score": round(
                        r2,
                        4,
                    ),
                }
            )

        else:

            raise ValueError(
                f"Unsupported task type: {task_type}"
            )

    return pd.DataFrame(results)


def add_cross_validation(
    training_result: dict,
    evaluation_results: pd.DataFrame,
    cv: int = 5,
) -> pd.DataFrame:
    """
    Add cross-validation scores to the model comparison.

    CV is skipped when the training dataset is too small.
    """

    models = training_result["models"]
    X_train = training_result["X_train"]
    y_train = training_result["y_train"]
    task_type = training_result["task_type"]

    result = evaluation_results.copy()

    # Avoid unreliable CV on very small datasets.
    if len(X_train) < cv * 2:
        result["cv_score"] = None
        return result

    # For classification specifically: stratified CV needs every
    # class to appear at least `cv` times, or sklearn folds end up
    # with a class missing entirely from some fold (noisy warnings,
    # unreliable scores — already caught by the try/except below so
    # it never crashes, but skipping cleanly here is more honest
    # than running it and hoping the warning gets ignored).
    if task_type == "Classification":

        smallest_class_count = y_train.value_counts().min()

        if smallest_class_count < cv:
            result["cv_score"] = None
            return result

    for index, row in result.iterrows():

        model_name = row["model"]
        model = models[model_name]

        try:

            if task_type == "Classification":

                scores = cross_val_score(
                    model,
                    X_train,
                    y_train,
                    cv=cv,
                    scoring="f1_weighted",
                )

            else:

                scores = cross_val_score(
                    model,
                    X_train,
                    y_train,
                    cv=cv,
                    scoring="r2",
                )

            result.loc[
                index,
                "cv_score",
            ] = round(
                scores.mean(),
                4,
            )

        except Exception:

            result.loc[
                index,
                "cv_score",
            ] = None

    return result


def select_best_model(
    evaluation_results: pd.DataFrame,
    task_type: str,
) -> str:
    """
    Select the best-performing model.

    Cross-validation score is preferred when available.
    Otherwise the primary hold-out metric is used.
    """

    if evaluation_results.empty:
        raise ValueError(
            "No model evaluation results found."
        )

    results = evaluation_results.copy()

    # USE CROSS-VALIDATION WHEN AVAILABLE

    if (
        "cv_score" in results.columns
        and results["cv_score"].notna().any()
    ):

        valid_results = results[
            results["cv_score"].notna()
        ]

        best_row = valid_results.loc[
            valid_results["cv_score"].idxmax()
        ]

        return best_row["model"]

    # FALLBACK TO HOLD-OUT METRICS

    if task_type == "Classification":

        best_row = results.loc[
            results["f1_score"].idxmax()
        ]

    elif task_type == "Regression":

        best_row = results.loc[
            results["r2_score"].idxmax()
        ]

    else:

        raise ValueError(
            f"Unsupported task type: {task_type}"
        )

    return best_row["model"]