# data/raw/

Curated, demo-ready sample datasets. These are the files to
actually upload when showing the app to someone — each one is
sized and written to cleanly demonstrate one feature working
well, not to break anything on purpose (that's what
`data/edge_cases/` is for).

| File | What it demonstrates |
|---|---|
| `test_1_clean_baseline.csv` | The happy path — clean data, 100/100 quality score, straight through to a trained classifier. Good opening demo. |
| `test_2_regression_house_prices.csv` | Proves the app isn't classification-only — auto-detects a Regression task and shows regression-appropriate metrics. |
| `test_3_high_cardinality_trap.csv` | Contains a name + email column — demonstrates PII detection and automatic exclusion of identifier-like columns before training. |
| `test_4_leakage_trap.csv` | Contains columns that are near-duplicates of the target — demonstrates the leakage detector catching it in the Task Detection tab. |
| `test_5a_drift_reference.csv` + `test_5b_drift_current.csv` | A matched pair, meant to be used together in the Monitoring tab (upload 5a as the main dataset, then 5b as the reference file) — the only files in the project that can demonstrate drift detection, since that needs two datasets to compare. |
| `datapilot_messy_test.csv`, `test_dataset.csv` | Smaller general-purpose files used during earlier manual testing — fine to keep, not essential for a demo. |

**Paste this at:** `data/raw/README.md`