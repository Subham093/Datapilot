# models/

Intentionally empty. Local scratch space for a saved trained
model (`.pkl`/`.joblib`) if you ever call
`src/exporter.py`'s `save_model_to_disk()` directly — the
app itself currently offers the trained model as a browser
download in the Model Training tab rather than writing it here
automatically.

Model files are gitignored (see `.gitignore`); only the
`.gitkeep` placeholder is tracked, so the folder exists in a
fresh clone even though it starts empty.

**Paste this at:** `models/README.md`