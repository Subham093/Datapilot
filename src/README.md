# src/

This is DataPilot's core engine — every actual data-science
decision (profiling, cleaning, detecting the ML task, checking
for leakage, training, evaluating, explaining, monitoring
drift, generating recommendations, writing reports) lives here
as plain, independently-testable functions.

Nothing in this folder imports Streamlit or knows the UI
exists. `app/frontend/` is just a thin layer that calls into
these functions and displays the result. That split is
deliberate: every function here can be run and unit-tested
with a two-line script, with no browser involved — see
`tests/`.

## What each file is responsible for

| File | Responsibility |
|---|---|
| `config.py` | Every tunable threshold used anywhere in the app (IQR multiplier, identifier-detection ratio, leakage correlation cutoff, drift %, etc.) — one single source of truth instead of the same magic number hardcoded in five places. |
| `validator.py` | First checkpoint after upload — is this even a usable dataset (enough rows, not empty, etc.)? |
| `profiler.py` | Produces the row/column/dtype/summary numbers shown in the Overview tab. |
| `quality.py` | Detects structural data-quality issues (missing values, duplicates, constant columns, inconsistent categories, outliers, invalid numeric-as-text values, heavily-missing columns, possible PII) and turns them into the 0–100 quality score. |
| `cleaner.py` | Actually fixes what `quality.py` found (median/mode imputation, outlier correction, text normalization) and keeps a step-by-step audit log of every change. |
| `task_detector.py` | Guesses the target column and whether the task is Classification or Regression; also checks the target for severe class imbalance. |
| `leakage.py` | Flags feature columns that are suspiciously identical to, or suspiciously correlated with, the target. |
| `preprocessing.py` | Feature-side prep before training: drops high-cardinality/identifier-like columns, builds the encoding pipeline. |
| `model_selector.py` | Picks which scikit-learn models to try for the detected task (Logistic Regression / Decision Tree / Random Forest for classification, with `class_weight="balanced"` so imbalanced targets aren't ignored; Linear Regression / Decision Tree / Random Forest for regression). |
| `model_trainer.py` | Runs the actual train/test split and `.fit()` calls. |
| `evaluator.py` | Computes accuracy/precision/recall/F1 (classification) or R²/MAE/RMSE (regression), cross-validates, and picks the best model. |
| `predictor.py` | Runs the trained model on new/uploaded data to generate predictions. |
| `explainer.py` | Feature importance for the trained model (what drove its predictions). |
| `monitoring.py` | Compares two datasets (reference vs. current) for schema changes and numeric drift — powers the Monitoring tab. |
| `recommendations.py` | Turns everything detected above (quality score, drift, class imbalance) into plain-English, prioritized action items. |
| `report_generator.py` | Assembles all of the above into the single downloadable text report. |
| `exporter.py` | Serialization helpers — turning DataFrames/models/reports into downloadable bytes, or saving to disk. |

**Paste this at:** `src/README.md`