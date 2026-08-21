import pandas as pd

from src.validator import validate_dataset


def test_valid_dataset_passes(clean_valid_df):
    result = validate_dataset(clean_valid_df)
    assert result["valid"] is True
    assert result["errors"] == []


def test_empty_dataset_fails():
    result = validate_dataset(pd.DataFrame())
    assert result["valid"] is False
    assert result["errors"]


def test_duplicate_columns_flagged():
    df = pd.DataFrame([[1, 2]], columns=["a", "a"])
    result = validate_dataset(df)
    assert result["valid"] is False


def test_high_missing_percentage_warns():
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [None, None, None, 1]})
    result = validate_dataset(df)
    assert result["valid"] is True
    assert result["warnings"]
