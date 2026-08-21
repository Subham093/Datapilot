# experiments/

Intentionally empty. Reserved scratch space for ad-hoc
notebooks or scripts (e.g. trying a new model, testing a new
threshold from `src/config.py`) that aren't part of the actual
app — nothing in `src/` or `app/` currently reads from or
writes to this folder.

Unlike `data/processed/` and `models/`, this folder isn't
tied to a specific file type, so there's no wildcard rule for
it in `.gitignore` — only the `.gitkeep` placeholder is
tracked. If you start putting real work here, add whatever
`.gitignore` rule fits it (e.g. `*.ipynb_checkpoints/`).

**Paste this at:** `experiments/README.md`