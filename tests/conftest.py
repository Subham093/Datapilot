import pandas as pd
import pytest


@pytest.fixture
def messy_df() -> pd.DataFrame:
    """Small dataset with duplicates, missing values, case
    variants, and a constant column — exercises every branch
    of the cleaning engine."""

    return pd.DataFrame(
        {
            "age": [20, 21, 22, 22],
            "income": [30000, None, 40000, 40000],
            "city": ["Delhi", "delhi", "Mumbai", "mumbai"],
            "constant": [1, 1, 1, 1],
        }
    )


@pytest.fixture
def classification_df() -> pd.DataFrame:
    """20-row synthetic dataset for task detection, training,
    evaluation, prediction, and explainability tests. Large
    enough for a stratified train/test split and 5-fold CV."""

    return pd.DataFrame(
        {
            "age": [
                22, 25, 28, 31, 35, 38, 42, 45, 48, 52,
                55, 29, 33, 40, 44, 50, 27, 36, 41, 47,
            ],
            "income": [
                30000, 35000, 40000, 45000, 50000, 55000, 60000, 65000,
                70000, 75000, 80000, 42000, 47000, 58000, 62000, 73000,
                39000, 52000, 61000, 68000,
            ],
            "city": [
                "Delhi", "Mumbai", "Delhi", "Pune", "Mumbai", "Delhi",
                "Pune", "Mumbai", "Delhi", "Pune", "Mumbai", "Delhi",
                "Pune", "Mumbai", "Delhi", "Pune", "Mumbai", "Delhi",
                "Pune", "Mumbai",
            ],
            "experience": [
                1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                11, 3, 4, 6, 7, 9, 2, 5, 7, 8,
            ],
            "purchased": [
                "No", "No", "No", "No", "Yes", "Yes", "Yes", "Yes",
                "Yes", "Yes", "Yes", "No", "No", "Yes", "Yes", "Yes",
                "No", "Yes", "Yes", "Yes",
            ],
        }
    )


@pytest.fixture
def leakage_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [22, 31, 45, 28, 39],
            "salary": [30000, 45000, 70000, 38000, 62000],
            "target_copy": [1, 0, 1, 0, 1],
            "purchased": [1, 0, 1, 0, 1],
        }
    )


@pytest.fixture
def reference_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [20, 25, 30, 35, 40],
            "income": [30000, 35000, 40000, 45000, 50000],
        }
    )


@pytest.fixture
def current_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [25, 30, 35, 40, 45],
            "income": [60000, 65000, 70000, 75000, 80000],
            "new_feature": [1, 2, 3, 4, 5],
        }
    )


@pytest.fixture
def clean_valid_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [22, 31, 45, 28],
            "salary": [30000, 45000, 70000, 38000],
            "city": ["Delhi", "Mumbai", "Delhi", "Pune"],
        }
    )
