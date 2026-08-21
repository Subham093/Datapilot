import subprocess
import sys
from pathlib import Path


def test_dashboard_runnable_via_streamlit_entrypoint():
    """
    Regression test for: `streamlit run app/frontend/dashboard.py`
    failing with `ModuleNotFoundError: No module named 'src'`.

    Unlike pytest (which adds the project root to sys.path
    automatically via pytest.ini), Streamlit only adds the
    dashboard file's own folder to sys.path. This test runs
    the dashboard file directly as a subprocess (bypassing
    pytest's own path handling) and checks that none of the
    `from src...` imports fail — that's exactly the failure
    mode a user hit when running the real app.
    """

    project_root = Path(__file__).resolve().parents[1]
    dashboard_path = project_root / "app" / "frontend" / "dashboard.py"

    result = subprocess.run(
        [sys.executable, str(dashboard_path)],
        capture_output=True,
        text=True,
        cwd=str(project_root),
        timeout=30,
    )

    assert "ModuleNotFoundError" not in result.stderr
    assert "No module named 'src'" not in result.stderr
