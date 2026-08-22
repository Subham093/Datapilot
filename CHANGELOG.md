## [1.3.1]

### Fixed
- `src/cleaner.py`: the missing-value fill step called
  `.median()` on a numeric column unconditionally, then checked
  `pd.isna()` on the result to detect an all-missing column.
  On some pandas/NumPy version combinations, calling `.median()`
  on an all-NaN column can emit a spurious
  `RuntimeWarning: Mean of empty slice`, even though the
  returned value (`NaN`) is correct. Now checks
  `column.notna().sum() == 0` *before* calling `.median()` at
  all, skipping the call entirely for all-missing columns
  instead of calling it and inspecting the result afterward.
  Behavior and audit-log output are unchanged — verified against
  `data/edge_cases/02_all_missing_column.csv` and the full
  56-test suite (56/56 still passing).

## [1.3.0]

### Changed
- `app/frontend/dashboard.py` was a single ~1,900-line script.
  Split into `dashboard.py` (thin entry point), `state.py`,
  `theme.py`, `helpers.py`, and one file per tab under
  `app/frontend/sections/`. No logic changed — every cross-
  section variable was renamed via AST analysis (not
  find/replace) to guarantee zero behavioral drift, and
  verified against the full test suite plus real end-to-end
  runs before/after.
- `app/frontend/sections/*.py` files renamed to `*_section.py`
  (`quality.py` → `quality_section.py`, etc.) to stop them
  colliding with same-named files in `src/`.
- Full visual redesign: white background, navy/amber theme,
  sidebar upload, `st.tabs()` navigation instead of one long
  scrolling page.

### Fixed
- `src/cleaner.py`: a numeric column that was 100% missing had
  no valid median to compute, so `fillna(NaN)` was a silent
  no-op — yet the audit log still claimed "Filled with median."
  Now skips the false log entry when the median is undefined,
  letting the (accurate) constant-column removal step explain
  what actually happened.
- `src/quality.py`: the Data Quality issue count didn't include
  non-numeric text hiding inside numeric columns (e.g. "72k" in
  an age column), even though `src/cleaner.py` already silently
  detected and fixed them — causing the quality table and the
  cleaning audit log to disagree on issue counts. `quality.py`
  now reuses `cleaner.py`'s exact detection function (not a
  reimplementation) so the two can't drift apart again.
- Deleted `src/reporting.py` (confirmed unused — the dashboard
  has called `generate_full_report()` from
  `src/report_generator.py` directly since [1.0.0]; only a
  stale docstring comment still mentioned the old module,
  which is also now corrected).
- Deleted `src/data_summary.py` and its test (confirmed unused
  by the actual application — only referenced by its own test
  file).
- Deleted `data/raw/cleaned_dataset.csv`, a stray generated
  artifact that didn't belong in `raw/` and contained an
  uncleaned outlier value (`age = 200`).

### Added
- `src/task_detector.py`: `check_class_imbalance()` — flags
  when a classification target's minority class falls under
  10% of rows, with a separate, more urgent flag when a class
  has fewer than 2 examples (too few to reliably split into
  train/test). Surfaced in the Task Detection tab, factored
  into Recommendations, and included in the downloadable
  report.
- `src/model_selector.py`: `class_weight="balanced"` added to
  all three classifiers, so an imbalanced target actually gets
  mitigated during training, not just flagged. Verified on a
  realistic imbalanced dataset: minority-class recall went from
  0.00 to 0.33 with this change, same data, same model.
- `src/quality.py`: two new generic, pattern-based checks —
  "Heavily Missing Column" (50%+ empty, recommends dropping
  instead of imputing) and "Possible Personal Information"
  (email/phone-shaped values in any text column, regardless of
  column name).
- `data/edge_cases/` — a 16-file robustness test pack (missing
  columns, extreme imbalance, leakage, infinite values, mixed
  dates, malformed column names, etc.) used to stress-test the
  fixes above.
- `tests/test_section_rename_regression.py` — boots the real
  dashboard via Streamlit's `AppTest` framework to confirm the
  section-file rename didn't break anything end-to-end.

### Corrected from [1.2.0]
- The "Known, deliberately not fixed yet" note about two
  competing reporting code paths (`generate_full_report()` vs
  `reporting.create_dataset_report()`) no longer applies —
  `src/reporting.py` has been deleted (see Fixed, above).