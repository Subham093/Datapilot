from src.exporter import model_to_bytes, model_from_bytes
from src.task_detector import analyze_ml_task
from src.model_trainer import train_models


def test_model_survives_serialization_roundtrip(classification_df):
    """A trained pipeline must produce identical predictions
    after being serialized to bytes and loaded back — this is
    the whole point of the 'Download Trained Model' button."""

    analysis = analyze_ml_task(classification_df)
    training_result = train_models(
        classification_df, analysis["target_column"], analysis["task_type"]
    )
    model = training_result["models"]["Random Forest"]

    X = classification_df.drop(columns=[analysis["target_column"]])
    original_predictions = model.predict(X)

    model_bytes = model_to_bytes(model)
    reloaded_model = model_from_bytes(model_bytes)
    reloaded_predictions = reloaded_model.predict(X)

    assert list(original_predictions) == list(reloaded_predictions)
