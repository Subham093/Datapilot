"""Sidebar dataset upload widget."""

import pandas as pd
import streamlit as st


def render_upload_widget():
    """Sidebar dataset upload control. Body is unchanged from the
    original dashboard.py — only wrapped in a function and moved
    into the sidebar."""

    st.markdown("#### 📂 Upload dataset")

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
    )


    if uploaded_file is not None:

        st.write(
            f"**Selected file:** `{uploaded_file.name}`"
        )

        analyze_clicked = st.button(
            "🚀 Upload & Analyze",
            type="primary",
            key="upload_analyze_btn",
        )

        if analyze_clicked:

            try:

                with st.spinner(
                    "Reading and analyzing your dataset..."
                ):

                    df = pd.read_csv(
                        uploaded_file
                    )

                    if df.empty:

                        raise ValueError(
                            "The uploaded CSV is empty."
                        )

                    # Store original dataset.

                    st.session_state[
                        "dataset"
                    ] = df

                    st.session_state[
                        "filename"
                    ] = uploaded_file.name

                    st.session_state[
                        "analysis_done"
                    ] = True

                    # Reset analysis.

                    st.session_state[
                        "cleaned_dataset"
                    ] = None

                    st.session_state[
                        "cleaning_log"
                    ] = []

                    st.session_state[
                        "cleaning_summary"
                    ] = None

                    st.session_state[
                        "training_result"
                    ] = None

                    st.session_state[
                        "evaluation_results"
                    ] = None

                    st.session_state[
                        "best_model_name"
                    ] = None

                    st.session_state[
                        "predictions"
                    ] = None

                    st.session_state[
                        "drift_warnings"
                    ] = []

                    # Reset preview values.

                    default_preview = min(
                        10,
                        len(df),
                    )

                    st.session_state[
                        "original_preview_rows"
                    ] = default_preview

                    st.session_state[
                        "cleaned_preview_rows"
                    ] = default_preview

                    st.session_state[
                        "prediction_preview_rows"
                    ] = default_preview

                st.success(
                    "✅ Dataset uploaded successfully!"
                )

            except Exception as e:

                st.error(
                    f"Could not read the CSV file: {e}"
                )