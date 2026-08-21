"""Model Training tab: training, evaluation, explainability, predictions."""

import streamlit as st

from src.preprocessing import detect_high_cardinality_columns
from src.model_trainer import train_models
from src.evaluator import add_cross_validation, evaluate_models, select_best_model
from src.predictor import generate_predictions
from src.explainer import get_feature_importance
from src.exporter import model_to_bytes

from app.frontend.helpers import show_dataset_preview


def render_training_evaluation_prediction(ctx):
    """Model training, evaluation, explainability, and predictions."""

    if (
        ctx.target_column is not None
        and ctx.task_type is not None
    ):

        st.header(
            "🚀 Automatic Machine Learning"
        )

        st.write(
            "DataPilot trains multiple suitable "
            "models, compares their performance, "
            "and selects the best model automatically."
        )

        # SHOW WHAT'S EXCLUDED BEFORE TRAINING
        
        # Previously, high-cardinality columns (a name
        # column, a leaked ID) were dropped silently
        # inside the preprocessor with zero visibility —
        # the user had no way to know why a column they
        # uploaded never affected the model.

        try:

            excluded_columns = (
                detect_high_cardinality_columns(
                    ctx.ml_df,
                    ctx.target_column,
                )
            )

        except Exception:

            excluded_columns = []

        if excluded_columns:

            st.info(
                "**Excluded from ML training:** "
                f"{', '.join(excluded_columns)}\n\n"
                "Reason: high-cardinality categorical "
                "column(s) (mostly unique values, e.g. "
                "a name or ID column). Encoding these "
                "would create one feature per unique "
                "value and degrade every model."
            )

        train_clicked = st.button(
            "🚀 Train & Compare Models",
            type="primary",
        )

        if train_clicked:

            try:

                with st.spinner(
                    "Training and evaluating models..."
                ):

                    ctx.training_result = (
                        train_models(
                            ctx.ml_df,
                            ctx.target_column,
                            ctx.task_type,
                        )
                    )

                    ctx.evaluation_results = (
                        evaluate_models(
                            ctx.training_result
                        )
                    )

                    # Cross-validation
                    #
                    # add_cross_validation existed and was
                    # tested, but the dashboard never
                    # actually called it — best-model
                    # selection ran on hold-out metrics
                    # alone. CV gives a steadier estimate
                    # (less sensitive to which rows landed
                    # in the test split), so it's used here
                    # whenever the dataset is large enough
                    # (add_cross_validation skips it safely
                    # otherwise and returns cv_score=None).

                    ctx.evaluation_results = (
                        add_cross_validation(
                            ctx.training_result,
                            ctx.evaluation_results,
                        )
                    )

                    ctx.best_model_name = (
                        select_best_model(
                            ctx.evaluation_results,
                            ctx.task_type,
                        )
                    )

                    st.session_state[
                        "training_result"
                    ] = ctx.training_result

                    st.session_state[
                        "evaluation_results"
                    ] = ctx.evaluation_results

                    st.session_state[
                        "best_model_name"
                    ] = ctx.best_model_name

                    st.session_state[
                        "predictions"
                    ] = None

                st.success(
                    "✅ Models trained and evaluated successfully!"
                )

            except Exception as e:

                st.error(
                    f"Model training failed: {e}"
                )

        # MODEL RESULTS

        ctx.evaluation_results = (
            st.session_state[
                "evaluation_results"
            ]
        )

        ctx.best_model_name = (
            st.session_state[
                "best_model_name"
            ]
        )

        ctx.training_result = (
            st.session_state[
                "training_result"
            ]
        )

        if (
            ctx.evaluation_results is not None
            and ctx.best_model_name is not None
            and ctx.training_result is not None
        ):

            st.subheader(
                "📊 Model Comparison"
            )

            st.dataframe(
                ctx.evaluation_results,
                width="stretch",
            )

            # BEST MODEL

            st.subheader(
                "🏆 Best Model"
            )

            st.success(
                f"Best model: **{ctx.best_model_name}**"
            )

            best_model = ctx.training_result[
                "models"
            ][ctx.best_model_name]

            # DOWNLOAD TRAINED MODEL
            
            # Before this, a trained model lived only in
            # Streamlit's session state — refresh the page
            # and it's gone, with no way to reuse it outside
            # the app. This lets you actually keep the model.

            st.download_button(
                label="⬇️ Download Trained Model (.joblib)",
                data=model_to_bytes(best_model),
                file_name=f"datapilot_{ctx.best_model_name.lower().replace(' ', '_')}.joblib",
                mime="application/octet-stream",
                help=(
                    "Load this later with: "
                    "joblib.load('model.joblib'). Requires "
                    "the same scikit-learn version to load "
                    "reliably."
                ),
            )

            # MODEL EXPLANATION

            st.subheader(
                "💡 Model Explainability"
            )

            try:

                ctx.feature_importance = (
                    get_feature_importance(
                        best_model
                    )
                )

                if not ctx.feature_importance.empty:

                    st.dataframe(
                        ctx.feature_importance.head(10),
                        width="stretch",
                    )

                    st.bar_chart(
                        ctx.feature_importance
                        .head(10)
                        .set_index("feature")[
                            "importance"
                        ]
                    )

                else:

                    st.info(
                        "Feature importance is not available "
                        "for this model."
                    )

            except Exception as e:

                st.info(
                    "Feature importance could not be "
                    f"displayed: {e}"
                )

            # PREDICTIONS

            st.subheader(
                "Predictions"
            )

            predict_clicked = st.button(
                "Generate Predictions",
                type="primary",
            )

            if predict_clicked:

                try:

                    with st.spinner(
                        "Generating predictions..."
                    ):

                        ctx.predictions = (
                            generate_predictions(
                                best_model,
                                ctx.ml_df,
                                ctx.target_column,
                            )
                        )

                        st.session_state[
                            "predictions"
                        ] = ctx.predictions

                        st.session_state[
                            "prediction_preview_rows"
                        ] = min(
                            10,
                            len(ctx.predictions),
                        )

                    st.success(
                        "✅ Predictions generated successfully!"
                    )

                except Exception as e:

                    st.error(
                        f"Prediction failed: {e}"
                    )

            ctx.predictions = (
                st.session_state[
                    "predictions"
                ]
            )

            if ctx.predictions is not None:

                # PREDICTION PREVIEW

                show_dataset_preview(
                    dataframe=ctx.predictions,
                    title="Prediction Preview",
                    input_key="prediction_preview_rows",
                )

                # DOWNLOAD PREDICTIONS

                st.caption(
                    "The download contains all generated "
                    "predictions, not only the previewed rows."
                )

                prediction_csv = (
                    ctx.predictions
                    .to_csv(index=False)
                    .encode("utf-8")
                )

                st.download_button(
                    label="⬇️ Download Predictions CSV",
                    data=prediction_csv,
                    file_name="datapilot_predictions.csv",
                    mime="text/csv",
                )


    else:

        st.info(
            "ℹ️ Model training is skipped until a target "
            "column is confirmed in the Task Detection tab."
        )