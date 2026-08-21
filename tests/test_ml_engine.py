from src.task_detector import analyze_ml_task
from src.model_trainer import train_models
from src.evaluator import evaluate_models, select_best_model


def test_full_training_pipeline_runs(classification_df):
    analysis = analyze_ml_task(classification_df)

    training_result = train_models(
        df=classification_df,
        target_column=analysis["target_column"],
        task_type=analysis["task_type"],
    )

    assert set(training_result["models"].keys()) == {
        "Logistic Regression",
        "Decision Tree",
        "Random Forest",
    }


def test_evaluation_and_best_model_selection(classification_df):
    analysis = analyze_ml_task(classification_df)
    training_result = train_models(
        classification_df, analysis["target_column"], analysis["task_type"]
    )

    evaluation_results = evaluate_models(training_result)
    best_model = select_best_model(evaluation_results, analysis["task_type"])

    assert not evaluation_results.empty
    assert best_model in training_result["models"]
