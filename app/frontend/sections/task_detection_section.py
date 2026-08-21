"""ML Task Detection tab: target/task detection and leakage check."""

import pandas as pd
import streamlit as st

from src.task_detector import (
    analyze_ml_task,
    detect_target_column,
    resolve_target_selectbox_options,
    NO_CONFIDENT_TARGET_LABEL,
)
from src.leakage import detect_target_leakage


def render_task_detection_and_leakage(ctx):
    """ML task/target detection and target-leakage check."""

    st.header(
        "🤖 ML Task Detection"
    )

    # TARGET COLUMN — DETECT, THEN LET THE USER CONFIRM
    
    # Previously this section only ever called
    # analyze_ml_task(ctx.ml_df) with no override, and just
    # displayed whatever it auto-detected. On a dataset
    # with no obvious target, the heuristic could still
    # pick a column and silently start training on it
    # without the user ever confirming that's correct.
    # Auto-detection now only supplies the DEFAULT
    # selection; the user has the final say.

    try:

        auto_detected_target = detect_target_column(
            ctx.ml_df
        )

    except Exception:

        auto_detected_target = None

    # Was a column removed during cleaning for having zero
    # variation? If the user's intended target only ever had
    # one class, cleaning correctly drops it as a useless
    # constant column — but with no explanation, it just
    # looks like the target silently vanished from the
    # dropdown below. Connect that dot explicitly.

    if ctx.cleaning_log:

        constant_columns_removed = [
            entry["column"]
            for entry in ctx.cleaning_log
            if entry.get("category") == "Constant Column"
        ]

        if constant_columns_removed:

            removed_list = ", ".join(
                f"'{c}'" for c in constant_columns_removed
            )

            st.warning(
                "⚠️ "
                f"{removed_list} "
                + (
                    "was"
                    if len(constant_columns_removed) == 1
                    else "were"
                )
                + " removed during cleaning because "
                + (
                    "it had"
                    if len(constant_columns_removed) == 1
                    else "they had"
                )
                + " only one unique value across every row. "
                "If this was meant to be your prediction "
                "target, classification isn't possible on "
                "this data as uploaded — every row has the "
                "same label, so there's nothing for a model "
                "to learn to distinguish."
            )

    available_columns = ctx.ml_df.columns.tolist()

    (
        target_selectbox_options,
        target_default_index,
    ) = resolve_target_selectbox_options(
        auto_detected_target,
        available_columns,
    )

    if auto_detected_target is None:

        st.warning(
            "DataPilot could not confidently detect a "
            "target column automatically. Select one "
            "from the dropdown below before continuing "
            "— nothing is pre-selected for you."
        )

    selected_target_column = st.selectbox(
        "🎯 Target column "
        "(auto-detected — change if this is wrong)",
        options=target_selectbox_options,
        index=target_default_index,
        help=(
            "DataPilot guesses the most likely target "
            "column from column names and statistics. "
            "This guess is not always right — confirm it "
            "before training, or pick a different column."
        ),
    )

    target_not_yet_chosen = (
        selected_target_column == NO_CONFIDENT_TARGET_LABEL
    )

    if target_not_yet_chosen:

        ctx.target_column = None
        ctx.task_type = None
        ctx.ml_analysis = None

    else:

        try:

            ctx.ml_analysis = analyze_ml_task(
                ctx.ml_df,
                target_column=selected_target_column,
            )

            ctx.target_column = ctx.ml_analysis.get(
                "target_column"
            )

            ctx.task_type = ctx.ml_analysis.get(
                "task_type"
            )

            features = ctx.ml_analysis.get(
                "features",
                0,
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "🎯 Active Target",
                    (
                        str(ctx.target_column)
                        if ctx.target_column
                        else "Not detected"
                    ),
                )

            with col2:

                st.metric(
                    "🤖 ML Task",
                    (
                        str(ctx.task_type)
                        if ctx.task_type
                        else "Not detected"
                    ),
                )

            with col3:

                st.metric(
                    "📊 Features",
                    features,
                )

            class_balance = ctx.ml_analysis.get(
                "class_balance"
            )

            if class_balance and class_balance.get("is_imbalanced"):

                minority_class = class_balance.get(
                    "minority_class"
                )
                minority_ratio = class_balance.get(
                    "minority_ratio",
                    0,
                )
                class_counts = class_balance.get(
                    "class_counts",
                    {},
                )

                counts_text = ", ".join(
                    f"{label}: {count}"
                    for label, count in class_counts.items()
                )

                if class_balance.get("too_few_to_split"):

                    st.error(
                        "⚠️ Severe class imbalance — class "
                        f"'{minority_class}' has only "
                        f"{class_balance.get('minority_count')} "
                        "example(s), too few to reliably "
                        f"split into train/test sets. "
                        f"({counts_text})"
                    )

                else:

                    st.warning(
                        "⚠️ Class imbalance detected — class "
                        f"'{minority_class}' makes up only "
                        f"{minority_ratio:.1%} of rows. "
                        "Accuracy alone can be misleading "
                        f"here. ({counts_text})"
                    )

        except Exception as e:

            st.warning(
                "ML task detection could not "
                f"be completed: {e}"
            )

            ctx.target_column = None
            ctx.task_type = None
            ctx.ml_analysis = None

    # DATA LEAKAGE

    if ctx.target_column is not None:

        st.subheader(
            "🛡️ Data Leakage Check"
        )

        try:

            ctx.leakage_warnings = (
                detect_target_leakage(
                    ctx.ml_df,
                    ctx.target_column,
                )
            )

            if ctx.leakage_warnings:

                st.warning(
                    f"⚠️ {len(ctx.leakage_warnings)} "
                    "potential leakage issue(s) detected."
                )

                leakage_df = pd.DataFrame(
                    ctx.leakage_warnings
                )

                st.dataframe(
                    leakage_df,
                    width="stretch",
                )

            else:

                st.success(
                    "✅ No obvious target leakage detected."
                )

        except Exception as e:

            st.warning(
                "Leakage check could not be completed: "
                f"{e}"
            )

    else:

        st.info(
            "ℹ️ No target column was detected. "
            "Supervised ML training will be skipped until "
            "a target is available."
        )