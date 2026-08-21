from sklearn.linear_model import (
    LogisticRegression,
    LinearRegression,
)
from sklearn.tree import (
    DecisionTreeClassifier,
    DecisionTreeRegressor,
)
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
)


def get_models(
    task_type: str,
) -> dict:
    """
    Return candidate ML models based on
    classification or regression.
    """

    if task_type == "Classification":

        return {
            "Logistic Regression":
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                ),

            "Decision Tree":
                DecisionTreeClassifier(
                    random_state=42,
                    class_weight="balanced",
                ),

            "Random Forest":
                RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    class_weight="balanced",
                ),
        }

    if task_type == "Regression":

        return {
            "Linear Regression":
                LinearRegression(),

            "Decision Tree":
                DecisionTreeRegressor(
                    random_state=42
                ),

            "Random Forest":
                RandomForestRegressor(
                    n_estimators=100,
                    random_state=42
                ),
        }

    raise ValueError(
        f"Unsupported task type: {task_type}"
    )