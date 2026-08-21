from src.task_detector import analyze_ml_task, detect_target_column, detect_task_type


def test_detects_purchased_as_target(classification_df):
    target = detect_target_column(classification_df)
    assert target == "purchased"


def test_classification_task_detected(classification_df):
    task_type = detect_task_type(classification_df, "purchased")
    assert task_type == "Classification"


def test_full_analysis_returns_expected_keys(classification_df):
    result = analyze_ml_task(classification_df)

    assert result["target_column"] == "purchased"
    assert result["task_type"] == "Classification"
    assert result["rows"] == 20
    assert result["features"] == 4


def test_manual_target_override_is_respected(classification_df):
    """
    The dashboard has a target-column selectbox that lets the
    user override auto-detection. This confirms the underlying
    mechanism it relies on actually works: passing an explicit
    target_column must bypass detection entirely, even if it's
    a column the heuristic would never have picked on its own
    (here, "city" — not remotely target-shaped).
    """

    result = analyze_ml_task(classification_df, target_column="city")

    assert result["target_column"] == "city"
    assert result["task_type"] == "Classification"