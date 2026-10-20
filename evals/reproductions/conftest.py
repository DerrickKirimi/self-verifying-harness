"""Start the archived app inside the sandbox; exercise its public HTTP API."""

import subprocess
import time
from urllib.error import URLError
from urllib.request import urlopen

import pytest


@pytest.fixture(scope="session")
def app_url():
    process = subprocess.Popen(["python", "-I", "/app/evals/app/app.py"])
    try:
        for _ in range(100):
            if process.poll() is not None:
                raise RuntimeError("app exited before becoming ready")
            try:
                with urlopen("http://127.0.0.1:8080/api/issues", timeout=1):
                    break
            except URLError:
                time.sleep(0.05)
        else:
            raise RuntimeError("app did not become ready")
        yield "http://127.0.0.1:8080"
    finally:
        process.terminate()
        process.wait(timeout=5)
