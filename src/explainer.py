import pandas as pd


def get_feature_importance(
    model,
) -> pd.DataFrame:
    """
    Extract feature importance from the trained
    pipeline when supported.

    Supports:
        Random Forest
        Decision Tree
        Linear models
    """

    if not hasattr(model, "named_steps"):

        return pd.DataFrame()

    if "model" not in model.named_steps:

        return pd.DataFrame()

    trained_model = model.named_steps[
        "model"
    ]

    preprocessor = model.named_steps.get(
        "preprocessor"
    )

    if preprocessor is None:

        return pd.DataFrame()

    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

    # Tree-based models
    if hasattr(
        trained_model,
        "feature_importances_",
    ):

        importance = (
            trained_model
            .feature_importances_
        )

    # Linear models
    elif hasattr(
        trained_model,
        "coef_",
    ):

        coefficients = (
            trained_model.coef_
        )

        if coefficients.ndim > 1:

            importance = abs(
                coefficients
            ).mean(axis=0)

        else:

            importance = abs(
                coefficients
            )

    else:

        return pd.DataFrame()

    result = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": importance,
        }
    )

    result = result.sort_values(
        "importance",
        ascending=False,
    )

    result = result.reset_index(
        drop=True
    )

    return result