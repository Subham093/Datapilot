"""
exporter.py

Handles writing DataPilot outputs to disk: the cleaned
dataset, the full text report, generated predictions, and
trained models — each as bytes ready for a Streamlit
download_button, so the dashboard doesn't need to know about
encoding/formatting or serialization.

This file previously existed but was empty (0 bytes) and
unused anywhere in the project — a placeholder that never
got built out. This is the real implementation.
"""

import io
import json

import joblib
import pandas as pd


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialize a DataFrame to UTF-8 CSV bytes."""

    return df.to_csv(index=False).encode("utf-8")


def dataframe_to_json_bytes(df: pd.DataFrame) -> bytes:
    """Serialize a DataFrame to UTF-8 JSON bytes (records orientation)."""

    return df.to_json(orient="records", indent=2).encode("utf-8")


def report_to_json_bytes(report: dict) -> bytes:
    """Serialize a report dict (from generate_full_report(),
    or the recommendations/leakage/drift lists) to pretty JSON bytes."""

    return json.dumps(report, indent=2, default=str).encode("utf-8")


def model_to_bytes(model) -> bytes:
    """
    Serialize a fitted sklearn Pipeline (preprocessor + model)
    to bytes using joblib, suitable for a Streamlit download
    button or writing straight to models/ on disk.

    NOTE: joblib pickles are Python-version and
    scikit-learn-version sensitive. Whoever loads this file
    back later needs a compatible environment — this is a
    real constraint, not a rare edge case, so it's called out
    explicitly rather than left as a silent gotcha.
    """

    buffer = io.BytesIO()
    joblib.dump(model, buffer)
    return buffer.getvalue()


def model_from_bytes(model_bytes: bytes):
    """Deserialize a model previously produced by model_to_bytes."""

    buffer = io.BytesIO(model_bytes)
    return joblib.load(buffer)


def save_model_to_disk(model, path: str) -> None:
    """Persist a fitted model to a local .joblib file (e.g. models/best_model.joblib)."""

    joblib.dump(model, path)


def load_model_from_disk(path: str):
    """Load a previously persisted model back into memory."""

    return joblib.load(path)


def export_full_bundle(
    cleaned_df: pd.DataFrame | None,
    cleaning_log: list | None,
    report_text: str,
    predictions_df: pd.DataFrame | None = None,
    trained_model=None,
) -> dict[str, bytes]:
    """
    Build every downloadable artifact DataPilot can offer in
    one call, keyed by suggested filename. The dashboard can
    loop over this dict and add one st.download_button per
    entry instead of hand-building each one.
    """

    bundle: dict[str, bytes] = {
        "datapilot_report.txt": report_text.encode("utf-8"),
    }

    if cleaned_df is not None:
        bundle["datapilot_cleaned_dataset.csv"] = dataframe_to_csv_bytes(cleaned_df)

    if cleaning_log:
        bundle["datapilot_cleaning_log.json"] = report_to_json_bytes(cleaning_log)

    if predictions_df is not None:
        bundle["datapilot_predictions.csv"] = dataframe_to_csv_bytes(predictions_df)

    if trained_model is not None:
        bundle["datapilot_best_model.joblib"] = model_to_bytes(trained_model)

    return bundle