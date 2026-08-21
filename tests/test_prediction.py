from src.task_detector import analyze_ml_task
from src.model_trainer import train_models
from src.evaluator import evaluate_models, select_best_model
from src.predictor import generate_predictions
from src.explainer import get_feature_importance


def test_predictions_have_expected_columns(classification_df):
    analysis = analyze_ml_task(classification_df)
    training_result = train_models(
        classification_df, analysis["target_column"], analysis["task_type"]
    )
    evaluation_results = evaluate_models(training_result)
    best_model_name = select_best_model(evaluation_results, analysis["task_type"])
    best_model = training_result["models"][best_model_name]

    predictions = generate_predictions(
        best_model, classification_df, analysis["target_column"]
    )

    assert "prediction" in predictions.columns
    assert len(predictions) == len(classification_df)


def test_feature_importance_available_for_tree_models(classification_df):
    analysis = analyze_ml_task(classification_df)
    training_result = train_models(
        classification_df, analysis["target_column"], analysis["task_type"]
    )
    best_model = training_result["models"]["Random Forest"]

    importance_df = get_feature_importance(best_model)

    assert not importance_df.empty
    assert {"feature", "importance"}.issubset(importance_df.columns)
