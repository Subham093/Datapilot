# tests/

Unit and integration tests for `src/` and end-to-end tests for
the dashboard itself. Run with `pytest` from the project root.

Most `src/` modules have a matching `tests/test_x.py`, but
coverage isn't strictly one-to-one — some modules are exercised
indirectly through other tests instead of getting their own
dedicated file.

## Worth knowing about

- `conftest.py` — shared pytest fixtures (e.g. a small "messy"
  DataFrame with duplicates/missing values/case-inconsistent
  text, reused across several cleaning-related tests instead of
  redefined in each file).
- `test_dashboard_entrypoint.py` — runs `dashboard.py` as a
  raw subprocess (`python app/frontend/dashboard.py`, bypassing
  pytest's own import-path handling) and checks stderr for
  `ModuleNotFoundError`. This is a regression test for a real
  bug: `streamlit run` only adds the dashboard file's own
  folder to `sys.path`, not the project root, so `from src...`
  imports could fail when run for real even though pytest
  (which sets up paths differently) never caught it.
- `test_section_rename_regression.py` — a regression test
  proving the app still boots correctly after the
  `app/frontend/sections/*.py` files were renamed to
  `*_section.py` (to avoid colliding with same-named files in
  `src/`).

**Paste this at:** `tests/README.md`