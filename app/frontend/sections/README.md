# app/frontend/sections/

One file per tab in the app. Each file exposes a single
`render_*(ctx)` function that `dashboard.py` calls inside its
matching `st.tabs()` entry. `ctx` is a plain shared object
carrying whatever an earlier tab computed that a later tab
needs (e.g. the cleaned dataset, the detected target column) —
it's not a database or session store, just a container passed
through the one script run.

Files are named `*_section.py` (not just `quality.py`,
`recommendations.py`, etc.) specifically to avoid colliding
with the same-named core-logic files in `src/` — easy to
otherwise open the wrong one by mistake in an editor.

| File | Tab | What it shows |
|---|---|---|
| `upload_section.py` | *(sidebar, not a tab)* | The CSV upload widget and the "Upload & Analyze" button. |
| `overview_section.py` | Overview | Row/column counts, duplicates, missing values, dataset preview. |
| `quality_section.py` | Data Quality | Detected quality issues, the quality score, the "Clean Dataset Automatically" button, and the cleaning audit log. |
| `task_detection_section.py` | Task Detection | Target column picker, detected task type (Classification/Regression), class-imbalance warning, and the leakage check. |
| `drift_section.py` | Monitoring | Upload a second (reference) dataset to compare against — schema changes and numeric drift. |
| `recommendations_section.py` | Recommendations | Plain-English, prioritized list combining quality, drift, and imbalance findings. |
| `training_section.py` | Model Training | Train/compare models, view evaluation metrics, explainability, and generate predictions. |
| `report_section.py` | Report | Builds and downloads the full text report. |

**Paste this at:** `app/frontend/sections/README.md`