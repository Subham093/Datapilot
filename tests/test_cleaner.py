import pandas as pd

from src.cleaner import clean_dataset_with_log, get_cleaning_summary


def test_cleaning_removes_all_missing_values(messy_df):
    cleaned_df, _ = clean_dataset_with_log(messy_df)
    assert cleaned_df.isna().sum().sum() == 0


def test_cleaning_removes_constant_columns(messy_df):
    cleaned_df, _ = clean_dataset_with_log(messy_df)
    assert "constant" not in cleaned_df.columns


def test_cleaning_produces_audit_log(messy_df):
    _, log = clean_dataset_with_log(messy_df)
    assert len(log) > 0


def test_audit_log_has_consistent_schema(messy_df):
    """Regression test: every audit-log entry must use the
    same five keys. This is the bug that produced a broken
    dashboard table with blank '—' cells (two independent
    cleaning engines used two different schemas)."""

    _, log = clean_dataset_with_log(messy_df)
    expected_keys = {"category", "column", "action", "count", "reason"}

    for entry in log:
        assert set(entry.keys()) == expected_keys


def test_outlier_is_corrected_and_logged():
    df = pd.DataFrame(
        {
            "experience": [1, 2, 3, 4, 5, 6, 7, 4, 3, 20],
            "city": ["Delhi"] * 5 + ["Mumbai"] * 5,
        }
    )

    cleaned_df, log = clean_dataset_with_log(df)

    assert 20 not in cleaned_df["experience"].tolist()
    assert any(entry["category"] == "Outlier Correction" for entry in log)


def test_small_dataset_measurement_column_outlier_still_corrected():
    """
    Regression test for a real bug a user found: on a small
    dataset (11 rows), a genuine measurement column like `age`
    can have every value happen to be unique just by chance
    (100% uniqueness). The identifier-protection heuristic
    used to mistake that for an ID column and skip a real,
    obvious outlier (age=200 among values otherwise ranging
    24-51). Must never happen again.
    """

    df = pd.DataFrame(
        {
            "age": [25, 30, 28, 35, 42, 29, 51, 27, 24, 200, 33],
            "city": ["Delhi", "Mumbai", "Delhi", "Mumbai", "Delhi",
                     "Delhi", "Bangalore", "Delhi", "Delhi", "Mumbai", "Delhi"],
        }
    )

    cleaned_df, log = clean_dataset_with_log(df)

    assert 200 not in cleaned_df["age"].tolist()
    assert any(
        entry["column"] == "age" and entry["category"] == "Outlier Correction"
        for entry in log
    )


def test_real_identifier_column_is_never_modified():
    """A genuine ID column (name suggests it, large sample,
    near-100% unique) must never be touched by outlier
    correction — corrupting a join key silently is far worse
    than leaving one outlier uncorrected."""

    df = pd.DataFrame(
        {
            "customer_id": list(range(1000, 1035)),
            "age": [25, 30, 28, 35, 42, 29, 51, 27, 24, 33, 26, 31, 29, 34,
                    40, 45, 22, 38, 36, 44, 28, 32, 27, 30, 50, 23, 39, 41,
                    37, 25, 55, 120, 29, 33, 26],
        }
    )

    cleaned_df, log = clean_dataset_with_log(df)

    assert cleaned_df["customer_id"].tolist() == df["customer_id"].tolist()
    assert not any(entry["column"] == "customer_id" for entry in log)


def test_cleaning_summary_counts_match(messy_df):
    cleaned_df, log = clean_dataset_with_log(messy_df)
    summary = get_cleaning_summary(messy_df, cleaned_df, log)

    assert summary["total_changes"] == len(log)
    assert summary["columns_removed"] == 1