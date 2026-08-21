"""Overview tab: dataset shape, columns, duplicates, preview."""

import pandas as pd
import streamlit as st

from app.frontend.helpers import show_dataset_preview


def render_overview(ctx):
    """Dataset overview: shape, columns, duplicates, memory usage."""

    st.header(
        "📊 Dataset Overview"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Rows",
            ctx.profile["rows"],
        )

    with c2:

        st.metric(
            "Columns",
            ctx.profile["columns"],
        )

    with c3:

        st.metric(
            "Duplicate Rows",
            ctx.profile["duplicate_rows"],
        )

    with c4:

        st.metric(
            "Missing Values",
            ctx.profile[
                "total_missing_values"
            ],
        )

    # ORIGINAL PREVIEW

    show_dataset_preview(
        dataframe=ctx.df,
        title="Dataset Preview",
        input_key="original_preview_rows",
    )

    # COLUMN PROFILE

    with st.expander(
        "🔎 View Column Profile"
    ):

        column_profile_df = pd.DataFrame(
            ctx.profile["columns_info"]
        )

        st.dataframe(
            column_profile_df,
            width="stretch",
        )