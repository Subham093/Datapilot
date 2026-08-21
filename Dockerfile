# DataPilot — Streamlit dashboard container
#
# WHY DOCKER IS WORTH IT HERE:
# You said you want to deploy this. Streamlit Cloud doesn't
# need Docker at all (it builds straight from requirements.txt),
# but Docker becomes worth it the moment you want to deploy to
# Render, Railway, an EC2/VM, or anywhere that isn't Streamlit
# Cloud's own free tier — and it also means "works on my machine"
# stops being a possible interview question, since the exact
# same image runs in your VS Code terminal, CI, and production.

FROM python:3.12-slim

# System dependencies (kept minimal on purpose — pandas/sklearn
# wheels are prebuilt, so we don't need a full build toolchain)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first so Docker can cache this
# layer — code changes won't force a full dependency reinstall.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

EXPOSE 8501

# Streamlit's own health endpoint — lets platforms like Render
# know the container is actually ready, not just "started".
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app/frontend/dashboard.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true"]
