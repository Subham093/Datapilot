from src.profiler import profile_dataset


def test_profile_reports_correct_shape(clean_valid_df):
    profile = profile_dataset(clean_valid_df)

    assert profile["rows"] == 4
    assert profile["columns"] == 3
    assert profile["duplicate_rows"] == 0


def test_profile_includes_per_column_info(clean_valid_df):
    profile = profile_dataset(clean_valid_df)
    column_names = [c["column"] for c in profile["columns_info"]]

    assert set(column_names) == {"age", "salary", "city"}
