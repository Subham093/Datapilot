from src.recommendations import (
    generate_recommendations,
    recommendations_to_dataframe,
)


def test_low_quality_score_triggers_high_priority():
    recommendations = generate_recommendations(
        quality_score=40,
        issues=[],
        drift_warnings=None,
    )
    assert recommendations[0]["priority"] == "High"


def test_drift_warnings_add_recommendation():
    issues = [
        {"type": "Missing Values", "column": "income", "severity": "Medium",
         "description": "Missing values detected."}
    ]
    drift_warnings = [
        {"type": "Numeric Drift", "column": "income", "severity": "Medium",
         "description": "Mean changed significantly."}
    ]

    recommendations = generate_recommendations(55, issues, drift_warnings)
    areas = [r["area"] for r in recommendations]

    assert "Data Drift" in areas


def test_recommendations_to_dataframe_not_empty():
    recommendations = generate_recommendations(55, [], [])
    df = recommendations_to_dataframe(recommendations)
    assert not df.empty
