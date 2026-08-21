# -*- coding: utf-8 -*-
"""Report tab: full dataset report generation and download."""

import streamlit as st

from src.report_generator import generate_full_report


def render_report_export(ctx):
    """Full dataset report generation and download."""

    # DATASET REPORT

    # Previously this rebuilt a thin ad-hoc text report
    # using create_dataset_report() — quality info only.
    # generate_full_report() already existed with support
    # for cleaning, leakage, ML, feature importance, drift,
    # and recommendations, but was never called anywhere.
    # Now wired in, using whatever sections actually ran
    # this session (cleaning/leakage/training are all
    # optional — each defaults to None if that section
    # wasn't used, and generate_full_report skips any
    # section it wasn't given).

    st.divider()

    st.header(
        "📄 Dataset Report"
    )

    report_dataset_name = st.session_state.get(
        "filename", "uploaded_dataset.csv"
    )

    report_text = generate_full_report(
        dataset_name=report_dataset_name,
        profile=ctx.profile,
        quality_score=ctx.quality_score,
        issues=ctx.issues,
        cleaning_log=ctx.cleaning_log,
        leakage_warnings=ctx.leakage_warnings,
        ml_analysis=ctx.ml_analysis,
        best_model=ctx.best_model_name,
        evaluation_results=ctx.evaluation_results,
        feature_importance=ctx.feature_importance,
        drift_warnings=ctx.drift_warnings,
        recommendations=ctx.recommendations,
    )

    st.download_button(
        label="⬇️ Download Dataset Report",
        data=report_text,
        file_name="datapilot_report.txt",
        mime="text/plain",
    )