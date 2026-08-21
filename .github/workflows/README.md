# .github/workflows/

Continuous integration — `ci.yml` runs automatically on every
push/PR to `main` via GitHub Actions.

It does two things, in order:
1. **`test` job** — installs `requirements.txt` and runs the
   full `pytest` suite on both Python 3.11 and 3.12, then
   confirms `app/frontend/dashboard.py` at least compiles.
2. **`docker-build` job** — (only runs if `test` passes)
   confirms the `Dockerfile` at the project root actually
   builds successfully.

If this is red on GitHub, something in the codebase is broken
— don't merge until it's green.

**Paste this at:** `.github/workflows/README.md`