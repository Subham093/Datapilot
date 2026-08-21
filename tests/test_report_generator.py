from src.report_generator import generate_full_report


def _minimal_profile():
    return {
        "rows": 10,
        "columns": 4,
        "total_missing_values": 2,
        "duplicate_rows": 1,
    }


def test_backward_compatible_minimal_call():
    """The original call signature (before cleaning_log,
    leakage_warnings, feature_importance existed) must still
    work unchanged — every new parameter defaults to None."""

    report = generate_full_report(
        dataset_name="test.csv",
        profile=_minimal_profile(),
        quality_score=85,
        issues=[],
    )

    assert "DATASET OVERVIEW" in report
    assert "DATA QUALITY" in report
    assert "Quality Score: 85/100" in report
    # sections that depend on unpassed args must not appear
    assert "CLEANING PERFORMED" not in report
    assert "MACHINE LEARNING ANALYSIS" not in report


def test_cleaning_section_included_when_log_provided():
    cleaning_log = [
        {
            "category": "Missing Values",
            "column": "income",
            "action": "Filled with median",
            "count": 2,
            "reason": "Numeric columns are imputed using the median.",
        }
    ]

    report = generate_full_report(
        dataset_name="test.csv",
        profile=_minimal_profile(),
        quality_score=85,
        issues=[],
        cleaning_log=cleaning_log,
    )

    assert "CLEANING PERFORMED" in report
    assert "CLEANING AUDIT" in report
    assert "Total Changes: 1" in report
    assert "income" in report


def test_empty_cleaning_log_reports_no_changes():
    report = generate_full_report(
        dataset_name="test.csv",
        profile=_minimal_profile(),
        quality_score=100,
        issues=[],
        cleaning_log=[],
    )

    assert "CLEANING PERFORMED" in report
    assert "No cleaning changes were needed." in report


def test_leakage_section_only_appears_with_ml_analysis():
    """Leakage check is nested inside the ML section — must
    not appear if ml_analysis wasn't provided, even if
    leakage_warnings was."""

    report = generate_full_report(
        dataset_name="test.csv",
        profile=_minimal_profile(),
        quality_score=85,
        issues=[],
        leakage_warnings=[{"type": "Target Copy", "column": "x",
                            "severity": "High", "description": "copy"}],
    )

    assert "LEAKAGE CHECK" not in report


def test_leakage_section_included_with_ml_analysis():
    report = generate_full_report(
        dataset_name="test.csv",
        profile=_minimal_profile(),
        quality_score=85,
        issues=[],
        ml_analysis={
            "target_column": "purchased",
            "task_type": "Classification",
            "features": 3,
        },
        leakage_warnings=[
            {
                "type": "Target Copy",
                "column": "predicted_outcome",
                "severity": "High",
                "description": "Exact copy of the target.",
            }
        ],
    )

    assert "LEAKAGE CHECK" in report
    assert "predicted_outcome" in report


def test_no_leakage_warnings_reports_clean():
    report = generate_full_report(
        dataset_name="test.csv",
        profile=_minimal_profile(),
        quality_score=85,
        issues=[],
        ml_analysis={
            "target_column": "purchased",
            "task_type": "Classification",
            "features": 3,
        },
        leakage_warnings=[],
    )

    assert "No target leakage warnings detected." in report


def test_feature_importance_section_with_real_dataframe():
    import pandas as pd

    importance_df = pd.DataFrame(
        {"feature": ["age", "income"], "importance": [0.6, 0.4]}
    )

    report = generate_full_report(
        dataset_name="test.csv",
        profile=_minimal_profile(),
        quality_score=85,
        issues=[],
        ml_analysis={
            "target_column": "purchased",
            "task_type": "Classification",
            "features": 2,
        },
        feature_importance=importance_df,
    )

    assert "FEATURE IMPORTANCE" in report
    assert "income" in report


def test_feature_importance_section_handles_empty_dataframe():
    import pandas as pd

    report = generate_full_report(
        dataset_name="test.csv",
        profile=_minimal_profile(),
        quality_score=85,
        issues=[],
        ml_analysis={
            "target_column": "purchased",
            "task_type": "Classification",
            "features": 2,
        },
        feature_importance=pd.DataFrame(),
    )

    assert "FEATURE IMPORTANCE" in report
    assert "not available for this model" in report


def test_cross_validation_note_appears_when_cv_score_column_present():
    import pandas as pd

    evaluation_results = pd.DataFrame(
        {
            "model": ["Random Forest"],
            "f1_score": [0.9],
            "cv_score": [0.87],
        }
    )

    report = generate_full_report(
        dataset_name="test.csv",
        profile=_minimal_profile(),
        quality_score=85,
        issues=[],
        ml_analysis={
            "target_column": "purchased",
            "task_type": "Classification",
            "features": 2,
        },
        evaluation_results=evaluation_results,
    )

    assert "cross-validation" in report.lower()
    assert "cv_score" in report


def test_full_report_with_every_section_populated():
    """End-to-end smoke test with every optional section
    filled in — closest thing to how the dashboard will
    actually call this once wired in."""

    import pandas as pd

    report = generate_full_report(
        dataset_name="messy_data.csv",
        profile=_minimal_profile(),
        quality_score=72,
        issues=[
            {"type": "Missing Values", "column": "income",
             "severity": "Medium", "description": "2 missing values."}
        ],
        cleaning_log=[
            {"category": "Missing Values", "column": "income",
             "action": "Filled with median", "count": 2,
             "reason": "Numeric imputation."}
        ],
        leakage_warnings=[],
        ml_analysis={
            "target_column": "purchased",
            "task_type": "Classification",
            "features": 3,
        },
        best_model="Random Forest",
        evaluation_results=pd.DataFrame(
            {"model": ["Random Forest"], "f1_score": [0.91], "cv_score": [0.88]}
        ),
        feature_importance=pd.DataFrame(
            {"feature": ["age"], "importance": [1.0]}
        ),
        drift_warnings=[],
        recommendations=[
            {"priority": "Low", "area": "Data Quality",
             "recommendation": "Dataset quality is good."}
        ],
    )

    for expected_section in [
        "DATASET OVERVIEW",
        "DATA QUALITY",
        "CLEANING PERFORMED",
        "CLEANING AUDIT",
        "MACHINE LEARNING ANALYSIS",
        "LEAKAGE CHECK",
        "MODEL COMPARISON",
        "FEATURE IMPORTANCE",
        "DATA MONITORING",
        "RECOMMENDATIONS",
    ]:
        assert expected_section in report, f"missing section: {expected_section}"