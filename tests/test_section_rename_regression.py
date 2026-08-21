"""
Regression test for the app/frontend/sections/*.py rename
(quality.py -> quality_section.py, recommendations.py ->
recommendations_section.py, etc.) that resolved a real
filename collision with src/quality.py and src/recommendations.py.

Uses Streamlit's own AppTest framework to actually BOOT the
real dashboard.py, not just check that imports resolve
statically — proves the renamed section modules are wired up
correctly end-to-end.
"""

from pathlib import Path

from streamlit.testing.v1 import AppTest


DASHBOARD_PATH = str(
    Path(__file__).resolve().parents[1] / "app" / "frontend" / "dashboard.py"
)


def test_dashboard_boots_with_renamed_sections():
    at = AppTest.from_file(DASHBOARD_PATH)
    at.run(timeout=30)

    assert not at.exception
