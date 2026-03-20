"""Playwright E2E test fixtures for StudioFace Flet app."""

import os
import subprocess
import time

import pytest


@pytest.fixture(scope="session")
def app_server():
    """Start the Flet app server for E2E tests."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main_py = os.path.join(project_root, "app", "main.py")
    env = {
        **os.environ,
        "FLET_FORCE_WEB_SERVER": "true",
        "FLET_SERVER_PORT": "8551",
        "PYTHONPATH": project_root,
    }
    proc = subprocess.Popen(
        ["python", main_py],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(8)  # Wait for server to start
    yield "http://localhost:8551"
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
