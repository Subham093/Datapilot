# app/frontend/

The Streamlit UI. This is presentation only — every actual
data-science decision happens in `src/`; this folder just
calls those functions and renders the result.

## Why this is split into several files instead of one script

This used to be a single ~1,900-line `dashboard.py`. It's now
broken up by responsibility so no one file does everything:

| File | Responsibility |
|---|---|
| `dashboard.py` | Entry point. Page config, theme injection, session-state init, sidebar, and the `st.tabs()` that wire each section in. Run this with `streamlit run app/frontend/dashboard.py`. |
| `state.py` | Session-state defaults (uploaded dataset, cleaning results, training results, etc.) so they're declared in one place instead of scattered across every section. |
| `theme.py` | The app's visual styling (colors, fonts, sidebar look, button styling) — all CSS injection, no logic. |
| `helpers.py` | Small display-formatting helpers shared by more than one section (e.g. safely rendering a value that might be missing). |
| `sections/` | One file per tab — see `sections/README.md`. |

## Why `st.tabs()` instead of separate pages

Every section's code still runs on every rerun, in the same
order it always did — `st.tabs()` only changes which section
is *visible*, not what executes. That was a deliberate choice:
it keeps cross-section state (e.g. the target column picked in
Task Detection, which Model Training depends on) working
exactly as it did in the original single-page script, just
without a 2,000-line scroll to get to it.

**Paste this at:** `app/frontend/README.md`