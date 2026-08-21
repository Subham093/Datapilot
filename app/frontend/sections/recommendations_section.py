"""Recommendations tab: AI-generated recommendations."""

import streamlit as st

from src.recommendations import generate_recommendations, recommendations_to_dataframe


def render_recommendations(ctx):
    """AI-generated recommendations based on quality/task/leakage findings."""

    st.header(
        "💡 DataPilot Recommendations"
    )

    ctx.drift_warnings = st.session_state[
        "drift_warnings"
    ]

    ctx.recommendations = (
        generate_recommendations(
            quality_score=ctx.quality_score,
            issues=ctx.issues,
            drift_warnings=ctx.drift_warnings,
            class_balance=(
                ctx.ml_analysis.get("class_balance")
                if ctx.ml_analysis
                else None
            ),
        )
    )

    recommendations_df = (
        recommendations_to_dataframe(
            ctx.recommendations
        )
    )

    if not recommendations_df.empty:

        priority_order = {
            "High": 0,
            "Medium": 1,
            "Low": 2,
        }

        recommendations_df[
            "_priority_order"
        ] = recommendations_df[
            "priority"
        ].map(
            priority_order
        )

        recommendations_df = (
            recommendations_df
            .sort_values(
                "_priority_order"
            )
            .drop(
                columns="_priority_order"
            )
        )

        st.dataframe(
            recommendations_df,
            width="stretch",
            hide_index=True,
        )

        st.caption(
            "Recommendations are generated from "
            "detected data-quality issues and "
            "dataset-drift results."
        )

    else:

        st.success(
            "✅ No recommendations at this time."
        )