import pandas as pd


def profile_dataset(df: pd.DataFrame) -> dict:
    """
    Generate a basic profile of the uploaded dataset.
    """

    profile = {}

    # Overall dataset information
    profile["rows"] = df.shape[0]
    profile["columns"] = df.shape[1]
    profile["duplicate_rows"] = int(df.duplicated().sum())
    profile["total_missing_values"] = int(df.isna().sum().sum())

    # Column-level information
    column_profiles = []

    for column in df.columns:

        missing_count = int(df[column].isna().sum())

        missing_percentage = (
            missing_count / len(df) * 100
            if len(df) > 0
            else 0
        )

        unique_count = int(df[column].nunique(dropna=True))

        column_info = {
            "column": column,
            "dtype": str(df[column].dtype),
            "missing_count": missing_count,
            "missing_percentage": round(missing_percentage, 2),
            "unique_values": unique_count,
            "is_constant": unique_count <= 1,
        }

        column_profiles.append(column_info)

    profile["columns_info"] = column_profiles

    return profile