import pandas as pd

from src.preprocessing import build_preprocessor, split_features_target


def test_high_cardinality_column_is_dropped():
    """A near-unique free-text column (e.g. customer names)
    must not survive into the feature set — encoding it would
    create one feature per row."""

    df = pd.DataFrame(
        {
            "customer_name": [f"person_{i}" for i in range(50)],
            "age": list(range(20, 70)),
            "purchased": ["Yes", "No"] * 25,
        }
    )

    preprocessor = build_preprocessor(df, "purchased")
    used_columns = [
        columns
        for name, _, columns in preprocessor.transformers
        if name == "categorical"
    ]

    assert used_columns == [] or "customer_name" not in used_columns[0]


def test_normal_categorical_column_survives(classification_df):
    """A genuinely useful low-cardinality column (city, with
    only 3 distinct values) must NOT be dropped."""

    preprocessor = build_preprocessor(classification_df, "purchased")

    categorical_columns = [
        columns
        for name, _, columns in preprocessor.transformers
        if name == "categorical"
    ][0]

    assert "city" in categorical_columns


def test_preprocessor_fits_without_crashing_on_high_cardinality():
    """End-to-end: the whole point of the guard is that this
    doesn't blow up memory or raise. Before the fix, this kind
    of column would silently create 50 one-hot columns from 50
    rows."""

    df = pd.DataFrame(
        {
            "customer_name": [f"person_{i}" for i in range(50)],
            "age": list(range(20, 70)),
            "purchased": ["Yes", "No"] * 25,
        }
    )

    preprocessor = build_preprocessor(df, "purchased")
    X, y = split_features_target(df, "purchased")

    transformed = preprocessor.fit_transform(X)

    # Only "age" should have made it through -> 1 feature column,
    # not 50+.
    assert transformed.shape[1] < 5


def test_detect_high_cardinality_columns_matches_actual_drop():
    """
    detect_high_cardinality_columns() is a separate function
    from build_preprocessor() (kept non-breaking on purpose,
    see docstring), used only to tell the dashboard UI what's
    about to be excluded. This test guards against those two
    pieces of logic silently drifting apart.
    """

    df = pd.DataFrame(
        {
            "customer_name": [f"person_{i}" for i in range(50)],
            "city": ["Delhi", "Mumbai"] * 25,
            "age": list(range(20, 70)),
            "purchased": ["Yes", "No"] * 25,
        }
    )

    from src.preprocessing import detect_high_cardinality_columns

    reported_dropped = detect_high_cardinality_columns(df, "purchased")

    preprocessor = build_preprocessor(df, "purchased")
    actually_used_categorical = [
        columns
        for name, _, columns in preprocessor.transformers
        if name == "categorical"
    ]
    actually_used_categorical = (
        actually_used_categorical[0] if actually_used_categorical else []
    )

    assert reported_dropped == ["customer_name"]
    assert "customer_name" not in actually_used_categorical
    assert "city" in actually_used_categorical