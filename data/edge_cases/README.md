# data/edge_cases/

A 16-file robustness test pack — deliberately broken or
unusual CSVs used to stress-test the app (missing columns,
extreme class imbalance, target leakage, infinite values,
mixed date formats, weird column names, and more).

**This is QA material, not demo material.** Don't upload these
when showing the project to someone — use `data/raw/` for
that. This folder is here to show *how* the app was tested:
each file targets one specific failure mode, and the app is
expected to handle every one of them gracefully (no crashes,
clear warnings, safe fallbacks) rather than silently producing
a wrong result.

See `README_TESTS.txt` in this same folder for the full
file-by-file breakdown of what each one targets and what
"correct" behavior looks like for it.

**Paste this at:** `data/edge_cases/README.md`