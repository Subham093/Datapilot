import pandas as pd


def generate_predictions(
    model,
    df: pd.DataFrame,
    target_column: str,
) -> pd.DataFrame:
    """
    Generate predictions for the supplied dataset.

    The target column is excluded from the input
    features if it exists.
    """

    if target_column in df.columns:

        X = df.drop(
            columns=[target_column]
        )

    else:

        X = df.copy()

    predictions = model.predict(X)

    result = df.copy()

    result["prediction"] = predictions

    return result