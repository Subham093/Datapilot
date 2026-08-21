"""
Small display/formatting helpers shared across dashboard sections.

Moved verbatim out of the old monolithic dashboard.py — bodies are
untouched, only the file location changed.
"""

import numpy as np
import pandas as pd
import streamlit as st


# HELPER: SAFE DISPLAY VALUE

def _display_value(value) -> str:
    """
    Convert audit-log values into clean display text.

    This function ONLY affects the dashboard display.
    It does not modify the dataset or audit log.
    """

    if value is None:
        return "—"

    try:
        missing = pd.isna(value)

        if isinstance(missing, (bool, np.bool_)):
            if missing:
                return "—"

    except Exception:
        pass

    if isinstance(value, str):

        cleaned_value = value.strip()

        if cleaned_value == "":
            return "—"

        return cleaned_value

    try:

        text = str(value)

        if text.strip().lower() in {
            "none",
            "nan",
            "<na>",
            "nat",
        }:
            return "—"

        return text

    except Exception:

        return "—"


# HELPER: CLEAN AUDIT DATAFRAME

def _prepare_audit_dataframe(cleaning_log) -> pd.DataFrame:
    """
    Convert the cleaning audit log into a display-ready
    DataFrame.

    src.cleaner is the ONLY cleaning engine in this project,
    so every log entry always has exactly these five keys —
    no more mixed schemas / blank dash columns.
    """

    if not cleaning_log:
        return pd.DataFrame()

    audit_df = pd.DataFrame(cleaning_log)

    if audit_df.empty:
        return audit_df

    required_columns = ["category", "column", "action", "count", "reason"]

    for column_name in required_columns:

        if column_name not in audit_df.columns:
            audit_df[column_name] = pd.NA

    audit_df = audit_df[required_columns].copy()

    audit_df = audit_df.rename(
        columns={
            "category": "Category",
            "column": "Column",
            "action": "Action",
            "count": "Count",
            "reason": "Reason",
        }
    )

    for column_name in audit_df.columns:

        audit_df[column_name] = (
            audit_df[column_name]
            .apply(_display_value)
        )

    return audit_df


# HELPER: DATASET PREVIEW

def show_dataset_preview(
    dataframe: pd.DataFrame,
    title: str,
    input_key: str,
) -> None:

    st.subheader(title)

    total_rows = len(dataframe)

    if total_rows == 0:

        st.info(
            "The dataset contains no rows."
        )

        return

    default_rows = min(
        10,
        total_rows,
    )

    # IMPORTANT STREAMLIT FIX
    #
    # Do NOT pass both:
    #
    # value=...
    # key=...
    #
    # while also modifying st.session_state[key].
    #
    # The widget itself owns its value.

    if input_key not in st.session_state:

        st.session_state[input_key] = default_rows

    current_value = st.session_state[
        input_key
    ]

    try:

        current_value = int(
            current_value
        )

    except Exception:

        current_value = default_rows

    current_value = max(
        1,
        min(
            current_value,
            1_000_000_000,
        ),
    )

    # Make sure an old value larger than the current
    # dataset does not create an invalid widget state.

    if current_value > total_rows:

        current_value = total_rows

        st.session_state[
            input_key
        ] = current_value

    preview_rows = st.number_input(
        "Number of rows to display",
        min_value=1,
        max_value=max(
            1,
            total_rows,
        ),
        step=1,
        key=input_key,
    )

    if preview_rows > total_rows:

        st.warning(
            f"⚠️ You requested {preview_rows:,} rows, "
            f"but the dataset contains only "
            f"{total_rows:,} rows."
        )

        return

    st.caption(
        f"Showing {preview_rows:,} of "
        f"{total_rows:,} total rows. "
        "This only controls the preview."
    )

    st.dataframe(
        dataframe.head(
            int(preview_rows)
        ),
        width="stretch",
    )