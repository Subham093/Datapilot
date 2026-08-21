"""Data Quality tab: quality issues, AI-generated cleaning, cleaned preview/download."""

import pandas as pd
import streamlit as st

from src.cleaner import clean_dataset_with_log, get_cleaning_summary
from src.exporter import dataframe_to_csv_bytes, report_to_json_bytes

from app.frontend.helpers import show_dataset_preview, _prepare_audit_dataframe


def render_quality_and_cleaning(ctx):
    """Data quality issues, AI-generated cleaning, and cleaned-dataset preview/download."""

    st.header(
        "🩺 Data Quality"
    )

    quality_col1, quality_col2 = st.columns(2)

    with quality_col1:

        st.metric(
            "Quality Score",
            f"{ctx.quality_score}/100",
        )

    with quality_col2:

        st.metric(
            "Issues Detected",
            len(ctx.issues),
        )

    if ctx.quality_score >= 80:

        st.success(
            "🟢 Dataset quality is good."
        )

    elif ctx.quality_score >= 60:

        st.warning(
            "🟡 Dataset needs some cleaning."
        )

    else:

        st.error(
            "🔴 Dataset has significant quality issues."
        )

    # QUALITY ISSUES

    if ctx.issues:

        st.subheader(
            "⚠️ Data Quality Issues"
        )

        issues_df = pd.DataFrame(
            ctx.issues
        )

        st.dataframe(
            issues_df,
            width="stretch",
        )

        st.info(
            "DataPilot will automatically attempt to "
            "correct detected data-quality problems. "
            "Numeric outliers are corrected rather than "
            "deleted when the statistical evidence is "
            "strong enough. Ambiguous categorical values "
            "are not guessed."
        )

        # CLEAN DATASET

        clean_clicked = st.button(
            "🧹 Clean Dataset Automatically",
            type="primary",
        )

        if clean_clicked:

            try:

                with st.spinner(
                    "Detecting and automatically "
                    "correcting anomalies..."
                ):

                    # Single cleaning engine (src.cleaner):
                    # duplicates -> missing values ->
                    # categorical normalization -> numeric
                    # anomaly/outlier correction -> constant
                    # column removal. See src/cleaner.py.

                    (
                        ctx.cleaned_df,
                        ctx.cleaning_log,
                    ) = clean_dataset_with_log(
                        ctx.df.copy()
                    )

                    # Cleaning summary

                    ctx.cleaning_summary = (
                        get_cleaning_summary(
                            ctx.df,
                            ctx.cleaned_df,
                            ctx.cleaning_log,
                        )
                    )

                    # Store cleaned dataset

                    st.session_state[
                        "cleaned_dataset"
                    ] = ctx.cleaned_df

                    st.session_state[
                        "cleaning_log"
                    ] = ctx.cleaning_log

                    st.session_state[
                        "cleaning_summary"
                    ] = ctx.cleaning_summary

                    # Reset ML results

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

                    # Reset preview

                    st.session_state[
                        "cleaned_preview_rows"
                    ] = min(
                        10,
                        len(ctx.cleaned_df),
                    )

                st.success(
                    "✅ Dataset automatically cleaned "
                    "and corrected!"
                )

            except Exception as e:

                st.error(
                    f"Cleaning failed: {e}"
                )

    else:

        st.success(
            "✅ No major data quality issues detected."
        )

    # CLEANED DATASET

    ctx.cleaned_df = st.session_state[
        "cleaned_dataset"
    ]

    if ctx.cleaned_df is not None:

        st.divider()

        st.header(
            "AI-Generated Cleaned Dataset"
        )

        st.caption(
            "DataPilot has applied safe, automatically "
            "detected corrections. Review the audit log "
            "before using the dataset for downstream work."
        )

        # CLEANED PREVIEW

        show_dataset_preview(
            dataframe=ctx.cleaned_df,
            title="Corrected Dataset Preview",
            input_key="cleaned_preview_rows",
        )

        # CLEANING SUMMARY

        summary = st.session_state[
            "cleaning_summary"
        ]

        if summary:

            st.subheader(
                "Cleaning Summary"
            )

            c1, c2, c3, c4 = st.columns(4)

            with c1:

                st.metric(
                    "Rows Removed",
                    summary.get(
                        "rows_removed",
                        0,
                    ),
                )

            with c2:

                st.metric(
                    "Columns Removed",
                    summary.get(
                        "columns_removed",
                        0,
                    ),
                )

            with c3:

                st.metric(
                    "Missing Values Handled",
                    summary.get(
                        "missing_values_handled",
                        0,
                    ),
                )

            with c4:

                st.metric(
                    "Total Changes",
                    summary.get(
                        "total_changes",
                        0,
                    ),
                )

        # AUDIT LOG

        ctx.cleaning_log = st.session_state[
            "cleaning_log"
        ]

        if ctx.cleaning_log:

            with st.expander(
                "🔍 View Cleaning Audit Log",
                expanded=True,
            ):

                audit_df = (
                    _prepare_audit_dataframe(
                        ctx.cleaning_log
                    )
                )

                if not audit_df.empty:

                    st.dataframe(
                        audit_df,
                        width="stretch",
                        height=500,
                        hide_index=True,
                    )

                    st.caption(
                        "Each entry shows the category of "
                        "change, the affected column, the "
                        "action taken, how many values/rows "
                        "were affected, and why."
                    )

                else:

                    st.info(
                        "No cleaning changes were recorded."
                    )

            # DOWNLOAD CLEANED DATA + AUDIT LOG

            download_col1, download_col2 = st.columns(2)

            with download_col1:

                st.download_button(
                    label="⬇️ Download Cleaned Dataset CSV",
                    data=dataframe_to_csv_bytes(ctx.cleaned_df),
                    file_name="datapilot_cleaned_dataset.csv",
                    mime="text/csv",
                )

            with download_col2:

                if ctx.cleaning_log:

                    st.download_button(
                        label="⬇️ Download Audit Log JSON",
                        data=report_to_json_bytes(ctx.cleaning_log),
                        file_name="datapilot_cleaning_log.json",
                        mime="application/json",
                    )

        else:

            st.info(
                "No cleaning changes were recorded."
            )

    # ML DATASET

    ctx.ml_df = ctx.df

    if ctx.cleaned_df is not None:

        ctx.ml_df = ctx.cleaned_df

        st.info(
            "ℹ️ Model training will use the cleaned dataset."
        )