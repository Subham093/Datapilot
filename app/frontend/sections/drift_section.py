"""Dataset Monitoring tab: original-vs-cleaned comparison and drift detection."""

import pandas as pd
import streamlit as st

from src.monitoring import compare_datasets, detect_data_drift


def render_drift_monitoring(ctx):
    """Dataset comparison (original vs cleaned) and data-drift detection."""

    st.header(
        "📈 Dataset Monitoring & Drift Detection"
    )

    st.write(
        "Compare the current dataset against a "
        "reference dataset to detect schema changes "
        "and numerical data drift."
    )

    reference_file = st.file_uploader(
        "Upload Reference Dataset",
        type=["csv"],
        key="reference_dataset_uploader",
    )

    if reference_file is not None:

        try:

            reference_df = pd.read_csv(
                reference_file
            )

            st.success(
                f"✅ Reference dataset loaded: "
                f"{reference_file.name}"
            )

            compare_clicked = st.button(
                "📈 Compare Datasets",
                type="primary",
                key="compare_datasets_button",
            )

            if compare_clicked:

                with st.spinner(
                    "Comparing datasets and detecting drift..."
                ):

                    comparison = compare_datasets(
                        reference_df,
                        ctx.df,
                    )

                    ctx.drift_warnings = (
                        detect_data_drift(
                            comparison
                        )
                    )

                st.session_state[
                    "drift_warnings"
                ] = ctx.drift_warnings

                # COMPARISON OVERVIEW

                st.subheader(
                    "📊 Dataset Comparison"
                )

                c1, c2, c3, c4 = st.columns(4)

                with c1:

                    st.metric(
                        "Reference Rows",
                        comparison[
                            "reference_rows"
                        ],
                    )

                with c2:

                    st.metric(
                        "Current Rows",
                        comparison[
                            "current_rows"
                        ],
                    )

                with c3:

                    st.metric(
                        "Reference Columns",
                        comparison[
                            "reference_columns"
                        ],
                    )

                with c4:

                    st.metric(
                        "Current Columns",
                        comparison[
                            "current_columns"
                        ],
                    )

                # SCHEMA CHANGES

                st.subheader(
                    "🔍 Schema Changes"
                )

                added_columns = comparison[
                    "added_columns"
                ]

                removed_columns = comparison[
                    "removed_columns"
                ]

                if added_columns:

                    st.warning(
                        "🆕 New columns detected."
                    )

                    st.dataframe(
                        pd.DataFrame(
                            {
                                "Added Column":
                                added_columns
                            }
                        ),
                        width="stretch",
                    )

                else:

                    st.success(
                        "✅ No new columns detected."
                    )

                if removed_columns:

                    st.warning(
                        "❌ Columns removed from "
                        "the reference dataset."
                    )

                    st.dataframe(
                        pd.DataFrame(
                            {
                                "Removed Column":
                                removed_columns
                            }
                        ),
                        width="stretch",
                    )

                else:

                    st.success(
                        "✅ No columns were removed."
                    )

                # NUMERIC DRIFT

                st.subheader(
                    "📉 Numeric Distribution Changes"
                )

                numeric_drift = comparison[
                    "numeric_drift"
                ]

                if numeric_drift:

                    drift_df = pd.DataFrame(
                        numeric_drift
                    )

                    st.dataframe(
                        drift_df,
                        width="stretch",
                    )

                else:

                    st.info(
                        "No common numeric columns "
                        "were available for drift analysis."
                    )

                # DRIFT WARNINGS

                st.subheader(
                    "⚠️ Drift Warnings"
                )

                if ctx.drift_warnings:

                    warnings_df = pd.DataFrame(
                        ctx.drift_warnings
                    )

                    st.warning(
                        f"{len(ctx.drift_warnings)} "
                        "potential drift issue(s) detected."
                    )

                    st.dataframe(
                        warnings_df,
                        width="stretch",
                    )

                else:

                    st.success(
                        "✅ No significant data drift detected "
                        "using the 20% threshold."
                    )

        except Exception as e:

            st.error(
                f"Dataset comparison failed: {e}"
            )