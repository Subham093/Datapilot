from src.task_detector import analyze_ml_task
from src.model_trainer import train_models
from src.evaluator import evaluate_models, add_cross_validation, select_best_model


def test_cross_validation_adds_scores(classification_df):
    analysis = analyze_ml_task(classification_df)
    training_result = train_models(
        classification_df, analysis["target_column"], analysis["task_type"]
    )

    evaluation_results = evaluate_models(training_result)
    evaluation_with_cv = add_cross_validation(training_result, evaluation_results)

    assert "cv_score" in evaluation_with_cv.columns


def test_best_model_prefers_cv_score_when_available(classification_df):
    analysis = analyze_ml_task(classification_df)
    training_result = train_models(
        classification_df, analysis["target_column"], analysis["task_type"]
    )

    evaluation_results = evaluate_models(training_result)
    evaluation_with_cv = add_cross_validation(training_result, evaluation_results)
    best_model = select_best_model(evaluation_with_cv, analysis["task_type"])

    assert best_model in training_result["models"]
