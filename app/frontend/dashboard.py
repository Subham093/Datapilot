import os
import sys
from types import SimpleNamespace

# Make the project root importable regardless of *how* this
# file gets run.
#
# `streamlit run app/frontend/dashboard.py` only adds this
# file's own folder (app/frontend/) to sys.path — NOT the
# project root — so `from src.profiler import ...` fails
# with "ModuleNotFoundError: No module named 'src'" even
# though `pytest` (which handles this automatically) works
# fine. This inserts the real project root (two levels up
# from this file) at the front of sys.path before any src
# import runs.

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import pandas as pd
import streamlit as st

from src.profiler import profile_dataset
from src.quality import detect_quality_issues, calculate_quality_score
from src.validator import validate_dataset

from app.frontend.state import init_session_state
from app.frontend.theme import inject_theme, render_app_header
from app.frontend.sections.upload_section import render_upload_widget
from app.frontend.sections.overview_section import render_overview
from app.frontend.sections.quality_section import render_quality_and_cleaning
from app.frontend.sections.task_detection_section import render_task_detection_and_leakage
from app.frontend.sections.drift_section import render_drift_monitoring
from app.frontend.sections.recommendations_section import render_recommendations
from app.frontend.sections.training_section import render_training_evaluation_prediction
from app.frontend.sections.report_section import render_report_export


# PAGE CONFIG

st.set_page_config(
    page_title="DataPilot",
    page_icon="🧭",
    layout="wide",
)

inject_theme()
init_session_state()


# SIDEBAR — global controls & navigation

with st.sidebar:
    render_app_header()
    st.markdown(
        "<div style='font-size:0.85rem; opacity:0.85; margin: 0.4rem 0 1rem 0;'>"
        "Upload a CSV and DataPilot profiles, validates, cleans, "
        "detects ML tasks, checks leakage, monitors drift, trains "
        "models, explains predictions, and builds reports."
        "</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    render_upload_widget()

    if st.session_state["analysis_done"] and st.session_state["dataset"] is not None:
        st.divider()
        _df = st.session_state["dataset"]
        st.caption("CURRENT DATASET")
        st.markdown(f"**{st.session_state.get('filename') or 'dataset.csv'}**")
        st.markdown(
            f"<span style='font-family: JetBrains Mono, monospace; font-size:0.85rem;'>"
            f"{_df.shape[0]:,} rows &nbsp;·&nbsp; {_df.shape[1]:,} cols"
            f"</span>",
            unsafe_allow_html=True,
        )


# MAIN AREA

if not st.session_state["analysis_done"]:

    st.markdown("## Welcome to DataPilot")
    st.write(
        "Upload a CSV file from the sidebar to get started. "
        "DataPilot will profile your data, flag quality issues, "
        "detect the right ML task, train and compare models, and "
        "generate a full report — all in one place."
    )

else:

    ctx = SimpleNamespace()

    ctx.df = st.session_state["dataset"]

    # DEFAULT VALUES FOR THE FINAL REPORT
    
    # Cleaning, leakage detection, training, and drift
    # analysis each only run if their section's button was
    # clicked / their try-block succeeded — so these variables
    # are NOT guaranteed to exist by the time the report is
    # built at the bottom of this script. Initializing them
    # here means the report can safely check "was this step
    # run?" instead of crashing with NameError when a section
    # was skipped.

    ctx.cleaned_df = None
    ctx.cleaning_log = None
    ctx.leakage_warnings = None
    ctx.ml_analysis = None
    ctx.best_model_name = None
    ctx.evaluation_results = None
    ctx.feature_importance = None
    ctx.drift_warnings = None
    ctx.recommendations = None

    # VALIDATION

    ctx.validation = validate_dataset(ctx.df)

    if not ctx.validation["valid"]:

        st.error(
            "❌ Dataset validation failed."
        )

        if ctx.validation.get("errors"):

            st.write(
                "### Validation Errors"
            )

            st.dataframe(
                pd.DataFrame(
                    {
                        "error":
                        ctx.validation["errors"]
                    }
                ),
                width="stretch",
            )

    else:

        # VALIDATION WARNINGS

        if ctx.validation.get("warnings"):

            st.warning(
                "⚠️ Dataset validation warnings detected."
            )

            st.dataframe(
                pd.DataFrame(
                    {
                        "warning":
                        ctx.validation["warnings"]
                    }
                ),
                width="stretch",
            )

        # PROFILE

        ctx.profile = profile_dataset(ctx.df)

        ctx.issues = detect_quality_issues(ctx.df)

        ctx.quality_score = calculate_quality_score(
            ctx.df,
            ctx.issues,
        )

        # SECTION TABS
        
        # Every tab's code still runs on every rerun, in the
        # same order as the original single-page script —
        # st.tabs() only changes which section is *visible*,
        # not what executes. That keeps cross-section state
        # (e.g. the target column picked in the Task
        # Detection tab) working exactly as before, just
        # without a 2,000-line scroll to get to it.

        (
            tab_overview,
            tab_quality,
            tab_task,
            tab_drift,
            tab_recs,
            tab_training,
            tab_report,
        ) = st.tabs(
            [
                "📊 Overview",
                "🩺 Data Quality",
                "🤖 Task Detection",
                "📈 Monitoring",
                "💡 Recommendations",
                "🚀 Model Training",
                "📄 Report",
            ]
        )

        with tab_overview:
            render_overview(ctx)

        with tab_quality:
            render_quality_and_cleaning(ctx)

        with tab_task:
            render_task_detection_and_leakage(ctx)

        with tab_drift:
            render_drift_monitoring(ctx)

        with tab_recs:
            render_recommendations(ctx)

        with tab_training:
            render_training_evaluation_prediction(ctx)

        with tab_report:
            render_report_export(ctx)
