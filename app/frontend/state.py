"""
Session-state defaults and initialization.

Moved verbatim out of the old monolithic dashboard.py — no logic
changed, just given its own home so dashboard.py isn't 2,000 lines.
"""

import streamlit as st


def init_session_state() -> None:
    defaults = {
        "dataset": None,
        "filename": None,
        "analysis_done": False,

        "cleaned_dataset": None,
        "cleaning_log": [],
        "cleaning_summary": None,

        "training_result": None,
        "evaluation_results": None,
        "best_model_name": None,
        "predictions": None,

        "drift_warnings": [],

        "original_preview_rows": 10,
        "cleaned_preview_rows": 10,
        "prediction_preview_rows": 10,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value