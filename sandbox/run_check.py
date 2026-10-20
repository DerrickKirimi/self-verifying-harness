"""Trusted launcher, baked into the runner image rather than the app checkout."""

import json
from pathlib import Path
import subprocess
import sys


result = subprocess.run(
    [sys.executable, "-I", "-m", "pytest", "-q", "-p", "no:cacheprovider",
     "--junitxml=/tmp/result.xml", "/checks/" + sys.argv[1]],
    capture_output=True, text=True, timeout=45,
)
report = Path("/tmp/result.xml")
print(json.dumps({
    "exit_code": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
    "junit": report.read_text() if report.exists() else None,
}))
