# .streamlit/

`config.toml` sets the app's base theme colors (navy text,
white background, amber accent) that Streamlit applies to its
native widgets automatically. This covers the base palette
only — the more detailed styling (sidebar look, tab strip,
metric cards, button states) is CSS injected in
`app/frontend/theme.py`, not here.

Streamlit reads this file automatically on startup; nothing
needs to import or reference it manually.

**Paste this at:** `.streamlit/README.md`