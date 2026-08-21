from src.monitoring import compare_datasets, detect_data_drift


def test_compare_datasets_detects_new_column(reference_df, current_df):
    comparison = compare_datasets(reference_df, current_df)
    assert "new_feature" in comparison["added_columns"]


def test_compare_datasets_detects_mean_drift(reference_df, current_df):
    comparison = compare_datasets(reference_df, current_df)
    income_drift = next(
        d for d in comparison["numeric_drift"] if d["column"] == "income"
    )
    assert income_drift["change_percentage"] > 0


def test_drift_warnings_generated(reference_df, current_df):
    comparison = compare_datasets(reference_df, current_df)
    warnings = detect_data_drift(comparison)
    assert len(warnings) > 0
